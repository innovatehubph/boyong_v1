from python.helpers.api import ApiHandler, Request, Response
from python.helpers.enhanced_file_browser import EnhancedFileBrowser
from python.helpers import runtime


class GetVpsFiles(ApiHandler):
    """
    Enhanced API endpoint for VPS-wide file system access
    """

    @classmethod
    def get_methods(cls):
        return ["GET"]

    async def process(self, input: dict, request: Request) -> dict | Response:
        current_path = request.args.get("path", "$WORK_DIR")
        
        # Handle special navigation requests
        if current_path == "$VPS_SUMMARY":
            browser = EnhancedFileBrowser()
            return {"data": browser.get_navigation_summary()}
        
        # Get files using enhanced browser
        result = await runtime.call_development_function(get_vps_files, current_path)
        
        return {"data": result}

async def get_vps_files(path):
    browser = EnhancedFileBrowser()
    return browser.get_files(path)