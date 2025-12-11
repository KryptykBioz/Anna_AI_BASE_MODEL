# File: BASE/tools/internal/voice/xtts_backend.py
# FIXED: Import controls directly for live volume updates

from typing import Dict, List, Optional
import threading
from pathlib import Path
from BASE.handlers.tts_interface import TTSInterface


class XTTSBackend(TTSInterface):
    """
    XTTS custom voice cloning backend
    FIXED: Reads volume directly from personality.controls for live updates
    """
    
    __slots__ = ('voice_sample_path', 'language', 'speed', '_is_available', '_init_error')
    
    def __init__(self, voice_sample_path: str, language: str = 'en', 
                 speed: float = 1.0, controls_module=None):
        """
        Initialize XTTS backend
        
        Args:
            controls_module: Ignored - we import directly for live updates
        """
        self.voice_sample_path = Path(voice_sample_path)
        self.language = language
        self.speed = speed
        self._is_available = False
        self._init_error = None
        
        
        print("XTTS BACKEND INITIALIZATION")
        
        
        # Step 1: Validate voice sample exists
        print(f"[1/5] Checking voice sample: {voice_sample_path}")
        if not self.voice_sample_path.exists():
            self._init_error = f"Voice sample not found: {voice_sample_path}"
            print(f"[FAILED] {self._init_error}")
            return
        print(f"[SUCCESS] Voice sample exists")
        
        # Step 2: Validate audio file is readable
        print(f"[2/5] Validating audio file...")
        try:
            import soundfile as sf
            data, sr = sf.read(str(self.voice_sample_path))
            duration = len(data) / sr
            print(f"[SUCCESS] Audio valid: {duration:.1f}s, {sr}Hz")
        except Exception as e:
            self._init_error = f"Invalid audio file: {e}"
            print(f"[FAILED] {self._init_error}")
            return
        
        # Step 3: Verify PyTorch is available
        print(f"[3/5] Checking PyTorch availability...")
        try:
            import torch
            print(f"[SUCCESS] PyTorch {torch.__version__}")
            
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"[SUCCESS] CUDA available: {gpu_name} ({vram:.1f} GB VRAM)")
            else:
                print(f"[WARNING]️ CUDA not available - will use CPU (slower)")
        except ImportError as e:
            self._init_error = f"PyTorch not found: {e}"
            print(f"[FAILED] {self._init_error}")
            print("   Install with: pip install torch torchvision torchaudio")
            return
        
        # Step 4: Import XTTS dependencies
        print(f"[4/5] Loading XTTS dependencies...")
        try:
            from BASE.tools.internal.voice.text_to_custom_voice import (
                load_embeddings_cache, init_tts, get_best_device
            )
            print(f"[SUCCESS] XTTS modules imported")
        except ImportError as e:
            self._init_error = f"Failed to import XTTS modules: {e}"
            print(f"[FAILED] {self._init_error}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 5: Initialize XTTS model
        print(f"[5/5] Initializing XTTS model...")
        try:
            device = get_best_device()
            device_str = device if isinstance(device, str) else str(device)
            print(f"  Using device: {device_str.upper()}")
            
            load_embeddings_cache()
            print(f"  [SUCCESS] Embeddings cache loaded")
            
            print(f"  Loading XTTS v2 model... (this may take 10-30 seconds)")
            tts_model = init_tts()
            
            if tts_model:
                print(f"[SUCCESS] XTTS model initialized successfully")
                self._is_available = True
            else:
                self._init_error = "XTTS model initialization returned None"
                print(f"[FAILED] {self._init_error}")
        
        except Exception as e:
            self._init_error = f"XTTS initialization error: {e}"
            print(f"[FAILED] {self._init_error}")
            import traceback
            traceback.print_exc()
        
        
        if self._is_available:
            print("XTTS BACKEND READY")
            print("Volume control: Reading directly from personality.controls module")
        else:
            print(f"XTTS BACKEND FAILED: {self._init_error}")
        

    def get_voice_info(self) -> Dict:
        """Get XTTS voice information with diagnostics"""
        info = {
            'name': 'Custom Voice (XTTS)',
            'type': 'XTTS',
            'language': self.language,
            'sample': str(self.voice_sample_path),
            'speed': self.speed
        }
        
        if self.is_available():
            info['status'] = 'available'
            
            # Add device info
            try:
                from BASE.tools.internal.voice.text_to_custom_voice import (
                    get_best_device, _embeddings_cache, _audio_cache
                )
                device = get_best_device()
                info['device'] = device if isinstance(device, str) else str(device)
                info['embeddings_cached'] = len(_embeddings_cache)
                info['audio_clips_cached'] = len(_audio_cache)
            except Exception as e:
                info['cache_error'] = str(e)
            
            # FIXED: Read volume directly from module
            import personality.controls as controls
            volume = controls.VOICE_VOLUME
            info['volume'] = volume
            info['volume_percent'] = f"{int(volume * 100)}%"
        else:
            info['status'] = 'unavailable'
            info['error'] = self._init_error or 'Unknown initialization error'
        
        return info
    
    def is_available(self) -> bool:
        """Check if XTTS backend is available"""
        return self._is_available
    
    def speak(self, text: str, stream: bool = True, 
              stop_event: Optional[threading.Event] = None) -> str:
        """
        Speak using XTTS voice cloning with volume control
        
        FIXED: Reads volume directly from personality.controls module each time
        """
        if not self.is_available():
            return f"Error: XTTS not available - {self._init_error}"
        
        try:
            from BASE.tools.internal.voice.text_to_custom_voice import (
                speak_stream, speak_custom_voice
            )
            
            # CRITICAL FIX: Import controls module directly to get LIVE value
            import personality.controls as controls
            volume = controls.VOICE_VOLUME  # Read directly from module
            
            print(f"\n[XTTS] Speaking with volume: {volume:.2f} ({int(volume * 100)}%)")
            
            if stream:
                result = speak_stream(
                    text=text,
                    ref_audio=str(self.voice_sample_path),
                    language=self.language,
                    speed=self.speed,
                    stop_flag=stop_event,
                    volume=volume
                )
            else:
                result = speak_custom_voice(
                    text=text,
                    ref_audio=str(self.voice_sample_path),
                    language=self.language,
                    speed=self.speed,
                    use_cache=True,
                    fallback=True,
                    stop_flag=stop_event,
                    volume=volume
                )
            
            # Normalize result
            if result == "[SUCCESS]":
                return "Speech completed"
            elif result == "Interrupted":
                return "Interrupted"
            elif result.startswith("Error"):
                return result
            else:
                return "Speech completed"
        
        except Exception as e:
            print(f"[XTTSBackend] Exception during speech: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
    
    def stop(self):
        """Stop XTTS speech playback"""
        try:
            import sounddevice as sd
            sd.stop()
        except Exception as e:
            print(f"[XTTSBackend] Error stopping: {e}")
    
    def precache_phrases(self, phrases: List[str]):
        """Pre-cache common phrases for instant playback"""
        if not self.is_available():
            print("[XTTSBackend] Cannot precache - backend unavailable")
            return
        
        from BASE.tools.internal.voice.text_to_custom_voice import preload_common_phrases
        
        print(f"[XTTSBackend] Pre-caching {len(phrases)} phrases")
        preload_common_phrases(str(self.voice_sample_path), phrases)
        print(f"[XTTSBackend] Pre-caching complete")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            from BASE.tools.internal.voice.text_to_custom_voice import (
                _embeddings_cache, _audio_cache
            )
            
            return {
                'embeddings_cached': len(_embeddings_cache),
                'audio_clips_cached': len(_audio_cache),
                'status': 'active'
            }
        except:
            return {'status': 'unavailable'}