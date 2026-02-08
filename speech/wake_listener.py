import os
import json
import queue
import threading
import time

try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk', 'vosk-model-small-en-us-0.15')

SAMPLE_RATE = 16000
BLOCK_SIZE = 4000

WAKE_WORDS = ["atlas", "at less", "at lass", "at last", "address"]


class WakeListener:
    """Continuous wake word listener running in background thread."""
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_running = False
        self.is_paused = False
        self.listener_thread = None
        self.stream = None
        self.callback = None
        self._initialized = False
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Vosk model for wake detection."""
        if not VOSK_AVAILABLE:
            print("[Wake] Vosk not available")
            return
        
        if not os.path.exists(MODEL_PATH):
            print(f"[Wake] Model not found")
            return
        
        try:
            self.model = Model(MODEL_PATH)
            self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
            self._initialized = True
        except Exception as e:
            print(f"[Wake Error] {e}")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if not self.is_paused:
            self.audio_queue.put(bytes(indata))
    
    def _contains_wake_word(self, text):
        """Check if text contains wake word."""
        text_lower = text.lower()
        for wake_word in WAKE_WORDS:
            if wake_word in text_lower:
                return True
        return False
    
    def _close_stream(self):
        """Close the audio stream if open."""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
    
    def _listener_loop(self):
        """Main listener loop running in background thread."""
        print(f"\n🎧 Listening for 'Atlas'...")
        
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
                
            try:
                self.stream = sd.RawInputStream(
                    samplerate=SAMPLE_RATE,
                    blocksize=BLOCK_SIZE,
                    dtype='int16',
                    channels=1,
                    callback=self._audio_callback
                )
                self.stream.start()
                
                while self.is_running:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                        
                        if self.is_paused:
                            break
                        
                        if self.recognizer.AcceptWaveform(data):
                            result = json.loads(self.recognizer.Result())
                            text = result.get('text', '')
                            
                            if text:
                                if self._contains_wake_word(text):
                                    self._close_stream()
                                    self._on_wake_detected()
                                    break
                        else:
                            partial = json.loads(self.recognizer.PartialResult())
                            partial_text = partial.get('partial', '')
                            
                            if partial_text and self._contains_wake_word(partial_text):
                                self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
                                self._close_stream()
                                self._on_wake_detected()
                                break
                        
                        time.sleep(0.05)
                        
                    except queue.Empty:
                        continue
                    except Exception as e:
                        if self.is_running:
                            print(f"[Wake Error] {e}")
                        break
                
                self._close_stream()
                        
            except Exception as e:
                if self.is_running:
                    print(f"[Wake] Mic error: {e}")
                    time.sleep(2)
    
    def _on_wake_detected(self):
        """Called when wake word is detected."""
        if self.callback:
            self.is_paused = True
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            self.callback()
    
    def start(self, callback):
        """Start the wake word listener."""
        if not self._initialized:
            print("[Wake] Not initialized")
            return False
        
        if self.is_running:
            return True
        
        self.callback = callback
        self.is_running = True
        self.is_paused = False
        
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
        
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        
        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.listener_thread.start()
        return True
    
    def stop(self):
        """Stop the wake word listener."""
        self.is_running = False
        self._close_stream()
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
            self.listener_thread = None
    
    def pause(self):
        """Pause listening."""
        self.is_paused = True
        self._close_stream()
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                break
    
    def resume(self):
        """Resume listening after command processing."""
        self.is_paused = False
        if self.model:
            self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        print(f"\n🎧 Listening for 'Atlas'...")


_wake_listener = None


def get_wake_listener():
    """Get or create wake listener instance."""
    global _wake_listener
    if _wake_listener is None:
        _wake_listener = WakeListener()
    return _wake_listener


def start_wake_listener(callback):
    """Start listening for wake word."""
    listener = get_wake_listener()
    return listener.start(callback)


def stop_wake_listener():
    """Stop wake word listener."""
    listener = get_wake_listener()
    listener.stop()


def pause_wake_listener():
    """Pause wake word listener."""
    listener = get_wake_listener()
    listener.pause()


def resume_wake_listener():
    """Resume wake word listener."""
    listener = get_wake_listener()
    listener.resume()


def is_wake_available():
    """Check if wake listener is available."""
    listener = get_wake_listener()
    return listener._initialized
