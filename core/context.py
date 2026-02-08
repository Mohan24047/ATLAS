# Context Manager
# Handles conversation history and prompt building

from config import MAX_HISTORY


class ContextManager:
    """Manages conversation history and context building."""
    
    def __init__(self):
        self.history = []
    
    def add_exchange(self, user_msg, assistant_msg):
        """Add a user-assistant exchange to history."""
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        
        # Trim history if too long (keep last MAX_HISTORY exchanges)
        max_messages = MAX_HISTORY * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
    
    def build_context(self, system_prompt, current_input):
        """
        Build full context for LLM.
        
        Args:
            system_prompt: System instructions
            current_input: Current user message
            
        Returns:
            Formatted context string
        """
        context_parts = [f"System: {system_prompt}\n"]
        
        # Add history
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "Atlas"
            context_parts.append(f"{role}: {msg['content']}")
        
        # Add current input
        context_parts.append(f"User: {current_input}")
        context_parts.append("Atlas:")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear conversation history."""
        self.history = []
