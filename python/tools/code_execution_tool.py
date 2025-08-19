import asyncio
from dataclasses import dataclass
import shlex
import time
from python.helpers.tool import Tool, Response
from python.helpers import files, rfc_exchange
from python.helpers.print_style import PrintStyle
from python.helpers.shell_local_optimized import OptimizedLocalInteractiveSession as LocalInteractiveSession
from python.helpers.shell_ssh import SSHInteractiveSession
from python.helpers.execution_manager import get_execution_manager, ParengBoyongExecutionManager
from python.helpers.automatic_deployment_system import get_deployment_system
from python.helpers.docker import DockerContainerManager
from python.helpers.strings import truncate_text as truncate_text_string
from python.helpers.messages import truncate_text as truncate_text_agent
import re


@dataclass
class State:
    shells: dict[int, LocalInteractiveSession | SSHInteractiveSession | ParengBoyongExecutionManager]
    docker: DockerContainerManager | None


class CodeExecution(Tool):

    async def execute(self, **kwargs):

        await self.agent.handle_intervention()  # wait for intervention and handle it, if paused

        await self.prepare_state()

        # os.chdir(files.get_abs_path("./work_dir")) #change CWD to work_dir

        runtime = self.args.get("runtime", "").lower().strip()
        session = int(self.args.get("session", 0))

        if runtime == "python":
            response = await self.execute_python_code(
                code=self.args["code"], session=session
            )
        elif runtime == "nodejs":
            response = await self.execute_nodejs_code(
                code=self.args["code"], session=session
            )
        elif runtime == "terminal":
            response = await self.execute_terminal_command(
                command=self.args["code"], session=session
            )
        elif runtime == "output":
            response = await self.get_terminal_output(
                session=session, first_output_timeout=60, between_output_timeout=5
            )
        elif runtime == "reset":
            response = await self.reset_terminal(session=session)
        else:
            response = self.agent.read_prompt(
                "fw.code.runtime_wrong.md", runtime=runtime
            )

        if not response:
            response = self.agent.read_prompt(
                "fw.code.info.md", info=self.agent.read_prompt("fw.code.no_output.md")
            )
        return Response(message=response, break_loop=False)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="code_exe",
            heading=self.get_heading(),
            content="",
            kvps=self.args,
        )

    def get_heading(self, text: str = ""):
        if not text:
            runtime = getattr(self, 'args', {}).get('runtime', 'python') if hasattr(self, 'args') and self.args else 'python'
            text = f"{self.name} - {runtime}"
        text = truncate_text_string(text, 60)
        session = getattr(self, 'args', {}).get("session", None) if hasattr(self, 'args') and self.args else None
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

            # initialize execution manager for session 0 if needed - Pareng Boyong Enhancement
            if 0 not in shells:
                # Use enhanced execution manager with AI error recovery
                execution_manager = get_execution_manager(self.agent.context.log, self.agent.config, self.agent)
                
                # Force local execution if SSH is disabled (default now)
                if not self.agent.config.code_exec_ssh_enabled:
                    execution_manager.force_local_execution()
                    PrintStyle(font_color="green").print("🚀 Using local execution (SSH disabled for reliability)")
                
                # Enable AI error recovery for this session
                if hasattr(execution_manager, 'recovery_system'):
                    execution_manager.recovery_system.enable_recovery()
                    PrintStyle(font_color="cyan").print("🤖 AI error recovery: ENABLED")
                
                shells[0] = execution_manager
                if not await execution_manager.connect():
                    raise Exception("Failed to establish any execution strategy")
                
                PrintStyle(font_color="cyan").print(f"✅ Execution ready: {execution_manager.get_strategy_info()}")

            self.state = State(shells=shells, docker=docker)
        self.agent.set_data("_cet_state", self.state)

    async def execute_python_code(self, session: int, code: str, reset: bool = False):
        escaped_code = shlex.quote(code)
        command = f"ipython -c {escaped_code}"
        prefix = "python> " + self.format_command_for_output(code) + "\n\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def execute_nodejs_code(self, session: int, code: str, reset: bool = False):
        escaped_code = shlex.quote(code)
        command = f"node /exe/node_eval.js {escaped_code}"
        prefix = "node> " + self.format_command_for_output(code) + "\n\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def execute_terminal_command(
        self, session: int, command: str, reset: bool = False
    ):
        prefix = "bash> " + self.format_command_for_output(command) + "\n\n"
        return await self.terminal_session(session, command, reset, prefix)

    async def terminal_session(
        self, session: int, command: str, reset: bool = False, prefix: str = ""
    ):

        await self.agent.handle_intervention()  # wait for intervention and handle it, if paused
        # try again on lost connection
        for i in range(2):
            try:

                if reset:
                    await self.reset_terminal()

                if session not in self.state.shells:
                    # Use enhanced execution manager for new sessions - Pareng Boyong Enhancement
                    execution_manager = get_execution_manager(self.agent.context.log, self.agent.config, self.agent)
                    
                    # Force local execution if SSH is disabled
                    if not self.agent.config.code_exec_ssh_enabled:
                        execution_manager.force_local_execution()
                    
                    # Enable AI error recovery
                    if hasattr(execution_manager, 'recovery_system'):
                        execution_manager.recovery_system.enable_recovery()
                        
                    self.state.shells[session] = execution_manager
                    if not await execution_manager.connect():
                        raise Exception(f"Failed to establish execution strategy for session {session}")
                        
                    PrintStyle(font_color="cyan").print(f"Session {session}: {execution_manager.get_strategy_info()}")

                self.state.shells[session].send_command(command)

                PrintStyle(
                    background_color="white", font_color="#1B4F72", bold=True
                ).print(f"{self.agent.agent_name} code execution output")
                
                output = await self.get_terminal_output(session=session, prefix=prefix)
                
                # Post-execution webapp deployment check
                await self._check_and_deploy_webapps(command, output)
                
                return output

            except (OSError, ConnectionError) as e:
                if "Socket is closed" in str(e) or "Connection lost" in str(e):
                    self.agent.context.log.log("SSH socket closed, attempting reconnection...")
                    if i == 0:  # First attempt - try to reconnect
                        PrintStyle.warning(f"SSH connection lost: {e}")
                        await self.prepare_state(reset=True, session=session)
                        continue
                    else:
                        raise Exception(f"Failed to re-establish SSH connection after retry: {e}")
                else:
                    raise e
            except Exception as e:
                if i == 0:
                    # try again on lost connection
                    PrintStyle.error(str(e))
                    await self.prepare_state(reset=True, session=session)
                    continue
                else:
                    raise e

    def format_command_for_output(self, command: str):
        # truncate long commands
        short_cmd = command[:200]
        # normalize whitespace for cleaner output
        short_cmd = " ".join(short_cmd.split())
        # replace any sequence of ', ", or ` with a single '
        # short_cmd = re.sub(r"['\"`]+", "'", short_cmd) # no need anymore
        # final length
        short_cmd = truncate_text_string(short_cmd, 100)
        return f"{short_cmd}"

    async def get_terminal_output(
        self,
        session=0,
        reset_full_output=True,
        first_output_timeout=10,  # Reduced from 30 - faster first output detection
        between_output_timeout=3,  # Reduced from 15 - faster completion detection
        dialog_timeout=2,  # Reduced from 5 - faster dialog detection
        max_exec_timeout=120,  # Reduced from 180 - reasonable max runtime
        sleep_time=0.01,  # Reduced from 0.1 - more responsive checking
        prefix="",
    ):
        # Common shell prompt regex patterns (add more as needed)
        prompt_patterns = [
            re.compile(r"\\(venv\\).+[$#] ?$"),  # (venv) ...$ or (venv) ...#
            re.compile(r"root@[^:]+:[^#]+# ?$"),  # root@container:~#
            re.compile(r"[a-zA-Z0-9_.-]+@[^:]+:[^$#]+[$#] ?$"),  # user@host:~$
        ]

        # potential dialog detection
        dialog_patterns = [
            re.compile(r"Y/N", re.IGNORECASE),  # Y/N anywhere in line
            re.compile(r"yes/no", re.IGNORECASE),  # yes/no anywhere in line
            re.compile(r":\s*$"),  # line ending with colon
            re.compile(r"\?\s*$"),  # line ending with question mark
        ]

        start_time = time.time()
        last_output_time = start_time
        full_output = ""
        truncated_output = ""
        got_output = False

        # if prefix, log right away
        if prefix:
            self.log.update(content=prefix)

        # Check if using optimized session for faster completion detection
        shell = self.state.shells[session]
        is_optimized = hasattr(shell, 'is_command_finished')
        
        while True:
            await asyncio.sleep(sleep_time)
            full_output, partial_output = await shell.read_output(
                timeout=0.5 if is_optimized else 1,  # Faster timeout for optimized sessions
                reset_full_output=reset_full_output
            )
            reset_full_output = False  # only reset once
            
            # Fast path: Check if command is finished (optimized sessions only)
            if is_optimized and shell.is_command_finished():
                PrintStyle.info("Command completed (optimized detection)")
                heading = self.get_heading_from_output(full_output, 0, True)
                self.log.update(content=prefix + full_output, heading=heading)
                return full_output

            await self.agent.handle_intervention()

            now = time.time()
            if partial_output:
                PrintStyle(font_color="#85C1E9").stream(partial_output)
                # full_output += partial_output # Append new output
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
                                "\n".join(last_lines), idx + 1, True
                            )
                            self.log.update(heading=heading)
                            return truncated_output

            # Early termination check for hanging processes
            if is_optimized and now - last_output_time > 5 and not got_output:
                # No output for 5 seconds on first run - likely hanging
                if hasattr(shell, 'kill_hanging_processes'):
                    await shell.kill_hanging_processes()
                    PrintStyle.warning("Killed potential hanging processes")
            
            # Check for max execution time
            if now - start_time > max_exec_timeout:
                sysinfo = self.agent.read_prompt(
                    "fw.code.max_time.md", timeout=max_exec_timeout
                )
                response = self.agent.read_prompt("fw.code.info.md", info=sysinfo)
                if truncated_output:
                    response = truncated_output + "\n\n" + response
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
                        response = truncated_output + "\n\n" + response
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
                                
                                # Kill any hanging processes before returning
                                if is_optimized and hasattr(shell, 'kill_hanging_processes'):
                                    await shell.kill_hanging_processes()

                                sysinfo = self.agent.read_prompt(
                                    "fw.code.pause_dialog.md", timeout=dialog_timeout
                                )
                                response = self.agent.read_prompt(
                                    "fw.code.info.md", info=sysinfo
                                )
                                if truncated_output:
                                    response = truncated_output + "\n\n" + response
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
        # remove any single byte \xXX escapes
        output = re.sub(r"(?<!\\)\\x[0-9A-Fa-f]{2}", "", output)
        # Strip every line of output before truncation
        output = "\n".join(line.strip() for line in output.splitlines())
        output = truncate_text_agent(agent=self.agent, output=output, threshold=10000)
        return output
    
    async def _check_and_deploy_webapps(self, command: str, output: str):
        """Check if webapps were created during execution and auto-deploy them"""
        
        try:
            # Check if this command might have created a webapp
            webapp_indicators = [
                'create-react-app', 'npx create-react-app', 'npm create react-app',
                'vue create', '@vue/cli', 'vue-cli',
                'express', 'npm init', 'npm install express',
                'flask', 'django-admin startproject',
                'mkdir', 'git clone',
                'index.html', 'app.py', 'server.js', 'main.py'
            ]
            
            # Check if command or output contains webapp indicators
            command_lower = command.lower()
            output_lower = output.lower()
            
            might_be_webapp = any(indicator in command_lower or indicator in output_lower 
                                for indicator in webapp_indicators)
            
            if might_be_webapp:
                PrintStyle(font_color="yellow").print("🔍 Checking for new webapps to deploy...")
                
                # Get deployment system
                deployment_system = get_deployment_system(self.agent.context.log)
                
                # Detect new webapps
                detected_webapps = deployment_system.detector.detect_new_webapps()
                
                for webapp in detected_webapps:
                    # Check if this webapp is not already deployed
                    if webapp.name not in deployment_system.deployed_webapps:
                        PrintStyle(font_color="cyan").print(f"🚀 Auto-deploying new webapp: {webapp.name}")
                        
                        # Deploy automatically
                        await deployment_system._deploy_webapp_automatically(webapp)
                        
                        # Inform user about the deployed webapp
                        if webapp.deployment_status == "deployed" and webapp.public_url:
                            PrintStyle(font_color="green").print(f"🎉 WEBAPP DEPLOYED FOR USER ACCESS!")
                            PrintStyle(font_color="green").print(f"   📱 Name: {webapp.name}")
                            PrintStyle(font_color="green").print(f"   🌐 URL: {webapp.public_url}")
                            PrintStyle(font_color="green").print(f"   ☁️ Service: {webapp.deployment_service.title()}")
                            
                            # Add deployment info to agent's response
                            deployment_info = f"\n\n🎉 **WEBAPP DEPLOYED!**\n" + \
                                           f"📱 **{webapp.name}** is now accessible at:\n" + \
                                           f"🌐 **{webapp.public_url}**\n" + \
                                           f"☁️ Hosted on {webapp.deployment_service.title()}\n\n" + \
                                           f"✅ Users can now access your webapp from anywhere!"
                            
                            # Store deployment info for the agent to include in response
                            if not hasattr(self.agent, '_webapp_deployments'):
                                self.agent._webapp_deployments = []
                            self.agent._webapp_deployments.append(deployment_info)
        
        except Exception as e:
            # Don't let deployment errors break code execution
            self.agent.context.log.log(f"Webapp deployment check error: {e}")
