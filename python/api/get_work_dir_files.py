from python.helpers.api import ApiHandler, Request, Response
from python.helpers.enhanced_file_browser import EnhancedFileBrowser
from python.helpers import runtime


class GetWorkDirFiles(ApiHandler):
    """
    Enhanced work directory files API with full VPS access
    Maintains backward compatibility while providing extended functionality
    """

    @classmethod
    def get_methods(cls):
        return ["GET"]

    async def process(self, input: dict, request: Request) -> dict | Response:
        current_path = request.args.get("path", "")
        
        # Handle legacy $WORK_DIR requests - NOW WITH FULL VPS ACCESS
        if current_path == "$WORK_DIR" or current_path == "":
            current_path = "/"  # Map to VPS root for full access
        elif current_path == "root":
            current_path = "/root"  # Map to actual root directory
        elif current_path == "a0":
            current_path = "/a0"  # Keep /a0 access but don't restrict to it

        # Use enhanced browser for better VPS access
        result = await runtime.call_development_function(get_files_enhanced, current_path)

        return {"data": result}

async def get_files_enhanced(path):
    """Enhanced file listing with VPS-wide access"""
    browser = EnhancedFileBrowser()
    return browser.get_files(path)