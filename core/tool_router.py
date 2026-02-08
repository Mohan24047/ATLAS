import inspect
from tools import file_tools, system_tools, memory_tools, task_tools, workflow_tools

class ToolRouter:
    """Manages tool registration, execution, and safety checks."""
    
    def __init__(self):
        self.tools = {}
        self.register_module(file_tools)
        self.register_module(system_tools)
        self.register_module(memory_tools)
        self.register_module(task_tools)
        self.register_module(workflow_tools)
        
        # Define destructive tools that require confirmation
        self.destructive_tools = {
            'create_file',
            'edit_file',
            'write_file', 
            'run_command', 
            'delete_file',
            'delete_fact',
            'update_fact'
        }

    def register_module(self, module):
        """Register all functions in a module as tools."""
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith('_'):
                self.tools[name] = func

    def get_tool(self, name):
        """Get a tool function by name."""
        return self.tools.get(name)

    def is_destructive(self, tool_name):
        """Check if a tool is destructive."""
        return tool_name in self.destructive_tools

    def execute_tool(self, tool_name, args):
        """Execute a tool."""
        func = self.get_tool(tool_name)
        if not func:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            # Handle both dict args and positional args if needed, 
            # but assuming args is a dict from LLM JSON.
            return func(**args)
        except Exception as e:
            return f"Error executing '{tool_name}': {e}"

# Singleton
router = ToolRouter()
