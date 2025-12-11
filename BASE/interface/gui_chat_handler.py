# Filename: BASE/interface/gui_chat_handler.py
"""
GUI Chat Handler - Manages message flow between GUI and AI Core
FIXES: Proper user message saving, message ordering, auto-prompt handling
FIXED: Content filter now uses centralized AI Core filter with dynamic toggle
"""

from datetime import datetime
from typing import Optional
import threading


class GUIMessageHandler:
    """
    Handles the complete message flow:
    1. User submits message
    2. Save to memory immediately
    3. Display in GUI
    4. Process through AI Core
    5. Display bot response
    """
    
    def __init__(self, ai_core, message_processor, message_queue, logger):
        """
        Initialize GUI message handler
        
        Args:
            ai_core: AI Core instance (contains centralized content filter)
            message_processor: MessageProcessor instance
            message_queue: Queue for GUI updates
            logger: Logger instance
        """
        self.ai_core = ai_core
        self.message_processor = message_processor
        self.message_queue = message_queue
        self.logger = logger
        self.username = ai_core.config.username
        self.agentname = ai_core.config.agentname
        
        # Use centralized content filter from AI Core
        # This ensures single filter instance and respects ENABLE_CONTENT_FILTER toggle
        self.content_filter = ai_core.content_filter
        self.controls = ai_core.controls
    
    def handle_user_message(self, message: str, is_auto_prompt: bool = False):
        """
        Handle complete user message flow
        
        FIXED: Auto-prompts now pass empty string to AI Core for background processing
        FIXED: Content filter respects ENABLE_CONTENT_FILTER control variable
        
        Args:
            message: User's message text (can be empty for auto-prompts)
            is_auto_prompt: Whether this is from auto-prompt system
        """
        # For auto-prompts, process with empty message (triggers proactive check)
        if is_auto_prompt:
            self.logger.system("Processing auto-prompt (background check)")
            self._process_message_async("")
            return
        
        # Skip truly empty user messages
        if not message or not message.strip():
            self.logger.warning("Skipping empty user message")
            return
        
        # FIXED: Check ENABLE_CONTENT_FILTER before filtering
        if message and message.strip() and getattr(self.controls, 'ENABLE_CONTENT_FILTER', True):
            cleaned_message, was_filtered, reason = self.content_filter.filter_incoming(
                message,
                log_callback=self.logger.system
            )
            
            if was_filtered:
                self.logger.system(f"[Filter] Cleaned incoming: {reason}")
            
            message = cleaned_message
        
        # Step 1: Save user message to memory IMMEDIATELY
        user_entry = self.ai_core.memory_manager.save_user_message(message)
        
        # Step 2: Log save (no GUI display here - already shown by send_message)
        if user_entry:
            self.logger.system(f"User message saved and displayed: {message[:50]}...")
        else:
            self.logger.warning("Memory saving disabled")
        
        # Step 3: Process message asynchronously
        self._process_message_async(message)
    
    def _process_message_async(self, message: str):
        """Process message in background thread"""
        processing_thread = threading.Thread(
            target=self.message_processor.process_message,
            args=(message,),
            daemon=True,
            name="GUI_Message_Processing"
        )
        processing_thread.start()
    
    def _extract_time(self, full_timestamp: str) -> str:
        """
        Extract time portion from full timestamp
        
        Args:
            full_timestamp: e.g., "Wednesday, November 12, 2025 at 10:01:54 PM"
            
        Returns:
            Time string: "22:01:54" or original if parsing fails
        """
        try:
            if " at " in full_timestamp:
                time_part = full_timestamp.split(" at ")[1]
                dt = datetime.strptime(time_part, "%I:%M:%S %p")
                return dt.strftime("%H:%M:%S")
            return full_timestamp
        except Exception as e:
            self.logger.warning(f"Failed to parse timestamp: {e}")
            return full_timestamp
    
    def load_conversation_history(self, messages_to_load: int = 400):
        """
        Load conversation history from memory and display in GUI
        FIXED: Proper chronological ordering using full datetime
        """
        try:
            self.logger.memory("Checking for date rollover and previous day summarization...")
            self.ai_core.memory_manager.check_and_summarize_previous_day()
            
            all_messages = []
            all_messages.extend(self.ai_core.memory_manager.short_memory)
            all_messages.extend(self.ai_core.memory_manager.medium_memory)
            
            from datetime import datetime, timedelta
            current_date = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            recent_messages = [
                msg for msg in all_messages
                if msg.get('date') in [current_date, yesterday]
            ]
            
            recent_messages.sort(key=lambda x: self._parse_sortable_datetime(x))
            recent_messages = recent_messages[-messages_to_load:]
            
            for msg in recent_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                full_timestamp = msg.get('timestamp', '')
                
                display_time = self._extract_time(full_timestamp)
                
                if role == 'user':
                    sender = self.username
                    msg_type = "user"
                elif role == 'assistant':
                    sender = self.agentname
                    msg_type = "agent"
                else:
                    continue
                
                self.message_queue.put((msg_type, sender, content))
            
            self.logger.system(f"Loaded {len(recent_messages)} messages from conversation history")
            
        except Exception as e:
            self.logger.error(f"Failed to load conversation history: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_sortable_datetime(self, msg: dict) -> datetime:
        """Parse message timestamp into sortable datetime"""
        try:
            date_str = msg.get('date', '')
            timestamp_str = msg.get('timestamp', '')
            
            if " at " in timestamp_str:
                dt = datetime.strptime(timestamp_str, "%A, %B %d, %Y at %I:%M:%S %p")
                return dt
            
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            
            return datetime.fromtimestamp(0)
            
        except Exception as e:
            self.logger.warning(f"Failed to parse datetime for sorting: {e}")
            return datetime.fromtimestamp(0)