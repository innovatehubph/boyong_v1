from python.helpers.tool import Tool, Response
import re


class ResponseTool(Tool):

    def detect_multimedia_in_response(self, text: str) -> dict:
        """Detect multimedia generation requests in response text"""
        
        text_lower = text.lower()
        
        # Enhanced detection patterns for responses
        image_patterns = [
            r'(i\'ll|let me|i will)\s+(create|generate|make|design)\s+(an?\s+)?(image|picture|photo|artwork)',
            r'(creating|generating|making)\s+(an?\s+)?(image|picture|photo|artwork)',
            r'(here\'s|here is)\s+(an?\s+)?(image|picture|photo)',
            r'\b(create|generate|make|draw|design)\s+(an?\s+)?(image|picture|photo|artwork|larawan)',
            r'gumawa\s+ng\s+(larawan|image)'
        ]
        
        video_patterns = [
            r'(i\'ll|let me|i will)\s+(create|generate|make|produce)\s+(a\s+)?(video|animation|clip)',
            r'(creating|generating|making)\s+(a\s+)?(video|animation|clip)',
            r'(here\'s|here is)\s+(a\s+)?(video|animation|clip)',
            r'\b(create|generate|make|produce)\s+(a\s+)?(video|animation|clip|movie)',
            r'(cinematic|film)\s+(video|scene)',
            r'gumawa\s+ng\s+video'
        ]
        
        # Check for image requests
        for pattern in image_patterns:
            if re.search(pattern, text_lower):
                return {
                    "type": "image",
                    "confidence": 0.7,
                    "prompt": text
                }
        
        # Check for video requests
        for pattern in video_patterns:
            if re.search(pattern, text_lower):
                return {
                    "type": "video",
                    "confidence": 0.7,
                    "prompt": text
                }
        
        return {"type": None, "confidence": 0.0}

    async def execute(self, **kwargs):
        message = self.args["text"] if "text" in self.args else self.args["message"]
        
        # Check for multimedia requests in the response message using Docker services
        try:
            detection = self.detect_multimedia_in_response(message)
            
            if detection["type"] and detection["confidence"] > 0.6:
                # Import Docker multimedia tools
                from python.tools.docker_multimedia_generator import (
                    generate_image_docker_tool,
                    generate_video_docker_tool,
                    check_docker_multimedia_services
                )
                
                # Check service health
                health_status = check_docker_multimedia_services()
                if health_status["overall_status"] in ["healthy", "partial"]:
                    
                    if detection["type"] == "image":
                        result = generate_image_docker_tool(
                            prompt=message,
                            width=1024,
                            height=1024
                        )
                        
                        if result.get("status") == "success":
                            file_path = result.get("file_path", "")
                            web_path = file_path.replace("/root/projects/pareng-boyong/pareng_boyong_deliverables/", "/pareng_boyong_deliverables/")
                            metadata = result.get("metadata", {})
                            
                            multimedia_message = f"""{message}

🎨 **Auto-Generated Image**
**Service:** Pollinations.AI (FLUX.1)
**Category:** {metadata.get('category', 'artwork').replace('_', ' ').title()}
**File:** `{file_path}`
**View:** [Click to view]({web_path})

<image>{result.get('image_base64', '')}</image>"""
                            
                            return Response(message=multimedia_message, break_loop=True)
                    
                    elif detection["type"] == "video":
                        result = generate_video_docker_tool(
                            prompt=message,
                            duration=4,
                            resolution="720p"
                        )
                        
                        if result.get("status") == "success":
                            file_path = result.get("file_path", "")
                            web_path = file_path.replace("/root/projects/pareng-boyong/pareng_boyong_deliverables/", "/pareng_boyong_deliverables/")
                            metadata = result.get("metadata", {})
                            
                            multimedia_message = f"""{message}

🎬 **Auto-Generated Video**  
**Service:** Wan2GP (CPU-optimized)
**Model:** {metadata.get('model', 'wan2gp')}
**Duration:** {metadata.get('duration', 4)}s
**File:** `{file_path}`
**View:** [Click to view]({web_path})

<video>{result.get('video_base64', '')}</video>"""
                            
                            return Response(message=multimedia_message, break_loop=True)
                
        except (ImportError, Exception) as e:
            # If multimedia fails, just use original message
            pass
            
        return Response(message=message, break_loop=True)

    async def before_execution(self, **kwargs):
        # self.log = self.agent.context.log.log(type="response", heading=f"{self.agent.agent_name}: Responding", content=self.args.get("text", ""))
        # don't log here anymore, we have the live_response extension now
        pass

    async def after_execution(self, response, **kwargs):
        # do not add anything to the history or output

        if self.loop_data and "log_item_response" in self.loop_data.params_temporary:
            log = self.loop_data.params_temporary["log_item_response"]
            log.update(finished=True) # mark the message as finished
