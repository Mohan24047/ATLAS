# Skill Registry
# Manages available tools and their metadata for LLM consumption

import inspect
import functools

class SkillRegistry:
    """Registry for AI capabilities (skills)."""
    
    def __init__(self):
        self.skills = {}
    
    def register(self, name=None, description=None):
        """Decorator to register a function as a skill."""
        def decorator(func):
            skill_name = name or func.__name__
            skill_doc = description or func.__doc__ or "No description provided."
            
            # Get function signature
            sig = inspect.signature(func)
            params = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                params.append(f"{param_name}")
            
            self.skills[skill_name] = {
                'func': func,
                'name': skill_name,
                'description': skill_doc,
                'params': params,
                'signature': str(sig)
            }
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_skill(self, name):
        """Get a skill function by name."""
        skill = self.skills.get(name)
        return skill['func'] if skill else None
    
    def list_skills(self):
        """Return list of registered skills."""
        return self.skills.values()
    
    def get_system_prompt_addition(self):
        """Generate the TOOLS section for system prompt."""
        if not self.skills:
            return ""
            
        prompt = "\n\nAVAILABLE TOOLS:\n"
        prompt += "To use a tool, reply with a JSON object: {\"tool\": \"tool_name\", \"args\": { ... }}\n\n"
        
        for name, info in self.skills.items():
            prompt += f"- {name}{info['signature']}: {info['description']}\n"
            
        return prompt

# Global registry instance
registry = SkillRegistry()

# Decorator alias
def skill(name=None, description=None):
    return registry.register(name, description)
