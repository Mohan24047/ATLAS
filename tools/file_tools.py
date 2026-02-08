import os

# Allowed directory for file operations
ATLAS_FILES_DIR = r"C:\Users\Mohan\OneDrive\Desktop\ATLAS_FILES"

def _get_safe_path(path):
    """
    Resolves path and ensures it is within ATLAS_FILES_DIR.
    Returns absolute path if safe, else raises ValueError.
    """
    # Create allowed dir if it doesn't exist (safety)
    if not os.path.exists(ATLAS_FILES_DIR):
        os.makedirs(ATLAS_FILES_DIR, exist_ok=True)

    # Handle absolute paths: must start with ATLAS_FILES_DIR
    if os.path.isabs(path):
        clean_path = os.path.normpath(path)
        if not clean_path.startswith(ATLAS_FILES_DIR):
            raise ValueError(f"Access denied: Path '{path}' is outside allowed directory '{ATLAS_FILES_DIR}'.")
        return clean_path
    
    # Handle relative paths: join with ATLAS_FILES_DIR
    safe_path = os.path.abspath(os.path.join(ATLAS_FILES_DIR, path))
    if not safe_path.startswith(ATLAS_FILES_DIR):
         raise ValueError(f"Access denied: Path '{path}' attempts to escape allowed directory.")
    
    return safe_path

def create_file(path, content):
    """
    Creates a new file with content.
    Args:
        path (str): Filename or path relative to ATLAS_FILES.
        content (str): Content to write.
    """
    try:
        full_path = _get_safe_path(path)
        
        # Ensure directory exists
        directory = os.path.dirname(full_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file: {full_path}"
    except Exception as e:
        return f"Error creating file: {e}"

def read_file(path):
    """
    Reads content from a file.
    Args:
        path (str): Filename or path relative to ATLAS_FILES.
    """
    try:
        full_path = _get_safe_path(path)
        if not os.path.exists(full_path):
            return f"File not found: {path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def list_files(directory="."):
    """
    Lists files in a directory.
    Args:
        directory (str): Directory relative to ATLAS_FILES.
    """
    try:
        full_path = _get_safe_path(directory)
        if not os.path.exists(full_path):
             return f"Directory not found: {directory}"
             
        items = os.listdir(full_path)
        return "\n".join(items) if items else "(Empty directory)"
    except Exception as e:
        return f"Error listing files: {e}"

def edit_file(path, content):
    """
    Overwrites an existing file.
    Args:
        path (str): Filename relative to ATLAS_FILES.
        content (str): New content.
    """
    # Currently same as create_file, but semantically distinct
    return create_file(path, content)
