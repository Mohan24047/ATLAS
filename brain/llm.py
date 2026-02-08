# LLM Module - Ollama Integration
# Handles communication with local Ollama model

import requests
import sys
sys.path.insert(0, '..')
from config import MODEL_NAME, OLLAMA_HOST


def initialize_model():
    """
    Check if Ollama is running and model is available.
    Returns True if ready, False otherwise.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if any(MODEL_NAME in name for name in model_names):
                return True
            print(f"[Warning] Model '{MODEL_NAME}' not found. Available: {model_names}")
            return True  # Still allow attempt
        return False
    except requests.exceptions.ConnectionError:
        print("[Error] Cannot connect to Ollama. Is it running?")
        return False
    except Exception as e:
        print(f"[Error] Initialization failed: {e}")
        return False


def generate_response(user_text, context):
    """
    Send prompt to Ollama and return response.
    
    Args:
        user_text: Current user message
        context: Full context including system prompt and history
        
    Returns:
        Response string or error message
    """
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": context,
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response received.")
        else:
            return f"[Error] Ollama returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "[Error] Request timed out. Model may be busy."
    except requests.exceptions.ConnectionError:
        return "[Error] Lost connection to Ollama."
    except Exception as e:
        return f"[Error] {str(e)}"
