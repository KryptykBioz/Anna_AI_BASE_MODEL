# ============================================================================
# FILE: BASE/tools/internal/voice/pyttsx3_backend.py
# FIXED: Import controls module directly to ensure live updates
# ============================================================================

"""
System Voice (pyttsx3) TTS Backend - FIXED VOLUME CONTROL

Key Fix: Import personality.controls directly rather than storing reference
This ensures we always read the LIVE module-level variable that the GUI updates
"""
from typing import Dict, Optional
import threading
from BASE.handlers.tts_interface import TTSInterface
from BASE.tools.internal.voice.voice_utils import (
    clean_text_for_tts,
    find_vb_cable_device
)


class Pyttsx3Backend(TTSInterface):
    """
    System voice TTS backend using pyttsx3
    
    FIXED: Imports controls module directly to read live VOICE_VOLUME value
    """
    
    def __init__(self, controls_module=None):
        """
        Initialize pyttsx3 backend
        
        Args:
            controls_module: Ignored - we import directly for live updates
        """
        # DON'T store controls_module reference - import directly instead
        self._pyttsx3_available = self._test_availability()
        
        
        print("PYTTSX3 BACKEND INITIALIZATION")
        
        print("Volume control: Reading directly from personality.controls module")
        print("This ensures GUI slider changes apply immediately")
        
    
    def _test_availability(self) -> bool:
        """Test if pyttsx3 is available and working"""
        try:
            import pyttsx3
            test_engine = pyttsx3.init()
            test_engine.stop()
            del test_engine
            return True
        except Exception as e:
            print(f"[Pyttsx3Backend] Not available: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if pyttsx3 is available"""
        return self._pyttsx3_available
    
    def speak(self, text: str, stream: bool = True, stop_event: Optional[threading.Event] = None) -> str:
        """
        Speak using system voice with volume control
        
        FIXED: Reads volume directly from personality.controls module each time
        
        Args:
            text: Text to speak
            stream: Ignored for pyttsx3 (no streaming support)
            stop_event: Event to check for interruption
            
        Returns:
            "Speech completed", "Interrupted", or "Error: <message>"
        """
        if not self.is_available():
            return "Error: pyttsx3 not available"
        
        # Clean text
        text = clean_text_for_tts(text)
        if not text:
            return "Error: No text after cleaning"
        
        # CRITICAL FIX: Import controls module directly to get LIVE value
        import personality.controls as controls
        volume = controls.VOICE_VOLUME  # Read directly from module
        
        print(f"\n[Pyttsx3] Speaking with volume: {volume:.2f} ({int(volume * 100)}%)")
        
        try:
            # Import implementation function
            from BASE.tools.internal.voice.text_to_system_voice import speak_system_voice
            
            # Create fresh engine for this call (pyttsx3 requirement)
            import pyttsx3
            fresh_engine = pyttsx3.init()
            
            # Speak with interruption support and volume
            result = speak_system_voice(
                text=text,
                engine=fresh_engine,
                stop_event=stop_event,
                volume=volume
            )
            
            # Cleanup engine (don't call stop(), just delete)
            del fresh_engine
            
            # Normalize result
            if "completed" in result.lower() or "success" in result.lower():
                return "Speech completed"
            elif "interrupted" in result.lower():
                return "Interrupted"
            else:
                return result
        
        except Exception as e:
            import traceback
            print(f"\n[Pyttsx3Backend] EXCEPTION:")
            traceback.print_exc()
            return f"Error: {e}"
    
    def stop(self):
        """Stop system voice playback"""
        try:
            import sounddevice as sd
            sd.stop()
        except Exception as e:
            print(f"[Pyttsx3Backend] Error stopping: {e}")
    
    def get_voice_info(self) -> Dict:
        """Get system voice information with volume info"""
        if not self.is_available():
            return {
                'name': 'System Voice',
                'type': 'pyttsx3',
                'status': 'unavailable'
            }
        
        try:
            import pyttsx3
            temp_engine = pyttsx3.init()
            voices = temp_engine.getProperty('voices')
            current = temp_engine.getProperty('voice')
            temp_engine.stop()
            del temp_engine
            
            # FIXED: Read volume directly from module
            import personality.controls as controls
            volume = controls.VOICE_VOLUME
            
            return {
                'name': 'System Voice',
                'type': 'pyttsx3',
                'status': 'available',
                'current_voice': current,
                'available_voices': len(voices),
                'volume': volume,
                'volume_percent': f"{int(volume * 100)}%"
            }
        except Exception as e:
            return {
                'name': 'System Voice',
                'type': 'pyttsx3',
                'status': 'error',
                'error': str(e)
            }