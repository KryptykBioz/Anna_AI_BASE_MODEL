# Filename: BASE/core/ai_core.py
"""
AI Core - Main Orchestration
FIXED: Single Config and Logger instances throughout system
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
import time
import threading

from BASE.core.core_initializer import CoreInitializer
from BASE.core.logger import Logger
from BASE.core.config import Config
from BASE.handlers.content_filter import ContentFilter

from personality.controls import KILL_COMMAND

class AICore:
    """Main AI backend orchestrator with singleton Config/Logger"""
    
    __slots__ = (
        'config', 'controls', 'project_root', 'gui_logger', 'logger',
        'shutdown_flag', 'speech_stop_flag', 'main_loop', '_loop_thread',
        'memory_manager', 'memory_search', 'session_file_manager',
        'processing_delegator', 'control_manager', 'tts_tool',
        'discord_integration', 'youtube_chat', 'twitch_chat', 'chat_handler',
        'last_reminder_cleanup', 'reminder_cleanup_interval', 'initializer', 'content_filter',
        'action_state_manager', 'instruction_persistence_manager', 'tool_manager'
    )
    
    def __init__(self, config, controls_module, project_root=None, gui_logger=None):
        """
        Initialize AI system with singleton Config and Logger
        
        CRITICAL: config parameter MUST be the same instance used everywhere
        """
        # ===================================================================
        # STEP 1: Store singleton references
        # ===================================================================
        self.config = config  # This MUST be the singleton instance
        self.controls = controls_module
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.gui_logger = gui_logger
        
        # ===================================================================
        # STEP 2: Create Logger WITH config reference immediately
        # ===================================================================
        # CRITICAL FIX: Pass config at creation, not later
        self.logger = Logger(
            name="Core",
            gui_callback=gui_logger,
            config=self.config  # Pass singleton config immediately
        )
        
        # Verify config is set correctly
        if not hasattr(self.logger, 'config') or self.logger.config is None:
            raise RuntimeError("CRITICAL: Logger config not set during initialization!")
        
        # Verify same instance
        if id(self.logger.config) != id(self.config):
            raise RuntimeError(
                f"CRITICAL: Logger has different config instance!\n"
                f"  AICore config: {id(self.config)}\n"
                f"  Logger config: {id(self.logger.config)}"
            )
        
        self.logger.system(f"[Init] Config instance: {id(self.config)}")
        self.logger.system(f"[Init] Logger config instance: {id(self.logger.config)}")
        self.logger.system("[Init] [SUCCESS] Single config instance verified")
        
        self.shutdown_flag = threading.Event()
        self.speech_stop_flag = threading.Event()
        
        # Event loop
        self.main_loop = None
        self._loop_thread = None
        self._start_event_loop()
        
        # External tools (injected later)
        self.tts_tool = None
        
        # Integration placeholders
        self.discord_integration = None
        self.youtube_chat = None
        self.twitch_chat = None
        self.chat_handler = None
        
        # State
        self.last_reminder_cleanup = 0
        self.reminder_cleanup_interval = 60
        
        # ===================================================================
        # STEP 3: Initialize via CoreInitializer with singleton config
        # ===================================================================
        self.logger.system("Initializing AI Core...")
        self.initializer = CoreInitializer(
            ai_core=self,
            config=self.config,  # Pass same singleton instance
            controls=controls_module,
            project_root=self.project_root,
            logger=self.logger,  # Pass logger with config already set
            main_loop=self.main_loop
        )

        # Run initialization
        self.initializer.initialize_all_systems()

        # Initialize content filter ONCE
        self.content_filter = ContentFilter(
            ollama_endpoint=config.ollama_endpoint,
            use_ai_filter=controls_module.USE_AI_CONTENT_FILTER
        )
        self.logger.system("Content filter initialized (centralized)")

        # Extract initialized components
        self.memory_manager = self.initializer.memory_manager
        self.memory_search = self.initializer.memory_search
        self.session_file_manager = self.initializer.session_file_manager
        self.action_state_manager = self.initializer.action_state_manager
        self.instruction_persistence_manager = self.initializer.instruction_persistence_manager
        self.processing_delegator = self.initializer.processing_delegator
        self.control_manager = self.initializer.control_manager
        self.tool_manager = self.initializer.tool_manager

        # ===================================================================
        # STEP 4: Verify all components share same config
        # ===================================================================
        self._verify_config_propagation()
        
        self.logger.system("AI Core Initialization Complete")
    
    def _verify_config_propagation(self):
        """
        Verify all components reference the same config instance
        CRITICAL: This catches initialization bugs early
        """
        base_config_id = id(self.config)
        
        checks = {
            'logger': (self.logger.config, 'Logger'),
            'control_manager': (self.control_manager.config if hasattr(self.control_manager, 'config') else None, 'ControlManager'),
        }
        
        failures = []
        for component_name, (component_config, display_name) in checks.items():
            if component_config is None:
                self.logger.warning(f"[Config Check] {display_name} has no config reference")
                continue
            
            if id(component_config) != base_config_id:
                failures.append(
                    f"  - {display_name}: {id(component_config)} != {base_config_id}"
                )
        
        if failures:
            error_msg = (
                "CRITICAL: Config instance mismatch detected!\n" +
                "\n".join(failures)
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self.logger.system("[Config Check] [SUCCESS] All components share same config instance")
    
    def _start_event_loop(self):
        """Start dedicated event loop for async processing"""
        def run_loop():
            self.main_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.main_loop)
            self.main_loop.run_forever()
        
        self._loop_thread = threading.Thread(target=run_loop, daemon=True, name="AICore_EventLoop")
        self._loop_thread.start()
        
        timeout, start_time = 5.0, time.time()
        while self.main_loop is None and (time.time() - start_time) < timeout:
            time.sleep(0.01)
        
        if self.main_loop:
            self.logger.system("Event loop initialized")
        else:
            self.logger.error("Failed to initialize event loop")
    
    def _stop_event_loop(self):
        """Stop the event loop"""
        if self.main_loop and self.main_loop.is_running():
            self.main_loop.call_soon_threadsafe(self.main_loop.stop)
            if self._loop_thread:
                self._loop_thread.join(timeout=2.0)
            self.logger.system("Event loop stopped")
    
    # ========================================================================
    # DEPENDENCY INJECTION API
    # ========================================================================
    
    def setup_tts_tool(self, tts_tool):
        """Inject TTS tool"""
        self.tts_tool = tts_tool
        
        if hasattr(self, 'processing_delegator'):
            response_gen = self.processing_delegator.response_generator
            if hasattr(response_gen, 'set_tts_tool'):
                response_gen.set_tts_tool(tts_tool)
        
        if tts_tool.is_available():
            info = tts_tool.get_voice_info()
            self.logger.speech(f"TTS tool connected: {info.get('name', 'Unknown')}")
        else:
            self.logger.warning("TTS tool registered but not available")
    
    # ========================================================================
    # INTEGRATION LIFECYCLE
    # ========================================================================
    
    def start_integrations(self):
        """Start all external integrations"""
        self.logger.system("Integrations started")
    
    def shutdown(self):
        """Gracefully shutdown all systems"""
        self.logger.system("🛑 Starting IMMEDIATE shutdown...")
        self.shutdown_flag.set()
        self.speech_stop_flag.set()
        
        # Stop cognitive loop FIRST
        try:
            thought_processor = self.processing_delegator.thought_processor
            thought_buffer = thought_processor.thought_buffer
            thought_buffer.force_shutdown()
            
            if hasattr(thought_processor, 'cognitive_loop'):
                loop_manager = thought_processor.cognitive_loop
                if loop_manager and loop_manager.is_running:
                    if self.main_loop and self.main_loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            loop_manager.stop_continuous_loop(), self.main_loop
                        )
                        time.sleep(0.5)
            
            self.logger.system("🛑 Stopped cognitive loop")
        except Exception as e:
            self.logger.warning(f"Error stopping cognitive loop: {e}")
        
        # Stop chat handler
        if hasattr(self, 'chat_handler') and self.chat_handler:
            try:
                self.chat_handler.shutdown()
            except Exception as e:
                self.logger.warning(f"Error stopping chat handler: {e}")
        
        # Stop Discord
        if self.discord_integration and self.discord_integration.running:
            try:
                self.discord_integration.stop()
                self.logger.discord("Stopped")
            except Exception as e:
                self.logger.warning(f"Error stopping Discord: {e}")
        
        # Stop TTS
        if self.tts_tool:
            try:
                self.tts_tool.stop()
            except:
                pass
        
        # Stop event loop
        self._stop_event_loop()
        
        self.logger.system("🛑 Shutdown complete")
    
    # ========================================================================
    # MAIN API - USER INTERACTION
    # ========================================================================
    
    async def process_user_message(
        self, message: str, source: str = "GUI", user_id: str = "local_user",
        is_image_message: bool = False, image_path: Optional[Path] = None,
        timestamp: Optional[float] = None, username_override: Optional[str] = None
    ) -> Optional[str]:
        """Main entry point with centralized filtering"""
        # Kill command check (highest priority)
        if message and isinstance(message, str):
            if self._check_kill_command(message):
                self.logger.system("[Kill Command] Initiating shutdown")
                self.shutdown_flag.set()
                self.speech_stop_flag.set()
                
                if hasattr(self, 'processing_delegator'):
                    thought_buffer = self.processing_delegator.thought_processor.thought_buffer
                    thought_buffer.force_shutdown()
                
                shutdown_thread = threading.Thread(target=self.shutdown, daemon=True)
                shutdown_thread.start()
                return "Shutting down immediately..."
        
        if self.shutdown_flag.is_set():
            self.logger.error("[Process] Cannot process: System shutting down")
            return None
        
        # Normalize empty messages
        if message and not message.strip():
            message = ""
        
        # CENTRALIZED INPUT FILTERING
        if message and message.strip() and getattr(self.controls, 'ENABLE_CONTENT_FILTER', True):
            cleaned_message, was_filtered, reason = self.content_filter.filter_incoming(
                message,
                log_callback=self.logger.system
            )
            
            if was_filtered:
                self.logger.system(f"[Filter Input] {reason}")
            
            message = cleaned_message
        
        # Periodic cleanup
        if hasattr(self, 'action_state_manager') and self.action_state_manager:
            self.action_state_manager.cleanup_old_actions()
        self._cleanup_old_reminders()
        
        # Build context
        context_parts = self._build_context(user_text=message)
        
        # Detect autonomous chat engagement
        is_autonomous_chat = (source == "AUTONOMOUS_CHAT")
        
        if not message and self._should_check_chat_engagement():
            self.logger.system("[Chat Engagement] Autonomous engagement check")
        
        # Process via delegator
        try:
            reply = await self.processing_delegator.process_user_input(
                user_input=message, source=source, user_id=user_id,
                is_image_message=is_image_message, image_path=image_path,
                timestamp=timestamp, username_override=username_override,
                context_parts=context_parts
            )
            
            # CENTRALIZED OUTPUT FILTERING
            if reply and getattr(self.controls, 'ENABLE_CONTENT_FILTER', True):
                cleaned_reply, was_filtered, reason = self.content_filter.filter_outgoing(
                    reply,
                    log_callback=self.logger.system
                )
                
                if was_filtered:
                    self.logger.system(f"[Filter Output] {reason}")
                
                reply = cleaned_reply
            
            if reply and is_autonomous_chat:
                self.logger.system(f"[Autonomous Chat] Response: {reply}")
            
            # Save to memory
            if reply and self.controls.SAVE_MEMORY:
                self.memory_manager.save_bot_response(reply)
                self.logger.memory("Saved bot response to memory")
            
            return reply
        except Exception as e:
            self.logger.error(f"[Process] Error processing message: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_kill_command(self, text: str) -> bool:
        """Check if text contains kill command"""
        if not text or not isinstance(text, str):
            return False
        return KILL_COMMAND in text.lower()
    
    def _should_check_chat_engagement(self) -> bool:
        """Check if chat engagement should be considered"""
        chat_enabled = getattr(self.controls, 'CHAT_ENGAGEMENT', False)
        if not chat_enabled:
            return False
        
        has_active_chat = (
            (self.youtube_chat and self.youtube_chat.enabled) or
            (self.twitch_chat and self.twitch_chat.enabled) or
            (self.discord_integration and self.discord_integration.running)
        )
        return has_active_chat
    
    # ========================================================================
    # CONTEXT BUILDING
    # ========================================================================
    
    def _build_context(self, user_text: str = "") -> List[str]:
        """Build context for AI processing"""
        context_parts = []
        
        # Session files
        if hasattr(self, 'session_file_manager') and self.session_file_manager:
            if self.session_file_manager.session_files:
                session_context = self.session_file_manager.get_context_for_query(user_text)
                if session_context:
                    context_parts.append(session_context)
        
        # Live chat context
        chat_context = self._get_chat_context()
        if chat_context:
            chat_engagement = getattr(self.controls, 'CHAT_ENGAGEMENT', False)
            if chat_engagement:
                context_parts.append(f"## LIVE CHAT ACTIVITY\n{chat_context}")
            else:
                context_parts.append(f"## LIVE CHAT ACTIVITY (response-only)\n{chat_context}")
        
        # Pending actions
        pending_context = self._get_pending_actions_context()
        if pending_context:
            context_parts.append(pending_context)
        
        return context_parts
    
    def _get_pending_actions_context(self) -> str:
        """Get pending actions context from tool system"""
        if not hasattr(self, 'action_state_manager') or not self.action_state_manager:
            return ""
        
        try:
            pending = self.action_state_manager.get_context_summary()
            if pending:
                return f"## PENDING ACTIONS\n\n{pending}"
        except Exception as e:
            self.logger.warning(f"[Pending Actions] Failed to get context: {e}")
        
        return ""
    
    def _get_chat_context(self) -> str:
        """Get live chat messages"""
        if hasattr(self, 'chat_handler') and self.chat_handler:
            chat_messages = self._get_clean_chat_messages()
            if not chat_messages:
                return ""
            
            # Ingest into thought buffer
            for msg in chat_messages:
                self._ingest_chat_message_clean(msg)
            
            return self._format_chat_for_context(chat_messages)
        
        return self._get_chat_context_legacy()
    
    def _get_clean_chat_messages(self, max_messages: int = 10, max_age: float = 300.0):
        """Get clean chat message objects from ChatHandler"""
        if not hasattr(self, 'chat_handler') or not self.chat_handler:
            return []
        
        all_messages = []
        current_time = time.time()
        
        for platform_name, buffer in self.chat_handler._buffers.items():
            for msg in buffer:
                if (current_time - msg.timestamp) > max_age:
                    continue
                all_messages.append(msg)
        
        all_messages.sort(key=lambda m: m.timestamp)
        return all_messages[-max_messages:]
    
    def _format_chat_for_context(self, chat_messages) -> str:
        """Format chat messages for context"""
        if not chat_messages:
            return ""
        lines = [f"[{msg.platform}] {msg.author}: {msg.content}" for msg in chat_messages]
        return "\n".join(lines)
    
    def _ingest_chat_message_clean(self, chat_msg):
        """Ingest clean ChatMessage into thought buffer"""
        from personality.bot_info import agentname
        has_mention = agentname.lower() in chat_msg.content.lower()
        
        self.processing_delegator.thought_processor.thought_buffer.ingest_chat_message(
            platform=chat_msg.platform,
            username=chat_msg.author,
            message=chat_msg.content,
            has_bot_mention=has_mention
        )
    
    def _get_chat_context_legacy(self) -> str:
        """Get chat from legacy integrations"""
        chat_parts = []
        
        if self.youtube_chat and self.youtube_chat.enabled:
            yt_context = self.youtube_chat.get_context_for_ai()
            if yt_context:
                chat_parts.append(f"[YouTube]\n{yt_context}")
        
        if self.twitch_chat and self.twitch_chat.enabled:
            twitch_context = self.twitch_chat.get_context_for_ai()
            if twitch_context:
                chat_parts.append(f"[Twitch]\n{twitch_context}")
        
        return "\n\n".join(chat_parts) if chat_parts else ""
    
    def get_live_chat_context(self) -> str:
        """Get recent live chat for AI context"""
        if not hasattr(self, 'chat_handler') or not self.chat_handler:
            return ""
        return self.chat_handler.get_recent_chat_context(max_messages=10, max_age_seconds=300.0)
    
    def _cleanup_old_reminders(self):
        """Periodic cleanup of announced reminders"""
        current_time = time.time()
        if current_time - self.last_reminder_cleanup < self.reminder_cleanup_interval:
            return
        
        self.last_reminder_cleanup = current_time
        
        if not getattr(self.controls, 'USE_REMINDERS', False):
            return
    
    # ========================================================================
    # ACCESSORS
    # ========================================================================
    
    def list_session_files(self):
        """List all session files"""
        return self.session_file_manager.list_files()
    
    def load_session_file(self, filepath: Path):
        """Load a session file from disk"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = self.session_file_manager.add_file(
                filepath=str(filepath), content=content, file_type="auto"
            )
            
            if result['success']:
                self.logger.system(f"Loaded session file: {filepath.name}")
                return result
            else:
                self.logger.error(f"Failed to load: {result.get('error', 'Unknown error')}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading {filepath}: {e}")
            return None
    
    def get_control_manager(self):
        return self.control_manager
    
    def get_memory_manager(self):
        return self.memory_manager
    
    def get_session_file_manager(self):
        return self.session_file_manager
    
    # Session file convenience methods
    def add_session_file(self, filepath: str, content: str, file_type: str = "auto"):
        return self.session_file_manager.add_file(filepath, content, file_type)
    
    def unload_session_file(self, file_id: str):
        return self.session_file_manager.remove_file(file_id)
    
    def remove_session_file(self, file_id: str):
        return self.session_file_manager.remove_file(file_id)
    
    def get_session_file_content(self, file_id: str, line_start=None, line_end=None):
        return self.session_file_manager.get_file_content(file_id, line_start, line_end)
    
    def search_session_files(self, query: str, file_id=None, top_k: int = 5):
        return self.session_file_manager.search(query, file_id, top_k)
    
    def clear_all_session_files(self):
        self.session_file_manager.clear_all()
    
    def clear_session_files(self):
        self.session_file_manager.clear_all()
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        stats = {
            'memory': self.memory_manager.get_stats(),
            'delegator': self.processing_delegator.get_performance_stats()
        }
        
        if hasattr(self, 'instruction_persistence_manager'):
            stats['instruction_persistence'] = (
                self.instruction_persistence_manager.get_statistics()
            )
        
        if hasattr(self, 'processing_delegator'):
            thought_processor = self.processing_delegator.thought_processor
            if hasattr(thought_processor, 'cognitive_loop') and thought_processor.cognitive_loop:
                stats['cognitive_loop'] = thought_processor.cognitive_loop.get_statistics()
        
        return stats