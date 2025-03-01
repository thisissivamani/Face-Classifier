from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Get environment info
            python_version = sys.version
            cwd = os.getcwd()
            files = os.listdir('.')
            api_files = []
            if os.path.exists('api'):
                api_files = os.listdir('api')
                
            # Construct debug info
            debug_info = {
                "status": "debug_info",
                "python_version": python_version,
                "current_directory": cwd,
                "files_in_root": files,
                "files_in_api": api_files,
                "sys_path": sys.path,
                "environment": dict(os.environ)
            }
            
            # Try to import modules
            module_status = {}
            for module in ["numpy", "cv2", "pywt", "joblib", "flask"]:
                try:
                    __import__(module)
                    module_status[module] = "available"
                except ImportError as e:
                    module_status[module] = f"error: {str(e)}"
            
            debug_info["modules"] = module_status
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(debug_info, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "traceback": traceback.format_exc()
            }).encode())

def handler(request):
    try:
        # Get environment info
        python_version = sys.version
        cwd = os.getcwd()
        files = os.listdir('.')
        api_files = []
        if os.path.exists('api'):
            api_files = os.listdir('api')
            
        # Construct debug info
        debug_info = {
            "status": "debug_info",
            "python_version": python_version,
            "current_directory": cwd,
            "files_in_root": files,
            "files_in_api": api_files,
            "sys_path": sys.path,
            "environment": dict(os.environ)
        }
        
        # Try to import modules
        module_status = {}
        for module in ["numpy", "cv2", "pywt", "joblib", "flask"]:
            try:
                __import__(module)
                module_status[module] = "available"
            except ImportError as e:
                module_status[module] = f"error: {str(e)}"
        
        debug_info["modules"] = module_status
        
        return {
            "statusCode": 200,
            "body": json.dumps(debug_info, default=str),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "traceback": traceback.format_exc()
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
