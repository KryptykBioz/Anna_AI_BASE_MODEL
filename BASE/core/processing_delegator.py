# Filename: BASE/core/processing_delegator.py
"""
Unified Processing Delegator - Enhanced Memory Integration
NOW: Memory retrieval considers both user input AND thought chain
"""
import asyncio
import time
from typing import Optional, List
from pathlib import Path

from BASE.core.thought_processor import ThoughtProcessor
from BASE.core.generators.response_generator import ResponseGenerator
from BASE.core.logger import Logger
from BASE.memory.memory_search import MemorySearch

from personality.controls import KILL_COMMAND
from personality.bot_info import username, agentname


class ProcessingDelegator:
    """
    Unified orchestrator for two-stage processing pipeline
    ENHANCED: Memory retrieval uses combined user input + thought context
    """
    
    def __init__(
        self,
        config,
        controls_module,
        project_root: Path,
        memory_manager=None,
        gui_logger=None,
        session_file_manager=None
    ):
        """Initialize unified processing delegator"""
        self.config = config
        self.controls = controls_module
        self.project_root = project_root
        self.memory_manager = memory_manager
        
        # Initialize logger WITH config
        self.logger = Logger(
            name="ProcessingDelegator", 
            gui_callback=gui_logger,
            config=config
        )
        
        # Verify config was set
        if not hasattr(self.logger, 'config') or self.logger.config is None:
            raise RuntimeError("Logger config not set during initialization!")
        
        if id(self.logger.config) != id(self.config):
            raise RuntimeError(
                f"Logger has different config instance!\n"
                f"  Delegator config: {id(self.config)}\n"
                f"  Logger config: {id(self.logger.config)}"
            )
        
        # Initialize memory search
        self.memory_search = None
        if memory_manager:
            self.memory_search = MemorySearch(memory_manager)
            self.logger.system("Memory search initialized with combined query support")
        else:
            self.logger.warning("No memory manager - memory features unavailable")
        
        # Store injected dependencies
        self.session_file_manager = session_file_manager
        
        # Tool manager (injected via set_tool_manager)
        self.tool_manager = None
        
        # Initialize STAGE 1: Thought Processor
        self.thought_processor = ThoughtProcessor(
            config=config,
            controls_module=controls_module,
            project_root=project_root,
            memory_search=self.memory_search,
            session_file_manager=session_file_manager,
            gui_logger=gui_logger
        )
        
        # Initialize STAGE 2: Response Generator
        self.response_generator = ResponseGenerator(
            config=config,
            controls_module=controls_module,
            project_root=project_root,
            memory_manager=memory_manager,
            memory_search=self.memory_search,
            gui_logger=gui_logger
        )
        
        # Link response generator to thought processor
        setattr(self.response_generator, '_thought_processor_ref', self.thought_processor)
        
        self.logger.system("ProcessingDelegator initialized with enhanced memory retrieval")
    
    # ========================================================================
    # ENHANCED: MEMORY CONTEXT BUILDING WITH THOUGHT CHAIN
    # ========================================================================
    
    def _build_memory_context(
        self, 
        user_input: str, 
        context_parts: List[str],
        recent_thoughts: List[str] = None
    ) -> str:
        """
        ENHANCED: Build memory context using BOTH user input AND thought chain
        
        Args:
            user_input: Current user input
            context_parts: Additional context (for trigger detection)
            recent_thoughts: Recent thoughts from thought buffer
        
        Returns:
            Formatted memory context string
        """
        if not self.memory_search:
            return ""
        
        # Get recent thoughts from thought buffer if not provided
        if recent_thoughts is None and hasattr(self, 'thought_processor'):
            recent_thoughts = self.thought_processor.thought_buffer.get_thoughts_for_response()[-5:]
        
        # Detect memory needs using combined context
        memory_needs = self._detect_memory_needs(user_input, context_parts, recent_thoughts)
        
        if not any([
            memory_needs['needs_medium'],
            memory_needs['needs_long'],
            memory_needs['needs_base'],
            memory_needs['needs_yesterday']
        ]):
            return ""
        
        context_sections = []
        
        # Yesterday's context (full detail)
        if memory_needs['needs_yesterday']:
            yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=8)
            if yesterday_ctx:
                context_sections.append("## YESTERDAY'S CONVERSATION")
                context_sections.append(yesterday_ctx)
        
        # Medium memory (earlier today) - ENHANCED with thought chain
        if memory_needs['needs_medium']:
            medium_results = self.memory_search.search_medium_memory_combined(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                k=3,
                use_embedding_combination=True  # Use weighted embedding
            )
            if medium_results:
                context_sections.append("\n## EARLIER TODAY")
                for r in medium_results:
                    role = username if r['role'] == 'user' else agentname
                    context_sections.append(
                        f"[{r['timestamp']}] {role}: {r['content']} "
                        f"(relevance: {r['similarity']:.2f})"
                    )
        
        # Long memory (past days) - ENHANCED with thought chain
        if memory_needs['needs_long']:
            long_results = self.memory_search.search_long_memory_combined(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                k=2,
                use_embedding_combination=True
            )
            if long_results:
                context_sections.append("\n## PAST CONVERSATIONS")
                for r in long_results:
                    context_sections.append(
                        f"[{r['date']}] {r['summary']} "
                        f"(relevance: {r['similarity']:.2f})"
                    )
        
        # Base knowledge - ENHANCED with thought chain
        if memory_needs['needs_base']:
            base_results = self.memory_search.search_base_knowledge_combined(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                k=3,
                min_similarity=0.4,
                use_embedding_combination=True
            )
            if base_results:
                context_sections.append("\n## KNOWLEDGE BASE")
                for r in base_results:
                    source = r.get('metadata', {}).get('source_file', 'unknown')
                    context_sections.append(
                        f"[{source}] {r['text']} "
                        f"(relevance: {r['similarity']:.2f})"
                    )
        
        return "\n".join(context_sections) if context_sections else ""
    
    def _detect_memory_needs(
        self, 
        user_input: str, 
        context_parts: List[str],
        recent_thoughts: List[str] = None
    ) -> dict:
        """
        ENHANCED: Detect memory needs from user input AND thought chain
        
        Args:
            user_input: Current user input
            context_parts: Additional context
            recent_thoughts: Recent thoughts from buffer
        
        Returns:
            Dictionary indicating which memory tiers to search
        """
        # Combine user input and thoughts for trigger detection
        text_to_analyze = user_input.lower()
        
        if recent_thoughts:
            thought_text = " ".join(recent_thoughts[-3:]).lower()
            text_to_analyze = f"{text_to_analyze} {thought_text}"
        
        recall_triggers = [
            'remember', 'recall', 'before', 'earlier', 'last time', 
            'you said', 'we talked', 'previous', 'mentioned', 'told me',
            'discussed', 'conversation about', 'when we', 'you told'
        ]
        
        reference_triggers = [
            'guide', 'how to', 'explain', 'what is', 'tell me about',
            'documentation', 'instructions', 'tutorial', 'help with',
            'show me how', 'teach me'
        ]
        
        yesterday_triggers = [
            'yesterday', 'last night', 'this morning', 'earlier today'
        ]
        
        history_triggers = [
            'history', 'past', 'previous', 'ago', 'used to', 'back when',
            'long time', 'weeks ago', 'months ago', 'before'
        ]
        
        comparison_triggers = [
            'different from', 'compared to', 'versus', 'vs', 'better than',
            'similar to', 'like before', 'unlike', 'same as'
        ]
        
        needs = {
            'needs_medium': False,
            'needs_long': False,
            'needs_base': False,
            'needs_yesterday': False,
            'query': user_input[-100:] if user_input else ""
        }
        
        # Detect triggers in combined context
        if any(trigger in text_to_analyze for trigger in yesterday_triggers):
            needs['needs_yesterday'] = True
            needs['needs_medium'] = True
        
        if any(trigger in text_to_analyze for trigger in recall_triggers + history_triggers):
            needs['needs_medium'] = True
            needs['needs_long'] = True
        
        if any(trigger in text_to_analyze for trigger in comparison_triggers):
            needs['needs_medium'] = True
            needs['needs_long'] = True
        
        if any(trigger in text_to_analyze for trigger in reference_triggers):
            needs['needs_base'] = True
            import re
            patterns = [
                r'how to (.+)',
                r'what is (.+)',
                r'explain (.+)',
                r'tell me about (.+)',
                r'guide (?:for|to) (.+)',
                r'documentation (?:for|about) (.+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, text_to_analyze)
                if match:
                    needs['query'] = match.group(1)[:50]
                    break
        
        return needs
    
    # ========================================================================
    # MAIN ENTRY POINTS (Enhanced with combined memory retrieval)
    # ========================================================================
    
    async def process_user_input(
        self,
        user_input: str,
        source: str = "GUI",
        user_id: str = "local_user",
        is_image_message: bool = False,
        image_path: Optional[Path] = None,
        timestamp: Optional[float] = None,
        username_override: Optional[str] = None,
        context_parts: list = None
    ) -> Optional[str]:
        """
        Process user input with ENHANCED memory retrieval
        Memory now considers both user input AND thought chain
        """
        # Kill command check
        if user_input and isinstance(user_input, str):
            if KILL_COMMAND in user_input.lower():
                self.logger.system("[Kill Command] Stopping")
                self.thought_processor.thought_buffer.force_shutdown()
                return None
        
        if self.thought_processor.thought_buffer.is_shutdown_requested():
            return None
        
        # Input filtering
        if user_input and user_input.strip():
            from BASE.handlers.content_filter import ContentFilter
            filter_instance = ContentFilter(use_ai_filter=False)
            
            cleaned_input, was_filtered, reason = filter_instance.filter_incoming(
                user_input,
                log_callback=self.logger.system
            )
            
            if was_filtered:
                self.logger.system(f"[Filter] Cleaned input: {reason}")
            
            user_input = cleaned_input
        
        context_parts = context_parts or []
        
        # Check chat engagement
        chat_engagement_enabled = getattr(self.controls, 'CHAT_ENGAGEMENT', False)
        is_autonomous_trigger = (source == "AUTONOMOUS_CHAT")
        
        clean_chat = self._get_clean_unengaged_chat()
        
        should_promote = False
        if chat_engagement_enabled and (clean_chat or is_autonomous_trigger):
            should_promote = self.thought_processor.thought_buffer.should_engage_with_chat()
            
            if should_promote:
                stats = self.thought_processor.thought_buffer.get_chat_engagement_stats()
                self.logger.system(f"[Chat Engagement] Promoting chat to primary response")
        
        if is_autonomous_trigger and not should_promote:
            return None
        
        original_input = ""
        
        # Input processing
        if should_promote and clean_chat:
            promoted_input = clean_chat
            original_input = promoted_input
            
            if user_input and user_input.strip():
                context_parts.insert(0, f"## USER NOTE\n{username_override or username} said: \"{user_input}\"")
            else:
                context_parts.insert(0, f"## AUTONOMOUS ENGAGEMENT\nResponding to chat activity")
            
            context_parts = [c for c in context_parts if not c.startswith('## LIVE CHAT')]
            self.thought_processor.ingest_user_directive(promoted_input)
            
        elif user_input and user_input.strip():
            original_input = user_input
            self.thought_processor.ingest_user_directive(user_input)
        
        # Session files context
        if hasattr(self, 'session_file_manager') and self.session_file_manager and self.session_file_manager.session_files:
            search_query = original_input if original_input else ""
            session_context = self.session_file_manager.get_context_for_query(search_query)
            if session_context:
                context_parts.insert(0, session_context)
        
        # ENHANCED: Get recent thoughts for memory context
        recent_thoughts = self.thought_processor.thought_buffer.get_thoughts_for_response()[-5:]
        
        # ENHANCED: Build memory context with combined user input + thoughts
        memory_context = self._build_memory_context(
            original_input, 
            context_parts,
            recent_thoughts=recent_thoughts
        )
        
        if memory_context:
            context_parts.insert(0, memory_context)
            self.logger.memory(
                f"[Enhanced Memory] Retrieved using user input + {len(recent_thoughts)} thoughts"
            )
        
        # STAGE 1: THOUGHT PROCESSING
        await self.thought_processor.process_thoughts(context_parts=context_parts)
        
        # Process tool results
        await self.thought_processor.process_thoughts(context_parts=context_parts)
        
        # STAGE 2: RESPONSE GENERATION
        response_context = []
        
        if memory_context:
            response_context.append(memory_context)
        
        if should_promote and clean_chat:
            response_context.append(f"## CHAT TO ADDRESS\n{clean_chat}")
        elif clean_chat:
            response_context.append(f"## LIVE CHAT ACTIVITY\n{clean_chat}")
        
        other_context = [
            c for c in context_parts 
            if not c.startswith('## LIVE CHAT') 
            and not c.startswith('## USER NOTE')
            and not c.startswith('## AUTONOMOUS ENGAGEMENT')
        ]
        response_context.extend(other_context)
        
        # Generate response
        response = await self.response_generator.generate_response(
            user_text=original_input,
            context_parts=response_context,
            is_chat_engagement=should_promote
        )
        
        # Add response echo immediately
        if response:
            self.thought_processor.thought_buffer.add_response_echo(
                response_text=response,
                timestamp=time.time()
            )
            self.logger.system(f"[Response Echo] Added to thought buffer immediately")
        
        # Mark chat as engaged
        if response and should_promote:
            unengaged = self.thought_processor.thought_buffer.get_unengaged_messages()
            message_indices = [msg.get('_index') for msg in unengaged if '_index' in msg]
            self.thought_processor.thought_buffer.mark_chat_engaged(message_indices)
            self.logger.system(f"[Chat Engagement] Marked {len(message_indices)} messages as engaged")
        
        return response
    
    # ========================================================================
    # HELPER METHODS (Preserved)
    # ========================================================================
    
    def _get_clean_unengaged_chat(self) -> Optional[str]:
        """Get clean unengaged chat messages"""
        if not hasattr(self, 'thought_processor') or not self.thought_processor:
            return None
        
        buffer = self.thought_processor.thought_buffer
        unengaged = buffer.get_unengaged_messages(max_messages=10)
        
        if not unengaged:
            return None
        
        batched_lines = []
        current_batch = []
        last_timestamp = 0
        
        for msg in unengaged:
            timestamp = msg.get('timestamp', 0)
            
            if last_timestamp > 0 and (timestamp - last_timestamp) > 10.0:
                if current_batch:
                    batched_lines.append("---")
            
            platform = msg.get('platform', 'Chat')
            username = msg.get('username', 'Unknown')
            message = msg.get('message', '')
            
            if not message or not username:
                continue
            
            current_batch.append(f"[{platform}] {username}: {message}")
            batched_lines.append(current_batch[-1])
            last_timestamp = timestamp
        
        if not batched_lines:
            return None
        
        header = f"PEOPLE IN CHAT: ({len(batched_lines)} messages)"
        return header + "\n" + "\n".join(batched_lines)
    
    def _extract_chat_from_context(self, context_parts: List[str]) -> Optional[str]:
        """Extract only live chat sections from context"""
        chat_parts = [
            part for part in context_parts
            if part.startswith('## LIVE CHAT')
        ]
        return '\n\n'.join(chat_parts) if chat_parts else None
    
    # ========================================================================
    # DEPENDENCY INJECTION
    # ========================================================================
    
    def set_tool_manager(self, tool_manager):
        """Inject tool manager into thought processor"""
        if not hasattr(self, 'thought_processor') or not self.thought_processor:
            if hasattr(self, 'logger'):
                self.logger.error(
                    "[ProcessingDelegator] [FAILED] Cannot inject: thought_processor not initialized!"
                )
            return
        
        self.tool_manager = tool_manager
        self.thought_processor.set_tool_manager(tool_manager)
        
        if hasattr(self, 'logger') and hasattr(self, 'controls'):
            if getattr(self.controls, 'LOG_TOOL_EXECUTION', False):
                enabled = tool_manager.get_enabled_tool_names()
                self.logger.system(
                    f"[ProcessingDelegator] [SUCCESS] Tool manager injected "
                    f"({len(enabled)} tools enabled)"
                )
    
    # ========================================================================
    # STATE ACCESS
    # ========================================================================
    
    def get_performance_stats(self) -> dict:
        """Get combined performance statistics"""
        thought_stats = self.thought_processor.get_performance_stats()
        response_stats = self.response_generator.get_response_stats()
        
        memory_stats = {}
        if self.memory_manager:
            memory_stats = self.memory_manager.get_stats()
        
        return {
            'thought_processor': thought_stats,
            'response_generator': response_stats,
            'memory': memory_stats,
            'enhanced_memory_retrieval': True  # Flag indicating new system
        }