import os
import subprocess
import time
from tools import system_tools

def start_coding(**kwargs):
    """Starts the coding environment: VS Code, ATLAS_FILES folder, and terminal."""
    results = []
    
    res_app = system_tools.open_app("antigravity")
    results.append(res_app)
    time.sleep(1)
    
    res_folder = system_tools.open_folder(system_tools.ATLAS_FILES_DIR)
    results.append(res_folder)
    time.sleep(1)
    
    try:
        cmd = f'start cmd /K "cd /d {system_tools.ATLAS_FILES_DIR}"'
        subprocess.run(cmd, shell=True, check=True)
        results.append("Opened terminal in project folder.")
    except Exception as e:
        results.append(f"Error opening terminal: {e}")
        
    return "\n".join(results)
