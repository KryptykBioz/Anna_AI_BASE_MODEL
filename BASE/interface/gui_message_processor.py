# Filename: BASE/interface/gui_message_processor.py
"""
Message processing logic for the GUI - fully delegated to AI Core
FIXED: No user message saving here - handled by gui_chat_handler
FIXED: Empty messages trigger background checks without displaying empty responses
FIXED: TTS speech interruption and state management
"""

import threading
import asyncio
from pathlib import Path
from typing import Optional
from personality.bot_info import agentname, username
from BASE.core.logger import MessageType


class MessageProcessor:
    """Handles message routing between GUI and AI Core"""
    
    def __init__(self, ai_core, message_queue, speech_stop_flag, logger):
        self.ai_core = ai_core
        self.message_queue = message_queue
        self.speech_stop_flag = speech_stop_flag
        self.logger = logger
        self.speech_thread: Optional[threading.Thread] = None
        
        self._is_speaking = False
        self._speech_lock = threading.Lock()
        self._speech_stop_event = threading.Event()

        self.agentname = agentname
        self.username = username
        self.project_root = Path(__file__).parent.parent.parent

    def process_message(self, message: str):
        """
        Process user message - ONLY handles AI processing
        FIXED: User message already saved by gui_chat_handler before this is called
        FIXED: Empty messages (auto-prompts) don't display empty responses
        
        Args:
            message: User's message text (can be empty for auto-prompts)
        """
        try:
            # Detect if this is an empty auto-prompt
            is_auto_prompt = not message or not message.strip()
            
            if is_auto_prompt:
                self.logger.system("Processing auto-prompt (background check)")
            
            # Process message through AI Core
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response = loop.run_until_complete(
                    self.ai_core.process_user_message(
                        message=message if message else "",  # Ensure empty string not None
                        source="GUI"
                    )
                )
                
                if response and response.strip():
                    # Bot response already saved by AI Core
                    # Just display it (3-tuple format)
                    self.message_queue.put(("agent", self.agentname, response))
                    
                    # Handle TTS if enabled
                    import personality.controls as controls
                    if controls.AVATAR_SPEECH and len(response) < 1000:
                        self._play_tts(response)
                # else:
                #     # No response generated (normal for auto-prompts)
                #     if is_auto_prompt:
                #         self.logger.system("Auto-prompt processed (no proactive response needed)")
                #     else:
                #         self.logger.warning("No response generated for user message")
                    
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = f"Failed to process message: {str(e)}"
            self.message_queue.put(("error", "Error", error_msg))
            self.logger.error(error_msg)
            import traceback
            traceback.print_exc()
            
        finally:
            # Signal processing complete
            self.message_queue.put(("processing_complete", None, None))
        
    def _play_tts(self, text: str):
        """
        Play TTS using centralized AI Core tools
        FIXED: Proper interruption without race conditions
        
        Args:
            text: Text to speak
        """
        # CRITICAL FIX: Acquire lock BEFORE checking state
        with self._speech_lock:
            # Stop previous speech if running
            if self._is_speaking:
                self.logger.speech("New response - interrupting previous speech")
                
                # Signal stop to running thread
                self._speech_stop_event.set()
                
                # Set flag to false immediately so new thread can start
                self._is_speaking = False
            
            # Stop TTS tool outside lock to avoid deadlock
            if self.ai_core.tts_tool:
                try:
                    self.ai_core.tts_tool.stop()
                except Exception as e:
                    self.logger.warning(f"Error stopping previous TTS: {e}")
            
            # Wait for previous thread to finish (short timeout)
            old_thread = self.speech_thread
        
        # Wait outside the lock
        if old_thread and old_thread.is_alive():
            old_thread.join(timeout=1.0)
        
        # CRITICAL: Clear stop event BEFORE starting new thread
        self._speech_stop_event.clear()
        
        # Start new speech thread
        def speak_async():
            """Async wrapper for TTS"""
            # Set speaking flag IMMEDIATELY at thread start
            with self._speech_lock:
                self._is_speaking = True
            
            try:
                self.logger.speech(f"Starting TTS: {text[:50]}...")
                
                # Use AI Core's TTS tool directly
                if self.ai_core.tts_tool and self.ai_core.tts_tool.is_available():
                    result = self.ai_core.tts_tool.speak(text, stream=True)
                    
                    # Check if we were interrupted
                    if self._speech_stop_event.is_set():
                        self.logger.speech("Speech interrupted by newer response")
                    elif result == "Interrupted":
                        self.logger.speech("Speech interrupted by newer response")
                    elif "error" in result.lower():
                        self.logger.error(f"TTS error: {result}")
                    else:
                        self.logger.speech(f"[COMPLETE] Speech completed")
                else:
                    self.logger.warning("TTS tool not available")
                        
            except Exception as e:
                self.logger.error(f"Speech error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # CRITICAL: Always clear flags in finally block
                with self._speech_lock:
                    self._is_speaking = False
                # Don't clear stop event here - let next call handle it
        
        # Create and start speech thread
        self.speech_thread = threading.Thread(
            target=speak_async,
            daemon=True,
            name="GUI_Speech_Thread"
        )
        self.speech_thread.start()
        
    def stop_speaking(self):
        """
        Public stop - ONLY for explicit user stop button
        Bot speech is NEVER interrupted by user input, only by newer bot responses
        """
        if not self._is_speaking:
            self.logger.speech("No speech to stop")
            return
        
        self.logger.speech("[STOP] Stopping speech (user clicked stop button)")
        
        # Signal stop
        self._speech_stop_event.set()
        
        # Stop TTS tool
        if self.ai_core.tts_tool:
            self.ai_core.tts_tool.stop()
        
        # Wait for thread to finish
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)
        
        # Clear state
        with self._speech_lock:
            self._is_speaking = False


# Legacy function for backward compatibility
def add_chat_message_with_timestamp(gui_instance, sender, message, msg_type="user", original_timestamp=""):
    """
    Legacy function - routes to ChatView.add_chat_message
    Kept for backward compatibility
    """
    from datetime import datetime
    from BASE.interface.gui_chat_view import ChatView
    
    # Convert legacy string types to MessageType enum
    if isinstance(msg_type, str):
        msg_type = ChatView._convert_legacy_type(msg_type)
    
    # Use original timestamp if provided
    if not original_timestamp:
        original_timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Route to ChatView
    ChatView.add_chat_message(
        gui_instance,
        sender,
        message,
        msg_type,
        original_timestamp=original_timestamp
    )