"""
Enhanced Code Execution Tool with RFC HTTP fallback
Priority Order: RFC HTTP → Daytona Cloud → RFC SSH → Local (last resort)
"""

import asyncio
from dataclasses import dataclass
import shlex
import time
from python.helpers.tool import Tool, Response
from python.helpers import files, rfc_exchange
from python.helpers.print_style import PrintStyle
from python.helpers.shell_local import LocalInteractiveSession
from python.helpers.shell_ssh import SSHInteractiveSession
from python.helpers.docker import DockerContainerManager
from python.helpers.strings import truncate_text as truncate_text_string
from python.helpers.messages import truncate_text as truncate_text_agent
import re
import aiohttp
import json


@dataclass
class State:
    shells: dict[int, LocalInteractiveSession | SSHInteractiveSession]
    docker: DockerContainerManager | None


class EnhancedCodeExecution(Tool):
    """
    Enhanced Code Execution Tool with RFC HTTP as primary execution method
    Priority Order: RFC HTTP → Daytona Cloud → RFC SSH → Local (last resort)
    """

    async def execute(self, **kwargs):
        await self.agent.handle_intervention()

        runtime_type = self.args.get("runtime", "").lower().strip()
        session = int(self.args.get("session", 0))

        # For reset and output operations, use original logic
        if runtime_type in ["output", "reset"]:
            await self.prepare_state()
            if runtime_type == "output":
                response = await self.get_terminal_output(
                    session=session, first_output_timeout=60, between_output_timeout=5
                )
            elif runtime_type == "reset":
                response = await self.reset_terminal(session=session)
        else:
            # For actual code execution, try RFC HTTP first
            response = await self.execute_with_fallback(
                code=self.args["code"], runtime=runtime_type, session=session
            )

        if not response:
            response = self.agent.read_prompt(
                "fw.code.info.md", info=self.agent.read_prompt("fw.code.no_output.md")
            )
        return Response(message=response, break_loop=False)

    async def execute_with_fallback(self, code: str, runtime: str, session: int) -> str:
        """Execute code with fallback priority: RFC HTTP → Daytona → RFC SSH → Local"""
        
        # Priority 1: Try RFC HTTP first (most reliable)
        try:
            PrintStyle(font_color="#00FF00", bold=True).print(
                f"Attempting execution via RFC HTTP (PRIMARY)..."
            )
            result = await self.execute_via_rfc_http(code, runtime, session)
            if result:
                return result
        except Exception as e:
            PrintStyle.warning(f"RFC HTTP failed: {str(e)}")

        # Priority 2: Try Daytona Cloud
        try:
            if runtime in ["python", "nodejs", "terminal"]:
                PrintStyle(font_color="#FFA500", bold=True).print(
                    f"Falling back to Daytona Cloud..."
                )
                result = await self.execute_via_daytona(code, runtime, session)
                if result:
                    return result
        except Exception as e:
            PrintStyle.warning(f"Daytona Cloud failed: {str(e)}")

        # Priority 3: Try RFC SSH
        try:
            PrintStyle(font_color="#FFFF00", bold=True).print(
                f"Falling back to RFC SSH..."
            )
            await self.prepare_state()
            result = await self.execute_via_rfc_ssh(code, runtime, session)
            if result:
                return result
        except Exception as e:
            PrintStyle.warning(f"RFC SSH failed: {str(e)}")

        # Priority 4: Local execution (last resort)
        PrintStyle(font_color="#FF0000", bold=True).print(
            f"WARNING: Using local execution (LAST RESORT - known to be problematic)..."
        )
        await self.prepare_state()
        
        if runtime == "python":
            return await self.execute_python_code(code=code, session=session)
        elif runtime == "nodejs":
            return await self.execute_nodejs_code(code=code, session=session)
        elif runtime == "terminal":
            return await self.execute_terminal_command(command=code, session=session)
        else:
            return self.agent.read_prompt("fw.code.runtime_wrong.md", runtime=runtime)

    async def execute_via_rfc_http(self, code: str, runtime: str, session: int) -> str:
        """Execute code via RFC HTTP API on port 55080"""
        try:
            # Direct HTTP call to RFC server
            url = "http://localhost:55080/execute"
            async with aiohttp.ClientSession() as session_http:
                async with session_http.post(url, json={
                    "code": code,
                    "runtime": runtime,
                    "session": session
                }, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        result = await response.json()
                        output = result.get('output', '') + result.get('error', '')
                        return f"RFC HTTP execution:\\n{output}"
                    else:
                        raise Exception(f"RFC HTTP returned status {response.status}")
                        
        except Exception as e:
            raise Exception(f"RFC HTTP execution failed: {str(e)}")

    async def execute_via_daytona(self, code: str, runtime: str, session: int) -> str:
        """Execute code via Daytona Cloud sandboxes"""
        try:
            # Daytona API configuration
            api_key = "dtn_4e298c6c270f9a3ac8d62e5280fc12965e89e20fe3e4404ae0a412ff05f0ffaf"
            api_url = "https://app.daytona.io/api"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Create execution request
            payload = {
                "code": code,
                "runtime": runtime,
                "timeout": 30
            }
            
            async with aiohttp.ClientSession() as session_http:
                async with session_http.post(
                    f"{api_url}/execute",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        output = result.get('output', '') + result.get('error', '')
                        return f"Daytona Cloud execution:\\n{output}"
                    else:
                        raise Exception(f"Daytona API returned status {response.status}")
                        
        except Exception as e:
            raise Exception(f"Daytona Cloud execution failed: {str(e)}")

    async def execute_via_rfc_ssh(self, code: str, runtime: str, session: int) -> str:
        """Execute code via RFC SSH on port 55022"""
        if runtime == "python":
            escaped_code = shlex.quote(code)
            command = f"python3 -c {escaped_code}"
        elif runtime == "nodejs":
            escaped_code = shlex.quote(code)
            command = f"node -e {escaped_code}"
        elif runtime == "terminal":
            command = code
        else:
            return None
            
        prefix = f"RFC SSH {runtime}> " + self.format_command_for_output(command) + "\\n\\n"
        return await self.terminal_session(session, command, False, prefix)

    # Include all the original helper methods below...
    def get_log_object(self):
        return self.agent.context.log.log(
            type="code_exe",
            heading=self.get_heading(),
            content="",
            kvps=self.args,
        )

    def get_heading(self, text: str = ""):
        if not text:
            text = f"{self.name} - {self.args['runtime']}"
        text = truncate_text_string(text, 60)
        session = self.args.get("session", None)
        session_text = f"[{session}] " if session or session == 0 else ""
        return f"icon://terminal {session_text}{text}"

    async def after_execution(self, response, **kwargs):
        self.agent.hist_add_tool_result(self.name, response.message)

    async def prepare_state(self, reset=False, session=None):
        self.state = self.agent.get_data("_cet_state")
        if not self.state or reset:

            # initialize docker container if execution in docker is configured
            if not self.state and self.agent.config.code_exec_docker_enabled:
                docker = DockerContainerManager(
                    logger=self.agent.context.log,
                    name=self.agent.config.code_exec_docker_name,
                    image=self.agent.config.code_exec_docker_image,
                    ports=self.agent.config.code_exec_docker_ports,
                    volumes=self.agent.config.code_exec_docker_volumes,
                )
                docker.start_container()
            else:
                docker = self.state.docker if self.state else None

            # initialize shells dictionary if not exists
            shells = {} if not self.state else self.state.shells.copy()

            # Only reset the specified session if provided
            if session is not None and session in shells:
                shells[session].close()
                del shells[session]
            elif reset and not session:
                # Close all sessions if full reset requested
                for s in list(shells.keys()):
                    shells[s].close()
                shells = {}

            # initialize local or remote interactive shell interface for session 0 if needed
            if 0 not in shells:
                if self.agent.config.code_exec_ssh_enabled:
                    pswd = (
                        self.agent.config.code_exec_ssh_pass
                        if self.agent.config.code_exec_ssh_pass
                        else await rfc_exchange.get_root_password()
                    )
                    shell = SSHInteractiveSession(
                        self.agent.context.log,
                        self.agent.config.code_exec_ssh_addr,
                        self.agent.config.code_exec_ssh_port,
                        self.agent.config.code_exec_ssh_user,
                        pswd,
                    )
                else:
                    shell = LocalInteractiveSession()

                shells[0] = shell
                await shell.connect()

            self.state = State(shells=shells, docker=docker)
        self.agent.set_data("_cet_state", self.state)

    async def execute_python_code(self, session: int, code: str, reset: bool = False):
        escaped_code = shlex.quote(code)
        # Use system Python with IPython module or fallback to venv IPython
        command = f"python3 -m IPython -c {escaped_code} 2>/dev/null || ipython -c {escaped_code}"
        prefix = "python> " + self.format_command_for_output(code) + "\\n\\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def execute_nodejs_code(self, session: int, code: str, reset: bool = False):
        escaped_code = shlex.quote(code)
        command = f"node /exe/node_eval.js {escaped_code}"
        prefix = "node> " + self.format_command_for_output(code) + "\\n\\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def execute_terminal_command(
        self, session: int, command: str, reset: bool = False
    ):
        prefix = "bash> " + self.format_command_for_output(command) + "\\n\\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def terminal_session(
        self, session: int, command: str, reset: bool = False, prefix: str = ""
    ):

        await self.agent.handle_intervention()
        # try again on lost connection
        for i in range(2):
            try:

                if reset:
                    await self.reset_terminal()

                if session not in self.state.shells:
                    if self.agent.config.code_exec_ssh_enabled:
                        pswd = (
                            self.agent.config.code_exec_ssh_pass
                            if self.agent.config.code_exec_ssh_pass
                            else await rfc_exchange.get_root_password()
                        )
                        shell = SSHInteractiveSession(
                            self.agent.context.log,
                            self.agent.config.code_exec_ssh_addr,
                            self.agent.config.code_exec_ssh_port,
                            self.agent.config.code_exec_ssh_user,
                            pswd,
                        )
                    else:
                        shell = LocalInteractiveSession()
                    self.state.shells[session] = shell
                    await shell.connect()

                self.state.shells[session].send_command(command)

                PrintStyle(
                    background_color="white", font_color="#1B4F72", bold=True
                ).print(f"{self.agent.agent_name} code execution output")
                return await self.get_terminal_output(session=session, prefix=prefix)

            except Exception as e:
                if i == 1:
                    # try again on lost connection
                    PrintStyle.error(str(e))
                    await self.prepare_state(reset=True)
                    continue
                else:
                    raise e

    def format_command_for_output(self, command: str):
        # truncate long commands
        short_cmd = command[:200]
        # normalize whitespace for cleaner output
        short_cmd = " ".join(short_cmd.split())
        # final length
        short_cmd = truncate_text_string(short_cmd, 100)
        return f"{short_cmd}"

    async def get_terminal_output(
        self,
        session=0,
        reset_full_output=True,
        first_output_timeout=30,
        between_output_timeout=15,
        dialog_timeout=5,
        max_exec_timeout=180,
        sleep_time=0.1,
        prefix="",
    ):
        # Common shell prompt regex patterns
        prompt_patterns = [
            re.compile(r"\\(venv\\).+[$#] ?$"),  # (venv) ...$ or (venv) ...#
            re.compile(r"root@[^:]+:[^#]+# ?$"),  # root@container:~#
            re.compile(r"[a-zA-Z0-9_.-]+@[^:]+:[^$#]+[$#] ?$"),  # user@host:~$
        ]

        # potential dialog detection
        dialog_patterns = [
            re.compile(r"Y/N", re.IGNORECASE),
            re.compile(r"yes/no", re.IGNORECASE),
            re.compile(r":\\s*$"),
            re.compile(r"\\?\\s*$"),
        ]

        start_time = time.time()
        last_output_time = start_time
        full_output = ""
        truncated_output = ""
        got_output = False

        # if prefix, log right away
        if prefix:
            self.log.update(content=prefix)

        while True:
            await asyncio.sleep(sleep_time)
            full_output, partial_output = await self.state.shells[session].read_output(
                timeout=1, reset_full_output=reset_full_output
            )
            reset_full_output = False

            await self.agent.handle_intervention()

            now = time.time()
            if partial_output:
                PrintStyle(font_color="#85C1E9").stream(partial_output)
                truncated_output = self.fix_full_output(full_output)
                heading = self.get_heading_from_output(truncated_output, 0)
                self.log.update(content=prefix + truncated_output, heading=heading)
                last_output_time = now
                got_output = True

                # Check for shell prompt at the end of output
                last_lines = (
                    truncated_output.splitlines()[-3:] if truncated_output else []
                )
                last_lines.reverse()
                for idx, line in enumerate(last_lines):
                    for pat in prompt_patterns:
                        if pat.search(line.strip()):
                            PrintStyle.info(
                                "Detected shell prompt, returning output early."
                            )
                            last_lines.reverse()
                            heading = self.get_heading_from_output(
                                "\\n".join(last_lines), idx + 1, True
                            )
                            self.log.update(heading=heading)
                            return truncated_output

            # Check for max execution time
            if now - start_time > max_exec_timeout:
                sysinfo = self.agent.read_prompt(
                    "fw.code.max_time.md", timeout=max_exec_timeout
                )
                response = self.agent.read_prompt("fw.code.info.md", info=sysinfo)
                if truncated_output:
                    response = truncated_output + "\\n\\n" + response
                PrintStyle.warning(sysinfo)
                heading = self.get_heading_from_output(truncated_output, 0)
                self.log.update(content=prefix + response, heading=heading)
                return response

            # Waiting for first output
            if not got_output:
                if now - start_time > first_output_timeout:
                    sysinfo = self.agent.read_prompt(
                        "fw.code.no_out_time.md", timeout=first_output_timeout
                    )
                    response = self.agent.read_prompt("fw.code.info.md", info=sysinfo)
                    PrintStyle.warning(sysinfo)
                    self.log.update(content=prefix + response)
                    return response
            else:
                # Waiting for more output after first output
                if now - last_output_time > between_output_timeout:
                    sysinfo = self.agent.read_prompt(
                        "fw.code.pause_time.md", timeout=between_output_timeout
                    )
                    response = self.agent.read_prompt("fw.code.info.md", info=sysinfo)
                    if truncated_output:
                        response = truncated_output + "\\n\\n" + response
                    PrintStyle.warning(sysinfo)
                    heading = self.get_heading_from_output(truncated_output, 0)
                    self.log.update(content=prefix + response, heading=heading)
                    return response

                # potential dialog detection
                if now - last_output_time > dialog_timeout:
                    # Check for dialog prompt at the end of output
                    last_lines = (
                        truncated_output.splitlines()[-2:] if truncated_output else []
                    )
                    for line in last_lines:
                        for pat in dialog_patterns:
                            if pat.search(line.strip()):
                                PrintStyle.info(
                                    "Detected dialog prompt, returning output early."
                                )

                                sysinfo = self.agent.read_prompt(
                                    "fw.code.pause_dialog.md", timeout=dialog_timeout
                                )
                                response = self.agent.read_prompt(
                                    "fw.code.info.md", info=sysinfo
                                )
                                if truncated_output:
                                    response = truncated_output + "\\n\\n" + response
                                PrintStyle.warning(sysinfo)
                                heading = self.get_heading_from_output(
                                    truncated_output, 0
                                )
                                self.log.update(
                                    content=prefix + response, heading=heading
                                )
                                return response

    async def reset_terminal(self, session=0, reason: str | None = None):
        # Print the reason for the reset to the console if provided
        if reason:
            PrintStyle(font_color="#FFA500", bold=True).print(
                f"Resetting terminal session {session}... Reason: {reason}"
            )
        else:
            PrintStyle(font_color="#FFA500", bold=True).print(
                f"Resetting terminal session {session}..."
            )

        # Only reset the specified session while preserving others
        await self.prepare_state(reset=True, session=session)
        response = self.agent.read_prompt(
            "fw.code.info.md", info=self.agent.read_prompt("fw.code.reset.md")
        )
        self.log.update(content=response)
        return response

    def get_heading_from_output(self, output: str, skip_lines=0, done=False):
        done_icon = " icon://done_all" if done else ""

        if not output:
            return self.get_heading() + done_icon

        # find last non-empty line with skip
        lines = output.splitlines()
        # Start from len(lines) - skip_lines - 1 down to 0
        for i in range(len(lines) - skip_lines - 1, -1, -1):
            line = lines[i].strip()
            if not line:
                continue
            return self.get_heading(line) + done_icon

        return self.get_heading() + done_icon

    def fix_full_output(self, output: str):
        # remove any single byte \\xXX escapes
        output = re.sub(r"(?<!\\)\\x[0-9A-Fa-f]{2}", "", output)
        # Strip every line of output before truncation
        output = "\\n".join(line.strip() for line in output.splitlines())
        output = truncate_text_agent(agent=self.agent, output=output, threshold=10000)
        return output