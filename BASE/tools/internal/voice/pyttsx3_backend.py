# ============================================================================
# FILE: BASE/tools/internal/voice/pyttsx3_backend.py
# FIXED: Enhanced debug logging to diagnose system TTS issues
# ============================================================================

"""
System Voice (pyttsx3) TTS Backend - ENHANCED DIAGNOSTICS

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
        
        print("\n" + "="*70)
        print("PYTTSX3 BACKEND INITIALIZATION")
        print("="*70)
        
        if self._pyttsx3_available:
            print("[SUCCESS] pyttsx3 is available")
        else:
            print("[FAILED] pyttsx3 is NOT available")
            return
        
        print("Volume control: Reading directly from personality.controls module")
        print("This ensures GUI slider changes apply immediately")
        
        # Test volume reading
        try:
            import personality.controls as controls
            volume = controls.VOICE_VOLUME
            print(f"[SUCCESS] Successfully read VOICE_VOLUME: {volume:.2f} ({int(volume * 100)}%)")
        except Exception as e:
            print(f"[FAILED] Failed to read VOICE_VOLUME: {e}")
        
        print("="*70 + "\n")
    
    def _test_availability(self) -> bool:
        """Test if pyttsx3 is available and working"""
        try:
            import pyttsx3
            print("[Test] Creating test pyttsx3 engine...")
            test_engine = pyttsx3.init()
            print("[Test] Test engine created successfully")
            
            # Test getting voices
            voices = test_engine.getProperty('voices')
            print(f"[Test] Found {len(voices)} available voices")
            if voices:
                print(f"[Test] Default voice: {voices[0].name}")
            
            # Clean up - DO NOT call stop()
            del test_engine
            print("[Test] pyttsx3 test passed")
            return True
        except Exception as e:
            print(f"[Pyttsx3Backend] Not available: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n[Pyttsx3Backend] Reading volume from controls module...")
        try:
            import personality.controls as controls
            volume = controls.VOICE_VOLUME  # Read directly from module
            print(f"[Pyttsx3Backend] Successfully read volume: {volume:.2f} ({int(volume * 100)}%)")
        except Exception as e:
            print(f"[Pyttsx3Backend] ERROR reading volume: {e}")
            volume = 1.0  # Fallback
            print(f"[Pyttsx3Backend] Using fallback volume: {volume}")
        
        print(f"\n[Pyttsx3Backend] Speaking with volume: {volume:.2f} ({int(volume * 100)}%)")
        print(f"[Pyttsx3Backend] Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        try:
            # Import implementation function
            from BASE.tools.internal.voice.text_to_system_voice import speak_system_voice
            
            # Create fresh engine for this call (pyttsx3 requirement)
            print("[Pyttsx3Backend] Creating fresh pyttsx3 engine...")
            import pyttsx3
            fresh_engine = pyttsx3.init()
            print("[Pyttsx3Backend] Fresh engine created")
            
            # Speak with interruption support and volume
            print(f"[Pyttsx3Backend] Calling speak_system_voice with volume={volume:.2f}...")
            result = speak_system_voice(
                text=text,
                engine=fresh_engine,
                stop_event=stop_event,
                volume=volume
            )
            print(f"[Pyttsx3Backend] speak_system_voice returned: {result}")
            
            # Cleanup engine (don't call stop(), just delete)
            del fresh_engine
            print("[Pyttsx3Backend] Engine cleaned up")
            
            # Normalize result
            if "completed" in result.lower() or "success" in result.lower():
                print("[Pyttsx3Backend] Result: Speech completed successfully")
                return "Speech completed"
            elif "interrupted" in result.lower():
                print("[Pyttsx3Backend] Result: Speech was interrupted")
                return "Interrupted"
            else:
                print(f"[Pyttsx3Backend] Result: {result}")
                return result
        
        except Exception as e:
            print(f"\n[Pyttsx3Backend] EXCEPTION:")
            import traceback
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
            # Don't call stop() - just delete
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