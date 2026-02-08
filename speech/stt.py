import os
import time
import wave
import tempfile
import struct
import math
import queue

try:
    import sounddevice as sd
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"[STT Warning] Could not import: {e}")

SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
CHANNELS = 1
DTYPE = 'int16'


class FasterWhisperSTT:
    """STT engine using Faster-Whisper."""
    
    def __init__(self):
        self.model = None
        self.model_size = "base.en"
        self.device = "cpu"
        self.compute_type = "int8"
        self._initialized = False
        
    def _initialize(self):
        """Initialize Whisper model."""
        if not WHISPER_AVAILABLE:
            print("[STT Error] Faster-Whisper not available")
            return
        
        print(f"[STT] Loading Faster-Whisper model '{self.model_size}' on {self.device}...")
        try:
            self.model = WhisperModel(
                self.model_size, 
                device=self.device, 
                compute_type=self.compute_type,
                cpu_threads=4
            )
            self._initialized = True
            print("[STT] Model loaded successfully")
        except Exception as e:
            print(f"[STT Error] Failed to load model: {e}")

    def is_speech(self, data, threshold=1000):
        """Simple energy-based speech detection."""
        count = len(data) / 2
        format = "%dh" % (count)
        shorts = struct.unpack(format, data)
        sum_squares = 0.0
        for sample in shorts:
            sum_squares += sample * sample
        
        rms = math.sqrt(sum_squares / count)
        return rms > threshold

    def listen_once(self, timeout=10, silence_timeout=2.0):
        """Record audio and transcribe."""
        if not self._initialized:
            self._initialize()
            if not self._initialized:
                return ""
        
        q = queue.Queue()
        
        def callback(indata, frames, time, status):
            q.put(bytes(indata))
        
        recorded_frames = []
        silence_start = None
        has_speech = False
        start_time = time.time()
        
        print("   (Recording...)")
        
        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE, 
                blocksize=BLOCK_SIZE, 
                dtype=DTYPE, 
                channels=CHANNELS, 
                callback=callback
            ):
                while True:
                    if time.time() - start_time > timeout:
                        break
                        
                    try:
                        data = q.get(timeout=0.1)
                        recorded_frames.append(data)
                        
                        if self.is_speech(data):
                            if not has_speech:
                                has_speech = True
                            silence_start = None
                        else:
                            if has_speech:
                                if silence_start is None:
                                    silence_start = time.time()
                                elif time.time() - silence_start > silence_timeout:
                                    break
                                    
                    except queue.Empty:
                        pass
                        
        except Exception as e:
            print(f"[STT Rec Error] {e}")
            return ""
            
        if not recorded_frames or not has_speech:
            return ""
            
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_filename = f.name
            
        try:
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)

            segments, info = self.model.transcribe(
                temp_filename, 
                beam_size=5,
                language="en",
                vad_filter=True
            )
            
            text = " ".join([segment.text for segment in segments]).strip()
            
            if not text or len(text) < 2:
                return ""
                
            ignored_phrases = [
                "subtitle", "subtitles", 
                "thank you", "thanks for watching", 
                "copyright", "all rights reserved"
            ]
            
            if any(phrase in text.lower() for phrase in ignored_phrases):
                print(f"[STT Filtered] Ignored noise: '{text}'")
                return ""
                
            return text
            
        except Exception as e:
            print(f"[STT Transcribe Error] {e}")
            return ""
            
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


_stt = None


def get_stt():
    """Get STT engine instance."""
    global _stt
    if _stt is None:
        _stt = FasterWhisperSTT()
    return _stt


def listen_once(timeout=10):
    """Listen for speech and return text."""
    stt = get_stt()
    return stt.listen_once(timeout=timeout)


def is_available():
    """Check if STT is available."""
    return WHISPER_AVAILABLE
