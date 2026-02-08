from memory.memory_manager import memory
import datetime

def add_task(description):
    """
    Adds a new task to the list.
    Args:
        description (str): Description of the task.
    """
    success = memory.add_task(description)
    if success:
        return f"Task added: {description}"
    else:
        return "Failed to add task."

def list_tasks(status=None):
    """
    Lists tasks, optionally filtered by status ('pending' or 'completed').
    Args:
        status (str): Optional. 'pending' or 'completed'.
    """
    tasks = memory.list_tasks(status)
    if not tasks:
        return "No tasks found."
    
    lines = []
    for t in tasks:
        icon = "[x]" if t['status'] == 'completed' else "[ ]"
        lines.append(f"{t['id']}. {icon} {t['task']}")
    return "\n".join(lines)

def complete_task(task_id):
    """
    Marks a task as completed.
    Args:
        task_id (int): ID of the task to complete.
    """
    try:
        task_id = int(task_id)
        success = memory.complete_task(task_id)
        if success:
            return f"Task {task_id} marked as complete."
        else:
            return f"Task {task_id} not found."
    except ValueError:
        return "Invalid task ID."

def set_reminder(message, time_str):
    """
    Sets a reminder for a specific time.
    Args:
        message (str): What to remind about.
        time_str (str): Time in 'YYYY-MM-DD HH:MM:SS' format, or relative like 'in 5 minutes' (handled by parsing if implementing NLP, simpler format for now).
                        Let's support ISO format or simple 'HH:MM' for today.
    """
    # Simple parsing logic for now. 
    # Ideal: "in 5 minutes" -> delta
    # For now, let's assume LLM gives ISO or we parse relative here manually?
    # Actually, let's ask LLM to convert to ISO.
    
    try:
        # Check if time_str matches regex for ISO
        # Implementation detail: we rely on LLM to provide ISO timestamp for now
        # OR we could accept 'HH:MM' and assume today.
        
        # Keep it simple: Assume ISO or try dateutil if installed? 
        # Requirement: "Use standard Python libraries". 
        # Let's try to parse 'HH:MM' as today, otherwise expect full ISO.
        
        target_time = None
        now = datetime.datetime.now()
        
        # Handle relative time: "in 5 minutes", "in 10 seconds", "in 2 hours"
        relative_match = False
        if time_str.lower().startswith("in "):
            try:
                parts = time_str.lower().replace("in ", "").split()
                if len(parts) >= 2:
                    amount = int(parts[0])
                    unit = parts[1]
                    
                    if "second" in unit:
                        target_time = now + datetime.timedelta(seconds=amount)
                        relative_match = True
                    elif "minute" in unit:
                        target_time = now + datetime.timedelta(minutes=amount)
                        relative_match = True
                    elif "hour" in unit:
                        target_time = now + datetime.timedelta(hours=amount)
                        relative_match = True
            except ValueError:
                pass # Fallback to other formats
        
        if not relative_match:
            if len(time_str) == 5 and ':' in time_str: # HH:MM
                hours, minutes = map(int, time_str.split(':'))
                target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if target_time < now:
                    target_time += datetime.timedelta(days=1) # Tomorrow
            else:
                 target_time = datetime.datetime.fromisoformat(time_str)
             
        rid = memory.add_reminder(message, target_time.isoformat())
        return f"Reminder set for {target_time.strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    except ValueError:
        return "Invalid time format. Please use 'in X minutes', 'HH:MM', or ISO format."
