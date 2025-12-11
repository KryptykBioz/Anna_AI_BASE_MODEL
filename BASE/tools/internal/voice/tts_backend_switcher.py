# ============================================================================
# Filename: BASE/tools/internal/voice/tts_backend_switcher.py
# FIXED: Correct import path for XTTSBackend
# ============================================================================
"""
Runtime TTS Backend Switcher

Allows switching between XTTS and pyttsx3 backends at runtime
when USE_CUSTOM_VOICE control is toggled in GUI

FIXED: Import path corrected from f5tts_xtts_backend to xtts_backend
"""
from typing import Optional
from pathlib import Path
from BASE.tools.internal.voice.tts_tool import TTSTool
from BASE.tools.internal.voice.xtts_backend import XTTSBackend  # FIXED: Correct import path
from BASE.tools.internal.voice.pyttsx3_backend import Pyttsx3Backend
from BASE.handlers.tts_interface import TTSInterface
from BASE.core.logger import Logger


class TTSBackendSwitcher:
    """
    Manages runtime switching between TTS backends
    
    Used by GUI when USE_CUSTOM_VOICE is toggled to
    switch between XTTS and pyttsx3 without restart
    """
    
    def __init__(self, ai_core, logger: Optional[Logger] = None):
        """
        Initialize backend switcher
        
        Args:
            ai_core: AI Core instance to inject new backend into
            logger: Optional logger
        """
        self.ai_core = ai_core
        self.logger = logger or Logger(name="TTSSwitcher")
        self.current_backend_type = None
        
        # CRITICAL: Store reference to controls module
        self.controls_module = None
        if hasattr(ai_core, 'controls'):
            self.controls_module = ai_core.controls
            self.logger.speech(f"Controls module captured: {id(self.controls_module)}")
        else:
            self.logger.warning("AI Core has no controls attribute")
        
        # Detect current backend at initialization
        if hasattr(ai_core, 'tts_tool') and ai_core.tts_tool:
            info = ai_core.tts_tool.get_voice_info()
            self.current_backend_type = info.get('type', None)
            self.logger.speech(f"Current TTS backend: {self.current_backend_type}")
    
    def switch_backend(self, use_custom_voice: bool) -> bool:
        """
        Switch TTS backend based on USE_CUSTOM_VOICE setting
        
        Args:
            use_custom_voice: True for XTTS, False for pyttsx3
            
        Returns:
            bool: True if switch successful, False otherwise
        """
        try:
            # Determine target backend
            target_type = "XTTS" if use_custom_voice else "pyttsx3"
            
            # Check if already using correct backend
            if self.current_backend_type == target_type:
                self.logger.speech(f"Already using {target_type}")
                return True
            
            self.logger.speech(f"Switching TTS backend: {self.current_backend_type} → {target_type}")
            
            # Stop current TTS if speaking
            if hasattr(self.ai_core, 'tts_tool') and self.ai_core.tts_tool:
                try:
                    self.ai_core.tts_tool.stop()
                except Exception as e:
                    self.logger.warning(f"Error stopping current TTS: {e}")
            
            # Create new backend with error handling
            if use_custom_voice:
                backend = self._create_xtts_backend()
                if backend is None:
                    self.logger.error("[FAILED] XTTS backend creation failed")
                    return False
            else:
                backend = self._create_pyttsx3_backend()
                if backend is None:
                    self.logger.error("[FAILED] pyttsx3 backend creation failed")
                    return False
            
            # Verify backend is available
            if not backend.is_available():
                self.logger.error(f"[FAILED] {target_type} backend not available after creation")
                return False
            
            # Create new TTS tool with new backend
            new_tts_tool = TTSTool(backend, self.logger)
            
            # Verify tool is available
            if not new_tts_tool.is_available():
                self.logger.error(f"[FAILED] TTSTool not available with {target_type} backend")
                return False
            
            # Inject into AI Core
            self.ai_core.setup_tts_tool(new_tts_tool)
            
            # Update current backend type
            self.current_backend_type = target_type
            
            # Log success with details
            info = new_tts_tool.get_voice_info()
            # self.logger.speech(f"[SUCCESS] Switched to {info.get('name')} ({info.get('type')})")
            
            # Log volume info
            if 'volume_percent' in info:
                self.logger.speech(f"  Volume: {info['volume_percent']}")
            
            # Additional device info for XTTS
            if use_custom_voice and info.get('device'):
                self.logger.speech(f"  Device: {info['device']}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"[FAILED] Failed to switch TTS backend: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_xtts_backend(self) -> Optional[XTTSBackend]:
        """
        Create XTTS backend with default settings and error handling
        
        Returns:
            XTTSBackend instance or None if creation failed
        """
        try:
            from personality.bot_info import agentname
            
            # Try voice sample (check multiple extensions)
            voice_extensions = ['.wav', '.mp3', '.flac']
            voice_path = None
            
            for ext in voice_extensions:
                test_path = f"./personality/voice/{agentname}_voice_sample{ext}"
                if Path(test_path).exists():
                    voice_path = test_path
                    break
            
            if not voice_path:
                self.logger.error(f"[FAILED] Voice sample not found for {agentname}")
                self.logger.error(f"   Checked: {', '.join([f'{agentname}_voice_sample{ext}' for ext in voice_extensions])}")
                return None
            
            self.logger.speech(f"Loading voice sample: {Path(voice_path).name}")
            
            # FIXED: Pass controls_module for volume control
            backend = XTTSBackend(
                voice_sample_path=voice_path,
                language='en',
                speed=1.0,
                controls_module=self.controls_module  # [SUCCESS] Pass controls
            )
            
            # Verify backend initialized correctly
            if not backend.is_available():
                self.logger.error("[FAILED] XTTS backend failed availability check")
                return None
            
            # Skip pre-caching during runtime switching (too slow and distracting)
            # Embeddings are cached automatically on first use
            self.logger.speech("Voice embeddings will cache on first use")
            
            return backend
        
        except Exception as e:
            self.logger.error(f"[FAILED] Error creating XTTS backend: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_pyttsx3_backend(self) -> Optional[Pyttsx3Backend]:
        """
        Create pyttsx3 backend with controls module for volume
        
        FIXED: Now passes controls_module to backend
        
        Returns:
            Pyttsx3Backend instance or None if creation failed
        """
        try:
            # CRITICAL FIX: Pass controls_module for volume control
            backend = Pyttsx3Backend(controls_module=self.controls_module)
            
            if not backend.is_available():
                self.logger.error("[FAILED] pyttsx3 backend failed availability check")
                return None
            
            # Log current volume setting
            if self.controls_module:
                volume = getattr(self.controls_module, 'VOICE_VOLUME', 1.0)
                self.logger.speech(f"pyttsx3 backend created with volume: {int(volume * 100)}%")
            
            return backend
        
        except Exception as e:
            self.logger.error(f"[FAILED] Error creating pyttsx3 backend: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_current_backend_type(self) -> Optional[str]:
        """
        Get current backend type
        
        Returns:
            "XTTS", "pyttsx3", or None
        """
        return self.current_backend_type