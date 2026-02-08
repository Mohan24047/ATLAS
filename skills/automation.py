# Automation Skills
# Controls for opening apps and system handling

import os
import subprocess
import platform
from .registry import skill


APPS = {
    'notepad': 'notepad.exe',
    'calculator': 'calc.exe',
    'chrome': 'start chrome',
    'browser': 'start msedge',
    'explorer': 'explorer.exe',
    'cmd': 'start cmd',
    'code': 'code',
}


@skill(name="open_app", description="Open an application (notepad, calculator, browser, etc)")
def open_app(app_name):
    """Opens a specified application."""
    app_key = app_name.lower().strip()
    
    # Check known apps
    if app_key in APPS:
        try:
            cmd = APPS[app_key]
            if platform.system() == "Windows":
                os.system(cmd)
            else:
                subprocess.Popen(app_key) # Simple fallback
            return f"Opening {app_name}..."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
    
    return f"I don't know how to open '{app_name}' yet. Available apps: {', '.join(APPS.keys())}"


@skill(name="shutdown", description="Shutdown the computer (requires confirmation)")
def shutdown():
    """Shutdown the system."""
    # For safety, we just return a message for now
    return "To shutdown, please execute the command manually. I am in safe mode."
