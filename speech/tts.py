import pyttsx3
import threading
import queue
import re
import time


class TTSEngine:
    """Thread-safe text-to-speech engine using a dedicated worker thread."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.engine = None
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        self._stop_current = False
        self._initialized = False
        
        self._start_worker()
    
    def _start_worker(self):
        """Start the TTS worker thread."""
        try:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            self._initialized = True
        except Exception as e:
            pass

    def _worker_loop(self):
        """Worker thread that processes speech requests."""
        try:
            while self.is_running:
                try:
                    if self.engine:
                        del self.engine
                    self.engine = pyttsx3.init()
                    self._configure_voice()
                except Exception:
                    pass
                try:
                    text = self.speech_queue.get(timeout=0.5)
                    
                    if text is None:
                        break
                    
                    if self._stop_current:
                        self._stop_current = False
                        self.speech_queue.task_done()
                        continue
                    
                    time.sleep(0.2)
                    safe_text = ". " + text
                    
                    if self.engine:
                        self.engine.say(safe_text)
                        self.engine.runAndWait()

                    self.speech_queue.task_done()

                except queue.Empty:
                    continue
                except Exception:
                    try:
                        if self.engine:
                            self.engine.endLoop()
                    except:
                        pass
                    try:
                        self.speech_queue.task_done()
                    except ValueError:
                        pass
                    
        except Exception:
            pass
        finally:
            self._initialized = False
            self.is_running = False

    def wait(self):
        """Wait for TTS to finish speaking."""
        self.speech_queue.join()

    def _configure_voice(self):
        """Configure voice settings."""
        if not self.engine:
            return
        
        try:
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 1.0)
            
            voices = self.engine.getProperty('voices')
            for voice in voices:
                name_lower = voice.name.lower()
                if 'david' in name_lower or ('male' in name_lower and 'female' not in name_lower):
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception:
            pass

    def _clean_text(self, text):
        """Clean text for speaking."""
        text = re.sub(r'```[\s\S]*?```', ' Code block. ', text)
        text = re.sub(r'`[^`]+`', ' Code snippet. ', text)
        text = re.sub(r'[a-zA-Z]:\\[\w\\]+|\/[\w\/]+', ' file path ', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _get_short_text(self, text, max_sentences=2):
        """Extract first 1-2 sentences for speaking."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        short = ' '.join(sentences[:max_sentences])
        
        if len(short) > 300:
            short = short[:300] + '...'
        
        if not short:
            return text[:100]
            
        return short.strip()
    
    def speak(self, text, short_only=True):
        """Queue text for speaking."""
        if self.worker_thread and not self.worker_thread.is_alive():
            self._initialized = False
            self._start_worker()
            
        if not self._initialized:
             self._start_worker()
             
        if not text:
            return
        
        stripped = text.strip()
        if stripped.startswith('{') and '"tool"' in stripped:
            return
        
        cleaned_text = self._clean_text(text)
        speak_text = self._get_short_text(cleaned_text) if short_only else cleaned_text
        
        if speak_text:
            self._stop_current = False
            self.speech_queue.put(speak_text)

    def _clear_queue(self):
        """Clear the speech queue."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                break
    
    def stop_speaking(self):
        """Stop current speech immediately."""
        self._stop_current = True
        self._clear_queue()
           
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


_tts = None


def get_tts():
    """Get TTS engine instance."""
    global _tts
    if _tts is None:
        _tts = TTSEngine()
    return _tts


def speak(text, short_only=True, wait=False):
    """Speak text."""
    tts = get_tts()
    tts.speak(text, short_only)
    if wait:
        tts.wait()


def stop_speaking():
    """Stop speech."""
    tts = get_tts()
    tts.stop_speaking()
