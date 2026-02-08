import os
import subprocess
import datetime

ATLAS_FILES_DIR = r"C:\Users\Mohan\OneDrive\Desktop\ATLAS_FILES"

ALLOWED_APPS = {
    'antigravity': 'code',
    'chrome': 'chrome',
    'explorer': 'explorer',
    'terminal': 'start cmd',
    'cmd': 'start cmd'
}

def get_time():
    """Returns the current time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def open_app(app_name):
    """Opens an allowed application."""
    app_key = app_name.lower()
    if app_key not in ALLOWED_APPS:
        return f"App '{app_name}' is not in the whitelist. Allowed: {list(ALLOWED_APPS.keys())}"
    
    command = ALLOWED_APPS[app_key]
    try:
        if app_key == 'explorer':
            subprocess.run(['explorer'], check=True)
        else:
            subprocess.run(command, shell=True, check=True)
        return f"Opened {app_name}."
    except Exception as e:
        return f"Error opening {app_name}: {e}"

def open_folder(path):
    """Opens a folder. Only ATLAS_FILES_DIR is allowed directly."""
    if os.path.normpath(path) == os.path.normpath(ATLAS_FILES_DIR):
        try:
            os.startfile(path)
            return f"Opened folder: {path}"
        except Exception as e:
            return f"Error opening folder: {e}"
    else:
        return f"Access restricted. Only '{ATLAS_FILES_DIR}' can be opened directly."

def open_file(path):
    """Opens a file. Only files inside ATLAS_FILES_DIR are allowed."""
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(os.path.abspath(ATLAS_FILES_DIR)):
        return f"Access restricted. Only files in '{ATLAS_FILES_DIR}' can be opened."
         
    try:
        os.startfile(abs_path)
        return f"Opened file: {abs_path}"
    except Exception as e:
        return f"Error opening file: {e}"
