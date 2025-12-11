# ============================================================================
# Filename: BASE/tools/internal/voice/tts_tool.py
# ============================================================================
"""
Unified TTS Tool - Backend-agnostic orchestrator for text-to-speech

This tool manages TTS operations regardless of which backend is used.
It handles threading, interruption, and provides a consistent interface
to the rest of the system.

The backend (XTTS, pyttsx3, etc.) is injected during initialization.
"""
import threading
from typing import Optional, Dict
from BASE.handlers.tts_interface import TTSInterface
from BASE.core.logger import Logger


class TTSTool:
    """
    Unified TTS orchestrator with swappable backends
    
    Responsibilities:
    - Manage speech state (is_speaking)
    - Handle thread safety (locks)
    - Coordinate interruptions (stop_event)
    - Provide consistent logging
    - Delegate actual speech to backend
    
    Does NOT:
    - Know about backend implementation details
    - Handle audio generation directly
    - Manage device selection
    """
    
    def __init__(self, backend: TTSInterface, logger: Optional[Logger] = None):
        """
        Initialize TTS tool with a backend
        
        Args:
            backend: TTS backend implementing TTSInterface
            logger: Optional logger for output (creates default if None)
        """
        self.backend = backend
        self.logger = logger or Logger(name="TTSTool")
        
        # Thread safety
        self._is_speaking = False
        self._speech_lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Log initialization
        if self.backend.is_available():
            info = self.backend.get_voice_info()
            self.logger.speech(f"TTS initialized: {info.get('name', 'Unknown')} ({info.get('type', 'Unknown')})")
        else:
            self.logger.warning("TTS backend initialized but not available")
    
    def is_available(self) -> bool:
        """
        Check if TTS is ready to use
        
        Returns:
            bool: True if backend is available
        """
        return self.backend.is_available()
    
    def speak(self, text: str, stream: bool = True) -> str:
        """
        Speak text using the configured backend
        
        This method handles:
        - Input validation
        - Stopping previous speech
        - Thread-safe state management
        - Error handling and logging
        - Passing control to backend
        
        Args:
            text: Text to speak
            stream: Whether to stream audio (if backend supports it)
            
        Returns:
            str: "Speech completed", "Interrupted", or error message
        """
        # Validate input
        if not text or not text.strip():
            self.logger.warning("Attempted to speak empty text")
            return "No text to speak"
        
        if not self.is_available():
            self.logger.error("TTS not available")
            return "TTS not available"
        
        # Stop any current speech
        with self._speech_lock:
            if self._is_speaking:
                self.logger.speech("Stopping previous speech for new text")
                self._stop_event.set()
                # Brief wait for stop to take effect
                import time
                time.sleep(0.1)
            
            # Mark as speaking and reset stop event
            self._is_speaking = True
            self._stop_event.clear()
        
        # Delegate to backend
        try:
            self.logger.speech(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Backend receives stop_event to respect interruptions
            result = self.backend.speak(text, stream, stop_event=self._stop_event)
            
            # Log result
            if "completed" in result.lower():
                self.logger.speech("[SUCCESS] Speech completed")
            elif "interrupted" in result.lower():
                self.logger.speech("[WARNING] Speech interrupted")
            elif "error" in result.lower():
                self.logger.error(f"TTS error: {result}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"TTS exception: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
        
        finally:
            # Always release lock and reset state
            with self._speech_lock:
                self._is_speaking = False
                self._stop_event.clear()
    
    def stop(self):
        """
        Stop any currently playing speech
        
        Thread-safe and safe to call even if nothing is playing
        """
        with self._speech_lock:
            if self._is_speaking:
                self.logger.speech("Stopping speech")
                self._stop_event.set()
                self.backend.stop()
                self._is_speaking = False
            else:
                self.logger.speech("Stop called but nothing playing")
    
    def get_voice_info(self) -> Dict:
        """
        Get information about current voice configuration
        
        Returns:
            Dict with voice details from backend
        """
        return self.backend.get_voice_info()
    
    def get_status(self) -> Dict:
        """
        Get current TTS status
        
        Returns:
            Dict with status information
        """
        return {
            'available': self.is_available(),
            'speaking': self._is_speaking,
            'backend': self.backend.get_voice_info().get('type', 'Unknown')
        }