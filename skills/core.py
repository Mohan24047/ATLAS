# Core Skills
# Basic system capabilities: Time, Date, Weather, System Info

import datetime
import platform
import os
from .registry import skill

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@skill(name="get_time", description="Get current local time")
def get_time():
    """Returns the current local time."""
    now = datetime.datetime.now()
    return f"Current time is {now.strftime('%I:%M %p')}"


@skill(name="get_date", description="Get current date")
def get_date():
    """Returns the current date."""
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}"


@skill(name="system_info", description="Get system status (CPU, RAM, OS)")
def system_info():
    """Returns system information."""
    info = []
    info.append(f"OS: {platform.system()} {platform.release()}")
    
    if PSUTIL_AVAILABLE:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        info.append(f"CPU Usage: {cpu}%")
        info.append(f"Memory: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
    else:
        info.append("Detailed stats unavailable (psutil not installed)")
        
    return " | ".join(info)
