# Filename: BASE/core/processing_delegator.py
"""
Processing Delegator - REFACTORED for Modular Prompt System
===========================================================
NEW: Uses SpokenConstructor for response generation
Removed old ResponseGenerator dependency
"""
import asyncio
import time
from typing import Optional, List
from pathlib import Path

from BASE.core.thought_processor import ThoughtProcessor
from BASE.core.logger import Logger
from BASE.memory.memory_search import MemorySearch

# NEW: Import spoken constructor and response decider
from BASE.core.response_decider import ResponseDecider, PriorityLevel
from BASE.core.spoken.spoken_constructor import SpokenConstructor

from personality.controls import KILL_COMMAND
from personality.bot_info import username, agentname


class ProcessingDelegator:
    """
    Unified orchestrator for two-stage processing pipeline
    REFACTORED: Uses modular spoken constructor
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
        """Initialize processing delegator with modular prompt system"""
        self.config = config
        self.controls = controls_module
        self.project_root = project_root
        self.memory_manager = memory_manager
        
        # Initialize logger
        self.logger = Logger(
            name="ProcessingDelegator", 
            gui_callback=gui_logger,
            config=config
        )
        
        # Initialize memory search
        self.memory_search = None
        if memory_manager:
            self.memory_search = MemorySearch(memory_manager)
            self.logger.system("Memory search initialized")
        
        # Store dependencies
        self.session_file_manager = session_file_manager
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
        
        # NEW: Initialize STAGE 2: Spoken Constructor
        self.spoken_constructor = SpokenConstructor(
            memory_search=self.memory_search,
            logger=self.logger
        )
        
        # NEW: Initialize response decider (for priority detection)
        self.response_decider = ResponseDecider(
            agentname=agentname,
            username=username,
            logger=self.logger
        )
        
        self.logger.system("ProcessingDelegator initialized with modular spoken constructor")
    
    # ========================================================================
    # MAIN ENTRY POINT - REFACTORED
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
        Process user input - REFACTORED
        NEW: Uses SpokenConstructor for response generation
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
                self.logger.system("[Chat Engagement] Promoting chat to primary response")
        
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
                context_parts.insert(0, "## AUTONOMOUS ENGAGEMENT\nResponding to chat activity")
            
            context_parts = [c for c in context_parts if not c.startswith('## LIVE CHAT')]
            self.thought_processor.ingest_user_directive(promoted_input)
            
        elif user_input and user_input.strip():
            original_input = user_input
            self.thought_processor.ingest_user_directive(user_input)
        
        # Session files context
        if self.session_file_manager and self.session_file_manager.session_files:
            search_query = original_input if original_input else ""
            session_context = self.session_file_manager.get_context_for_query(search_query)
            if session_context:
                context_parts.insert(0, session_context)
        
        # Build memory context
        recent_thoughts = self.thought_processor.thought_buffer.get_thoughts_for_response()[-5:]
        memory_context = self._build_memory_context(
            original_input, 
            context_parts,
            recent_thoughts=recent_thoughts
        )
        
        if memory_context:
            context_parts.insert(0, memory_context)
            self.logger.memory("[Memory] Retrieved context")
        
        # STAGE 1: THOUGHT PROCESSING
        await self.thought_processor.process_thoughts(context_parts=context_parts)
        
        # Process tool results
        await self.thought_processor.process_thoughts(context_parts=context_parts)
        
        # STAGE 2: RESPONSE GENERATION - REFACTORED
        response = await self._generate_spoken_response(
            user_text=original_input,
            context_parts=context_parts,
            chat_context=clean_chat,
            is_chat_engagement=should_promote
        )
        
        # Add response echo immediately
        if response:
            self.thought_processor.thought_buffer.add_response_echo(
                response_text=response,
                timestamp=time.time()
            )
            self.logger.system("[Response Echo] Added to thought buffer")
        
        # Mark chat as engaged
        if response and should_promote:
            unengaged = self.thought_processor.thought_buffer.get_unengaged_messages()
            message_indices = [msg.get('_index') for msg in unengaged if '_index' in msg]
            self.thought_processor.thought_buffer.mark_chat_engaged(message_indices)
            self.logger.system(f"[Chat Engagement] Marked {len(message_indices)} messages as engaged")
        
        return response
    
    # ========================================================================
    # RESPONSE GENERATION - REFACTORED
    # ========================================================================
    
    async def _generate_spoken_response(
        self,
        user_text: str,
        context_parts: List[str],
        chat_context: Optional[str] = None,
        is_chat_engagement: bool = False
    ) -> Optional[str]:
        """
        Generate spoken response - REFACTORED
        NEW: Uses SpokenConstructor + priority detection
        
        Args:
            user_text: Current user input
            context_parts: Additional context
            chat_context: Live chat messages
            is_chat_engagement: Whether responding to chat
        
        Returns:
            Spoken response text or None
        """
        # Detect priority markers in thoughts
        thought_buffer = self.thought_processor.thought_buffer
        priority_level, has_spoken_trigger = self.response_decider._detect_priority_markers(
            thought_buffer
        )
        
        if not has_spoken_trigger:
            # No high-priority markers - don't generate response
            return None
        
        # Get recent thoughts for context
        recent_thoughts = thought_buffer.get_thoughts_for_response()[-10:]
        
        # Build response context
        response_context = []
        
        # Add memory context
        memory_parts = [c for c in context_parts if c.startswith('## MEMORY') or c.startswith('## YESTERDAY')]
        response_context.extend(memory_parts)
        
        # Add chat context
        if is_chat_engagement and chat_context:
            response_context.append(f"## CHAT TO ADDRESS\n{chat_context}")
        elif chat_context:
            response_context.append(f"## LIVE CHAT ACTIVITY\n{chat_context}")
        
        # Add other context (game, vision, etc.)
        other_context = [
            c for c in context_parts 
            if not c.startswith('## LIVE CHAT') 
            and not c.startswith('## USER NOTE')
            and not c.startswith('## AUTONOMOUS ENGAGEMENT')
            and not c.startswith('## MEMORY')
            and not c.startswith('## YESTERDAY')
        ]
        response_context.extend(other_context[:3])  # Limit to 3 additional contexts
        
        # NEW: Build prompt using SpokenConstructor
        prompt = self.spoken_constructor.build_spoken_prompt(
            thought_chain=recent_thoughts,
            user_text=user_text,
            priority_level=priority_level.value,
            context_parts=response_context,
            chat_context=chat_context if is_chat_engagement else None,
            is_chat_engagement=is_chat_engagement
        )
        
        # Generate response
        response = self._call_ollama(
            prompt=prompt,
            model=self.config.text_model,
            system_prompt=None
        )
        
        # Clean response
        import re
        THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)
        response = THINK_PATTERN.sub('', response).strip()
        
        # Validate
        if not response:
            return None
        
        # Post-process (emoji removal)
        from BASE.core.clean_response import remove_emoji
        response = remove_emoji(response)
        
        return response
    
    def _call_ollama(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API"""
        import requests
        
        try:
            url = f"{self.config.ollama_endpoint}/api/generate"
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            self.logger.prompt(f"[Response Synthesis]\n{full_prompt}")
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "keep_alive": "24h"
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            content = result.get("response", "") or result.get("message", {}).get("content", "")
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            return ""
    
    # ========================================================================
    # MEMORY CONTEXT BUILDING - Enhanced with thought chain
    # ========================================================================
    
    def _build_memory_context(
        self, 
        user_input: str, 
        context_parts: List[str],
        recent_thoughts: List[str] = None
    ) -> str:
        """
        Build memory context using user input AND thought chain
        
        Args:
            user_input: Current user input
            context_parts: Additional context (for trigger detection)
            recent_thoughts: Recent thoughts from thought buffer
        
        Returns:
            Formatted memory context string
        """
        if not self.memory_search:
            return ""
        
        # Detect memory needs
        memory_needs = self._detect_memory_needs(user_input, context_parts, recent_thoughts)
        
        if not any([
            memory_needs['needs_medium'],
            memory_needs['needs_long'],
            memory_needs['needs_base'],
            memory_needs['needs_yesterday']
        ]):
            return ""
        
        context_sections = []
        
        # Yesterday's context
        if memory_needs['needs_yesterday']:
            yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=8)
            if yesterday_ctx:
                context_sections.append("## YESTERDAY'S CONVERSATION")
                context_sections.append(yesterday_ctx)
        
        # Medium memory (earlier today)
        if memory_needs['needs_medium']:
            medium_results = self.memory_search.search_medium_memory_combined(
                user_input=user_input,
                recent_thoughts=recent_thoughts,
                k=3,
                use_embedding_combination=True
            )
            if medium_results:
                context_sections.append("\n## EARLIER TODAY")
                for r in medium_results:
                    role = username if r['role'] == 'user' else agentname
                    context_sections.append(
                        f"[{r['timestamp']}] {role}: {r['content']} "
                        f"(relevance: {r['similarity']:.2f})"
                    )
        
        # Long memory (past days)
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
        
        # Base knowledge
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
        """Detect memory needs from user input AND thought chain"""
        # Combine user input and thoughts
        text_to_analyze = user_input.lower()
        
        if recent_thoughts:
            thought_text = " ".join(recent_thoughts[-3:]).lower()
            text_to_analyze = f"{text_to_analyze} {thought_text}"
        
        # Trigger detection
        recall_triggers = [
            'remember', 'recall', 'before', 'earlier', 'last time', 
            'you said', 'we talked', 'previous', 'mentioned', 'told me'
        ]
        
        reference_triggers = [
            'guide', 'how to', 'explain', 'what is', 'tell me about',
            'documentation', 'instructions'
        ]
        
        yesterday_triggers = [
            'yesterday', 'last night', 'this morning', 'earlier today'
        ]
        
        history_triggers = [
            'history', 'past', 'previous', 'ago', 'used to', 'back when'
        ]
        
        needs = {
            'needs_medium': False,
            'needs_long': False,
            'needs_base': False,
            'needs_yesterday': False,
            'query': user_input[-100:] if user_input else ""
        }
        
        if any(trigger in text_to_analyze for trigger in yesterday_triggers):
            needs['needs_yesterday'] = True
            needs['needs_medium'] = True
        
        if any(trigger in text_to_analyze for trigger in recall_triggers + history_triggers):
            needs['needs_medium'] = True
            needs['needs_long'] = True
        
        if any(trigger in text_to_analyze for trigger in reference_triggers):
            needs['needs_base'] = True
        
        return needs
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_clean_unengaged_chat(self) -> Optional[str]:
        """Get clean unengaged chat messages"""
        buffer = self.thought_processor.thought_buffer
        unengaged = buffer.get_unengaged_messages(max_messages=10)
        
        if not unengaged:
            return None
        
        lines = []
        for msg in unengaged:
            platform = msg.get('platform', 'Chat')
            chat_username = msg.get('username', 'Unknown')
            message = msg.get('message', '')
            
            if not message or not chat_username:
                continue
            
            lines.append(f"[{platform}] {chat_username}: {message}")
        
        if not lines:
            return None
        
        header = f"PEOPLE IN CHAT: ({len(lines)} messages)"
        return header + "\n" + "\n".join(lines)
    
    # ========================================================================
    # DEPENDENCY INJECTION
    # ========================================================================
    
    def set_tool_manager(self, tool_manager):
        """Inject tool manager into thought processor"""
        self.tool_manager = tool_manager
        self.thought_processor.set_tool_manager(tool_manager)
        
        enabled = tool_manager.get_enabled_tool_names()
        self.logger.system(
            f"[ProcessingDelegator] Tool manager injected "
            f"({len(enabled)} tools enabled)"
        )
    
    # ========================================================================
    # STATE ACCESS
    # ========================================================================
    
    def get_performance_stats(self) -> dict:
        """Get combined performance statistics"""
        thought_stats = self.thought_processor.get_performance_stats()
        
        memory_stats = {}
        if self.memory_manager:
            memory_stats = self.memory_manager.get_stats()
        
        return {
            'thought_processor': thought_stats,
            'memory': memory_stats,
            'prompt_system': 'modular_spoken'  # Flag
        }