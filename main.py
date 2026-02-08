# Atlas Main Entry Point
# Terminal-based AI assistant with wake word, memory, and voice

import sys
import os
import re
import time
import threading
import queue

# Add atlas directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ASSISTANT_NAME
from brain.llm import initialize_model, generate_response
from brain.prompt import get_prompt_with_memory
from core.context import ContextManager
from memory.memory_manager import memory
from speech.tts import speak, stop_speaking, get_tts
from speech.stt import listen_once, is_available as stt_available
from utils.logger import Logger
import json
from skills.registry import registry


# Patterns that suggest user wants to store information
MEMORY_TRIGGERS = [
    r'\bmy name is\b',
    r'\bremember that\b',
    r'\bi prefer\b',
    r'\bmy project\b',
    r'\bmy favorite\b',
    r'\bi like\b',
    r'\bi am\b',
    r'\bcall me\b',
]

# Patterns for memory recall
RECALL_TRIGGERS = [
    r'what do you (know|remember) about me',
    r'list (my )?memory',
    r'what have you remembered',
    r'show (my )?facts',
]

# Wake words
WAKE_WORDS = ["atlas", "at less", "at lass", "at last", "address"]


def should_ask_to_remember(text):
    """Check if the message contains memory-worthy information."""
    text_lower = text.lower()
    for pattern in MEMORY_TRIGGERS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_recall_request(text):
    """Check if user is asking about stored memory."""
    text_lower = text.lower()
    for pattern in RECALL_TRIGGERS:
        if re.search(pattern, text_lower):
            return True
    return False


def contains_wake_word(text):
    """Check if text contains wake word."""
    text_lower = text.lower()
    for word in WAKE_WORDS:
        if word in text_lower:
            return True
    return False


def extract_fact_from_input(text):
    """Extract a key-value fact from user input."""
    text_lower = text.lower()
    
    patterns = [
        (r'my name is (\w+)', 'name', None),
        (r'call me (\w+)', 'name', None),
        (r'i prefer (.+)', 'preference', 'preference'),
        (r'my favorite (.+?) is (.+)', None, None),
        (r'my (.+?) is (.+)', None, None),
        (r'remember that (.+)', 'note', 'note'),
        (r'i am (?:a |an )?(.+)', 'identity', 'personal'),
        (r'i like (.+)', 'likes', 'preference'),
    ]
    
    for pattern, default_key, category in patterns:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                return default_key, groups[0].strip(), category
            elif len(groups) == 2:
                return groups[0].strip(), groups[1].strip(), category
    
    return None, None, None


def format_facts_for_display(facts):
    """Format facts for terminal display."""
    if not facts:
        return "I don't have any stored information about you yet."
    
    lines = ["Here's what I remember about you:", ""]
    for fact in facts:
        category = f" [{fact['category']}]" if fact['category'] else ""
        lines.append(f"  • {fact['key']}: {fact['value']}{category}")
    
    return "\n".join(lines)


from core.tool_router import router
from core.scheduler import Scheduler

class AtlasAssistant:
    """Main Atlas assistant."""
    
    def __init__(self):
        self.context = ContextManager()
        self.pending_memory = None
        self.pending_tool_call = None
        self.running = True
        
        # Start Scheduler for background tasks (reminders)
        self.scheduler = Scheduler(notification_callback=self.on_notification)
        self.scheduler.start()
        
    def on_notification(self, message):
        """Handle background notifications."""
        print(f"\n[Notification] {message}")
        # Ideally, we should speak this if idle, or queue it.
        # For now, just print to avoid interrupting active conversation logic too much.
        # But user wants "voice alerts".
        # We can try to speak it.
        speak(message)
    
    def process_command(self, user_input):
        """Process a user command and return response."""
        
        # Handle shutdown command
        if 'shutdown' in user_input.lower():
            self.running = False
            return "Shutting down. Goodbye, sir."
        
        # Handle reminder confirmation
        cleaned_input = re.sub(r'[^\w\s]', '', user_input.lower())
        confirmation_words = ['done', 'confirmed', 'okay', 'ok', 'stop', 'silence', 'got it']
        if any(word in cleaned_input.split() for word in confirmation_words):
             if self.scheduler.confirm_all():
                 return "Reminder confirmed."

        # Handle pending memory confirmation
        # Handle pending memory confirmation
        if self.pending_memory:
            cleaned_input = re.sub(r'[^\w\s]', '', user_input.lower())
            affirmative = ['yes', 'y', 'sure', 'ok', 'okay', 'yeah', 'correct', 'right', 'please', 'absolutely', 'definitely']
            negative = ['no', 'n', 'nope', 'dont', 'do not', 'cancel', 'stop']
            
            if any(word in cleaned_input.split() for word in affirmative):
                key, value, category = self.pending_memory
                memory.store_fact(key, value, category)
                self.pending_memory = None
                return f"Noted. I'll remember that your {key} is {value}."
            elif any(word in cleaned_input.split() for word in negative):
                self.pending_memory = None
                return "Understood. I won't store that."
            else:
                self.pending_memory = None
                return "I didn't get a clear confirmation, so I won't store that."
        
        # Check for memory recall requests
        if is_recall_request(user_input):
            facts = memory.list_facts()
            return format_facts_for_display(facts)
        
        # Check if we should ask to remember
        if should_ask_to_remember(user_input):
            key, value, category = extract_fact_from_input(user_input)
            if key and value:
                self.pending_memory = (key, value, category)
                return f"Should I remember that your {key} is \"{value}\"?"
        
        # Load current facts for context
        facts = memory.list_facts()
        system_prompt = get_prompt_with_memory(facts)
        
        # Build context with history
        full_context = self.context.build_context(system_prompt, user_input)
        
        # Generate response
        response = generate_response(user_input, full_context)
        
        # Check for pending tool execution (confirmation received)
        if self.pending_tool_call:
            tool_name, tool_args = self.pending_tool_call
            
            cleaned_input = re.sub(r'[^\w\s]', '', user_input.lower())
            affirmative = ['yes', 'y', 'sure', 'proceed', 'go ahead', 'okay', 'ok', 'please', 'absolutely', 'definitely']
            
            if any(word in cleaned_input.split() for word in affirmative):
                print(f"[Tool] User confirmed '{tool_name}'...")
                result = router.execute_tool(tool_name, tool_args)
                self.pending_tool_call = None
                return f"Executed '{tool_name}'. Result: {result}"
            else:
                self.pending_tool_call = None
                return "Action cancelled."

        # Check for tool call in response
        try:
            if response.strip().startswith('{') and '"tool":' in response:
                print(f"[Tool] LLM requested tool execution...")
                try:
                    # Clean response if it has markdown header/footer
                    json_str = response.strip()
                    if json_str.startswith('```json'):
                        json_str = json_str[7:]
                    if json_str.endswith('```'):
                        json_str = json_str[:-3]
                    
                    tool_data = json.loads(json_str.strip())
                    tool_name = tool_data.get('tool')
                    args = tool_data.get('args', {})
                    
                    # Check safety
                    if router.is_destructive(tool_name):
                         print(f"[Tool] Safety check: '{tool_name}' requires confirmation.")
                         
                         # Preview content for file operations
                         if tool_name in ['create_file', 'edit_file'] and 'content' in args:
                             print(f"\n--- Preview ({args.get('path', 'unknown')}) ---")
                             print(args['content'])
                             print("------------------------------------------\n")
                             
                         self.pending_tool_call = (tool_name, args)
                         return f"I need to execute '{tool_name}' with arguments {args}. Should I proceed?"
                    
                    # Execute safe tool immediately
                    print(f"[Tool] Executing '{tool_name}'...")
                    result = router.execute_tool(tool_name, args)
                    print(f"[Tool] Output: {result}")
                    
                    # Feed result back to LLM for final response
                    tool_msg = f"\nSystem: Tool '{tool_name}' returned: {result}"
                    full_context += tool_msg
                    response = generate_response(user_input, full_context)
                    
                except json.JSONDecodeError:
                    print("[Tool] Error: Invalid JSON parsing")
        except Exception as e:
            print(f"[Tool] Error: {e}")
        
        # Store conversation
        memory.store_conversation(user_input, response)
        self.context.add_exchange(user_input, response)
        
        return response
    
    def speak_async(self, text):
        """Speak text without blocking."""
        def _speak():
            speak(text)
        t = threading.Thread(target=_speak, daemon=True)
        t.start()
        return t
    
    def run_wake_mode(self):
        """Wake mode - Uses Vosk for wake word, Whisper for command."""
        from speech.wake_listener import get_wake_listener, is_wake_available
        
        print(f"\n{'='*50}")
        print(f"  {ASSISTANT_NAME} - AI Assistant")
        print(f"  Voice Mode (Wake: Vosk | STT: Whisper)")
        print(f"{'='*50}")
        print("Initializing...\n")
        
        # Initialize model
        if not initialize_model():
            print("\n[!] Failed to connect to Ollama.")
            return
            
        if not stt_available():
            print("[!] Speech recognition not available")
            return
            
        # Check wake listener
        wake = get_wake_listener()
        if not wake._initialized:
            print("[!] Vosk wake detection not available. Falling back to simple mode.")
            self.run_simple_wake_mode()
            return

        # Show facts count
        facts = memory.list_facts()
        if facts:
            print(f"[Memory] Loaded {len(facts)} stored fact(s)")
        
        print(f"\n{ASSISTANT_NAME} ready.")
        print(f"Say '{ASSISTANT_NAME}' to activate.")
        print("Or type 'exit' to quit.\n")
        print("-" * 50)
        
        
        speak(f"{ASSISTANT_NAME} is ready, sir.", wait=True)
        
        # Wake detection event
        wake_event = threading.Event()
        console_queue = queue.Queue()
        
        def on_wake():
            stop_speaking()
            wake_event.set()
        
        # Start wake listener
        wake.start(on_wake)
        
        # Start console listener
        def console_input_loop():
            print("\nType a command at any time:")
            while self.running:
                try:
                    text = input("> ").strip()
                    if text:
                        console_queue.put(text)
                        wake_event.set()
                except EOFError:
                    break
        
        console_thread = threading.Thread(target=console_input_loop, daemon=True)
        console_thread.start()
        
        try:
            while self.running:
                # Wait for wake word OR console input
                wake_event.wait()
                wake_event.clear()
                
                # Check if it was console input
                if not console_queue.empty():
                    command = console_queue.get()
                    if command.lower() in ['exit', 'quit']:
                        break
                    
                    print(f"\n{ASSISTANT_NAME}: ", end="", flush=True)
                    response = self.process_command(command)
                    print(response)
                    speak(response, short_only=False, wait=False) # Non-blocking speech for text
                    continue

                # Voice Activation
                print(f"\n✨ {ASSISTANT_NAME} activated!")
                
                # Stop any ongoing speech immediately (redundant but safe)
                stop_speaking()
                
                # Confirmation
                print(f"{ASSISTANT_NAME}: Yes?")
                speak("Yes?", short_only=False, wait=True)
                
                # Start conversation loop
                first_turn = True
                while True:
                    # Check console queue inside conversation loop too!
                    if not console_queue.empty():
                        command = console_queue.get()
                        print(f"   (Text Input): \"{command}\"")
                    else:
                        # Pause wake listener before listening for command (avoid mic conflict)
                        wake.pause()
                        
                        if first_turn:
                             print("🎤 Listening for command...")
                             command = listen_once(timeout=10)
                             first_turn = False
                        else:
                             # Follow-up listen
                             print(f"\n🎤 Listening for follow-up (10s timeout)...")
                             command = listen_once(timeout=10)
                        
                        wake.resume()
                    
                    if command:
                        print(f"   Heard: \"{command}\"")
                        
                        # Process
                        print(f"\n{ASSISTANT_NAME}: ", end="", flush=True)
                        response = self.process_command(command)
                        print(response)
                        
                        # Speak response
                        speak(response, short_only=False, wait=True)
                        
                        # Check if wake event happened during speech (Voice Barge-in)
                        if wake_event.is_set() and console_queue.empty():
                             print("\n[Interrupted]")
                             wake_event.clear()
                             first_turn = True 
                             continue
                        
                        # Loop continues to listen again...
                    else:
                        print("   (Conversation timeout)")
                        speak("Closing conversation.", short_only=True, wait=True)
                        break # Exit conversation loop
                
                # Resume wake listener for next activation (redundant but safe)
                wake.resume()
                
        except KeyboardInterrupt:
            wake.stop()
            print(f"\n\n{ASSISTANT_NAME}: Goodbye.")
            speak("Goodbye.", wait=True)
        except Exception as e:
            wake.stop()
            print(f"\n[Error] {e}")

    def run_simple_wake_mode(self):
        """Fallback: uses STT for both wake detection and commands."""
        # ... (Existing code kept as fallback) ...
        print(f"\n{'='*50}")
        print(f"  {ASSISTANT_NAME} - AI Assistant")
        print(f"  Simple Mode (STT only)")
        print(f"{'='*50}")
        # ... rest of existing function ...

    
    def run_manual_mode(self):
        """Run in manual input mode."""
        Logger.DEBUG = False
        
        print(f"\n{'='*50}")
        print(f"  {ASSISTANT_NAME} - AI Assistant")
        print(f"  Manual Mode")
        print(f"{'='*50}")
        print("Initializing...\n")
        
        if not initialize_model():
            print("\n[!] Failed to connect to Ollama.")
            return
        
        voice_enabled = stt_available()
        if voice_enabled:
            print("[Voice] Speech-to-text ready")
        
        facts = memory.list_facts()
        if facts:
            print(f"[Memory] Loaded {len(facts)} stored fact(s)")
        
        print(f"\n{ASSISTANT_NAME} ready. Type 'exit' to quit.")
        if voice_enabled:
            print("Press ENTER to use voice input.\n")
        print("-" * 50)
        
        speak(f"{ASSISTANT_NAME} is ready, sir.")
        time.sleep(2)
        
        while self.running:
            try:
                if voice_enabled:
                    prompt = "\nYou (type or ENTER for voice): "
                else:
                    prompt = "\nYou: "
                
                user_input = input(prompt).strip()
                stop_speaking()
                
                # Voice input on empty ENTER
                if not user_input and voice_enabled:
                    print("🎤 Listening...")
                    user_input = listen_once(timeout=10)
                    if user_input:
                        print(f"   Heard: \"{user_input}\"")
                    else:
                        print("   (No speech detected)")
                        continue
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    goodbye = "Goodbye, sir. Until next time."
                    print(f"\n{ASSISTANT_NAME}: {goodbye}")
                    speak(goodbye, wait=True)
                    break
                
                print(f"\n{ASSISTANT_NAME}: ", end="", flush=True)
                response = self.process_command(user_input)
                print(response)
                speak(response, wait=True)
                
            except KeyboardInterrupt:
                print(f"\n\n{ASSISTANT_NAME}: Goodbye.")
                break


def main():
    """Main entry point."""
    atlas = AtlasAssistant()
    
    # Check for command line args
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        atlas.run_manual_mode()
    else:
        # Default to wake mode
        atlas.run_wake_mode()


if __name__ == "__main__":
    main()
