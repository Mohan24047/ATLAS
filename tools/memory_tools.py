from memory.memory_manager import memory

def store_fact(key, value, category="general"):
    """
    Stores a new fact or updates an existing one.
    Args:
        key (str): The key/topic (e.g., "user_name").
        value (str): The fact/value (e.g., "Mohan").
        category (str): Optional category.
    """
    success = memory.store_fact(key, value, category)
    if success:
        return f"Stored: {key} = {value} ({category})"
    else:
        return "Failed to store memory."

def get_fact(key):
    """
    Retrieves a specific fact or searches memory.
    Args:
        key (str): The key or topic to search for.
    """
    # Try exact match first
    fact = memory.get_fact(key)
    if fact:
         return f"{key}: {fact['value']} ({fact['category']})"

    # Fallback to search
    query = key.lower()
    facts = memory.list_facts()
    results = []
    for f in facts:
        if query in f['key'].lower() or query in f['value'].lower():
             results.append(f"{f['key']}: {f['value']}")
    
    if not results:
        return f"No facts found for '{key}'."
        
    return "Found related memories:\n" + "\n".join(results)

def update_fact(key, value):
    """
    Updates an existing fact.
    Args:
        key (str): The key to update.
        value (str): The new value.
    """
    success = memory.update_fact(key, value)
    if success:
        return f"Updated: {key} = {value}"
    else:
        return f"Could not update '{key}'. It might not exist."

def delete_fact(key):
    """
    Deletes a fact from memory.
    Args:
        key (str): The key to delete.
    """
    success = memory.delete_fact(key)
    if success:
        return f"Deleted memory: {key}"
    else:
        return f"Could not delete '{key}'. It might not exist."

def list_memories():
    """
    Lists all stored memories.
    """
    facts = memory.list_facts()
    if not facts:
        return "Memory is empty."
    
    lines = [f"- {f['key']}: {f['value']} ({f.get('category', 'general')})" for f in facts]
    return "Current Memories:\n" + "\n".join(lines)
