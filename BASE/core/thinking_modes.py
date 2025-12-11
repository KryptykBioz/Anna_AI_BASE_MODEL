# Filename: BASE/core/thinking_modes.py
"""
Thinking Modes - Specialized cognitive processing
NOW: Startup logic removed - handled by reflective mode automatically
"""
import time
import json
import asyncio
from typing import List, Optional, Dict
import re
from personality.bot_info import username


class ThinkingModes:
    """
    Specialized thinking mode implementations
    Uses tool_manager for all tool operations
    """
    __slots__ = (
        'processor', 'config', 'controls', 'logger',
        'prompt_builder',        # Centralized prompt builder
        'tool_manager',          # Tool manager reference
        'action_state_manager'   # Action state manager reference
    )
    
    def __init__(self, processor, config, controls, logger):
        """Initialize thinking modes with required dependencies"""
        self.processor = processor
        self.config = config
        self.controls = controls
        self.logger = logger
        
        # Initialize tool system references
        self.tool_manager = None
        self.action_state_manager = None
        
        # Get reference to processor's prompt builder
        self.prompt_builder = None
    
    def set_prompt_builder(self, prompt_builder):
        """
        Inject centralized prompt builder
        
        Args:
            prompt_builder: ThoughtPromptBuilder instance
        """
        self.prompt_builder = prompt_builder
        
        if self.logger:
            self.logger.system("[Thinking Modes] Prompt builder injected")
    
    # ========================================================================
    # CONTEXT BUILDING
    # ========================================================================
    
    async def build_thought_context(self) -> List[str]:
        """Build context for thought processing (NO CHAT)"""
        context_parts = []
        
        # Tool state (FIRST)
        tool_state = self._get_tool_state_summary()
        if tool_state:
            context_parts.insert(0, tool_state)
        
        # Session files (SECOND)
        if hasattr(self.processor, 'session_file_manager'):
            sfm = self.processor.session_file_manager
            if sfm and sfm.session_files:
                last_user_msg = self.processor.thought_buffer.get_last_user_input()
                session_context = sfm.get_context_for_query(last_user_msg)
                if session_context:
                    context_parts.append(session_context)
                    file_count = len(sfm.session_files)
                    self.logger.system(f"[Session Files] Added {file_count} file(s) to context")
        
        # User context
        user_ctx = self.processor.thought_buffer.get_user_context()
        if user_ctx:
            context_parts.append(user_ctx)
        
        # Memory context
        memory_ctx = await self._build_memory_context_for_thoughts()
        if memory_ctx:
            context_parts.append(memory_ctx)
        
        # Ongoing context
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        if ongoing_ctx:
            context_parts.append(f"Current Focus: {ongoing_ctx}")
        
        # Goal context
        if self.processor.thought_buffer.current_goal:
            goal_summary = self.processor.thought_buffer.get_goal_summary()
            if goal_summary:
                context_parts.append(goal_summary)
        
        return context_parts
    
    def _get_tool_state_summary(self) -> Optional[str]:
        """Get actionable tool state summary"""
        if hasattr(self, 'tool_manager') and self.tool_manager:
            if hasattr(self.tool_manager, 'action_state_manager'):
                action_mgr = self.tool_manager.action_state_manager
                failure_summary = action_mgr.get_recent_failures_summary(max_failures=3)
                
                if failure_summary:
                    return failure_summary
                
                pending = action_mgr.get_pending_actions()
                if len(pending) > 3:
                    return f"## PENDING TOOLS\n{len(pending)} actions in progress (may be slow)"
        
        return None
    
    async def _build_memory_context_for_thoughts(self) -> Optional[str]:
        """
        Build memory context considering current thought chain
        """
        if not self.processor.memory_search:
            return None
        
        # Get recent thoughts AND user input
        recent_thoughts = self.processor.thought_buffer.get_thoughts_for_response()[-5:]
        thoughts_text = " ".join([str(t) for t in recent_thoughts]).lower()
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        user_input = self.processor.thought_buffer.get_last_user_input()
        
        analysis_text = f"{thoughts_text} {ongoing_ctx} {user_input}".lower()
        
        # Detect memory triggers
        memory_triggers = {
            'recall': ['remember', 'recall', 'before', 'earlier', 'last time', 
                    'you said', 'we talked', 'previous', 'past'],
            'reference': ['how to', 'guide', 'explain', 'what is', 'tell me about',
                        'documentation', 'instructions'],
            'yesterday': ['yesterday', 'last night', 'this morning'],
            'comparison': ['different from', 'compared to', 'versus', 'better than']
        }
        
        needs_memory, memory_type = False, None
        
        for trigger_type, triggers in memory_triggers.items():
            if any(trigger in analysis_text for trigger in triggers):
                needs_memory = True
                memory_type = trigger_type
                break
        
        if not needs_memory:
            return None
        
        context_sections = []
        
        # Yesterday's context
        if memory_type == 'yesterday':
            yesterday_ctx = self.processor.memory_search.get_yesterday_context(max_entries=8)
            if yesterday_ctx:
                from datetime import datetime, timedelta
                yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                context_sections.append(f"## YESTERDAY'S CONVERSATION ({yesterday_date})")
                context_sections.append(yesterday_ctx)
        
        # Recall/comparison - Enhanced with thought chain
        if memory_type in ['recall', 'comparison']:
            query = user_input if user_input else ongoing_ctx
            if query:
                medium_results = self.processor.memory_search.search_medium_memory_combined(
                    user_input=query,
                    recent_thoughts=recent_thoughts,
                    k=3,
                    use_embedding_combination=True
                )
                if medium_results:
                    context_sections.append("\n## EARLIER TODAY")
                    for r in medium_results:
                        role = (self.processor.memory_search.memory_manager.username 
                            if r['role'] == 'user' 
                            else self.processor.memory_search.memory_manager.agentname)
                        context_sections.append(
                            f"[{r['timestamp']}] {role}: {r['content']} "
                            f"(relevance: {r['similarity']:.2f})"
                        )
                
                long_results = self.processor.memory_search.search_long_memory_combined(
                    user_input=query,
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
        
        # Reference queries - Enhanced with thought chain
        if memory_type == 'reference':
            query = self._extract_reference_query(analysis_text)
            if query:
                base_results = self.processor.memory_search.search_base_knowledge_combined(
                    user_input=query,
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
        
        return "\n".join(context_sections) if context_sections else None
    
    def _extract_reference_query(self, text: str) -> str:
        """Extract reference query from text"""
        patterns = [
            r'how to (.+?)(?:\?|$)', r'what is (.+?)(?:\?|$)',
            r'explain (.+?)(?:\?|$)', r'tell me about (.+?)(?:\?|$)',
            r'guide (?:for|to) (.+?)(?:\?|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        return ' '.join(words[:5]) if words else text[-100:]
    
    # ========================================================================
    # THINKING MODE DETERMINATION - AUTOMATIC STARTUP DETECTION
    # ========================================================================
    
    def determine_thinking_mode(self, context_parts: List[str]) -> str:
        """
        Determine thinking mode with automatic startup detection
        
        CRITICAL: If thought_count < 10, ALWAYS use reflective mode for startup
        """
        # Get current thought count
        thought_count = len(self.processor.thought_buffer.get_thoughts_for_response())
        
        # AUTOMATIC STARTUP DETECTION: < 10 thoughts = startup mode
        if thought_count < 10:
            if self.logger:
                self.logger.system(
                    f"[Mode Selection] Startup detected ({thought_count} thoughts) -> "
                    f"Using reflective mode for initialization"
                )
            return 'memory_reflection'
        
        # Get time since last user input (in seconds)
        time_since_user = self.processor.thought_buffer.get_time_since_last_user_input()
        
        # 6 minute threshold (360 seconds) for reflection mode
        REFLECTION_THRESHOLD = 360.0
        
        # If recent input (< 6 minutes), use standard mode
        if time_since_user < REFLECTION_THRESHOLD:
            return 'standard'
        
        # After 6+ minutes of no input, check for reflection triggers
        recent_thoughts = self.processor.thought_buffer.get_thoughts_for_response()[-5:]
        thoughts_text = " ".join([str(t) for t in recent_thoughts]).lower()
        
        has_memory_reference = any(word in thoughts_text for word in
                                ['remember', 'recall', 'before', 'earlier', 'last time'])
        
        has_future_orientation = any(word in thoughts_text for word in
                                    ['should', 'will', 'going to', 'plan', 'next'])
        
        consecutive = self.processor.thought_buffer.consecutive_proactive_thoughts
        
        # Only use special modes after 6+ minutes of inactivity
        if has_memory_reference or consecutive % 8 == 0:
            return 'memory_reflection'
        elif has_future_orientation or consecutive % 12 == 0:
            return 'future_planning'
        else:
            return 'standard'
    
    # ========================================================================
    # THINKING MODE IMPLEMENTATIONS
    # ========================================================================
    
    async def memory_reflective_thinking(self, context_parts: List[str]) -> Optional[Dict]:
        """
        Reflect on past events by retrieving memories
        NOW: Automatically handles startup when thought_count < 10
        """
        if not self.processor.memory_search:
            return await self.proactive_processing(context_parts)
        
        if not self.prompt_builder:
            self.logger.error("[Memory Reflection] No prompt builder available")
            return await self.proactive_processing(context_parts)
        
        # Get current thought count
        thought_count = len(self.processor.thought_buffer.get_thoughts_for_response())
        is_startup = thought_count < 10
        
        if is_startup and self.logger:
            self.logger.system(
                f"[Reflective Mode] STARTUP MODE (thoughts: {thought_count})"
            )
        
        recent_thoughts = self.processor.thought_buffer.get_recent_context(last_n=5)
        recent_thoughts_str = [str(t) for t in recent_thoughts]
        
        # Build query (not used for startup)
        query = " ".join(recent_thoughts_str[-3:]) if recent_thoughts_str else "past experiences"
        
        # Get ongoing context
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        if not ongoing_ctx:
            if is_startup:
                from datetime import datetime
                current_time = datetime.now().strftime("%A, %B %d at %I:%M %p")
                ongoing_ctx = f"System startup at {current_time}"
            else:
                ongoing_ctx = "Current state and recent thoughts"
        
        # Build prompt using centralized builder
        # The reflective constructor will automatically load startup context
        # when thought_count < 10
        prompt = self.prompt_builder.build_memory_reflection_prompt(
            recent_thoughts=recent_thoughts_str,
            ongoing_context=ongoing_ctx,
            memory_context=query  # Not used for startup
        )
        
        response = self.processor._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        result = self._parse_thinking_response(response)
        
        if result and is_startup and self.logger:
            self.logger.system(
                f"[Startup] Generated initial thought: {result['thought'][:100]}..."
            )
        
        return result
    
    async def future_planning_thinking(self, context_parts: List[str]) -> Optional[Dict]:
        """Plan future actions and anticipate needs"""
        if not self.prompt_builder:
            self.logger.error("[Future Planning] No prompt builder available")
            return await self.proactive_processing(context_parts)
        
        recent_thoughts = self.processor.thought_buffer.get_recent_context(last_n=5)
        recent_thoughts_str = [str(t) for t in recent_thoughts]
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        
        time_since_user = self.processor.thought_buffer.get_time_since_last_user_input()
        time_context = (f"{username} last spoke {time_since_user // 60:.0f} minutes ago" 
                    if time_since_user < 9999 else "No recent user input")
        
        prompt = self.prompt_builder.build_future_planning_prompt(
            recent_thoughts=recent_thoughts_str,
            ongoing_context=ongoing_ctx if ongoing_ctx else "Open time for planning",
            time_context=time_context
        )
        
        response = self.processor._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        return self._parse_thinking_response(response)
    
    async def proactive_processing(self, context_parts: List[str]) -> Optional[Dict]:
        """
        Standard proactive thought generation
        NOTE: Startup is now handled by reflective mode automatically
        """
        if not self.prompt_builder:
            self.logger.error("[Proactive] No prompt builder available")
            return None
        
        recent_thoughts = self.processor.thought_buffer.get_recent_context(last_n=10)
        recent_thoughts_str = [str(t) for t in recent_thoughts]
        
        # Extract recent responses
        recent_responses = []
        for thought in recent_thoughts_str:
            if "I just said" in thought or "I just asked" in thought:
                match = re.search(r'"([^"]+)"', thought)
                if match:
                    recent_responses.append(match.group(1).lower())
        
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        if not ongoing_ctx and context_parts:
            ongoing_ctx = "\n".join(context_parts[:2])
        if not ongoing_ctx:
            ongoing_ctx = "Just started - reflecting on recent memories"
        
        memory_context = ""
        if self.processor.memory_search and recent_thoughts_str:
            query = " ".join(recent_thoughts_str[-3:])
            long_results = self.processor.memory_search.search_long_memory(query, k=1)
            
            if long_results and long_results[0]['similarity'] > 0.5:
                memory_context = f"\n\n## RELEVANT PAST EXPERIENCE\n[{long_results[0]['date']}] {long_results[0]['summary']}"
        
        # Build repetition warning
        repetition_warning = ""
        if recent_responses:
            repetition_warning = (
                "\n\n## REPETITION PREVENTION\n"
                "You recently said these things:\n"
            )
            for resp in recent_responses[-2:]:
                repetition_warning += f"- \"{resp[:100]}\"\n"
            repetition_warning += "\nThink about something NEW. Don't repeat these ideas or phrases."
        
        # Build tool hints
        thoughts_text = ' '.join(recent_thoughts_str).lower()
        has_uncertainty = any(word in thoughts_text for word in 
                            ['wonder', 'curious', 'not sure', 'unclear', 'maybe'])
        
        tool_hints = []
        if has_uncertainty:
            tool_hints.append(
                "Note: Your recent thoughts show uncertainty. "
                "Consider what information would help."
            )
        
        user_input_age = self.processor.thought_buffer.get_time_since_last_user_input()
        if user_input_age > 600:
            tool_hints.append(
                f"{username} has been quiet for a while. "
                "Reflect on your memories and plan ahead."
            )
        
        consecutive = self.processor.thought_buffer.consecutive_proactive_thoughts
        
        prompt = self.prompt_builder.build_standard_proactive_prompt(
            recent_thoughts=recent_thoughts_str,
            ongoing_context=ongoing_ctx,
            memory_context=memory_context,
            repetition_warning=repetition_warning,
            tool_hints=tool_hints if tool_hints else None,
            consecutive_count=consecutive
        )
        
        response = self.processor._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        result = self._parse_thinking_response(response)
        
        return result
    
    def _parse_thinking_response(self, response: str) -> Optional[Dict]:
        """Parse LLM response for thought and actions"""
        think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL | re.IGNORECASE)
        action_match = re.search(r'<action_list>(.*?)</action_list>', response, re.DOTALL | re.IGNORECASE)
        
        thought = None
        actions = []
        
        if think_match:
            thought = think_match.group(1).strip()
            if not (10 <= len(thought) <= 300):
                thought = None
        
        if action_match:
            action_json = action_match.group(1).strip()
            action_json = re.sub(r'```json|```', '', action_json).strip()
            if action_json and action_json != '[]':
                try:
                    actions = json.loads(action_json)
                    if not isinstance(actions, list):
                        actions = []
                except:
                    actions = []
        
        if thought:
            return {'thought': thought, 'actions': actions}
        
        return None
    
    # ========================================================================
    # PERIODIC ACTIONS
    # ========================================================================
    
    async def periodic_memory_integration(self):
        """Periodic memory integration check"""
        if not self.processor.memory_search:
            return
        
        ongoing_ctx = self.processor.thought_buffer.get_ongoing_context()
        if not ongoing_ctx:
            return
        
        try:
            memory_results = self.processor.memory_search.search_long_memory(ongoing_ctx, k=1)
            
            if memory_results and memory_results[0]['similarity'] > 0.6:
                past_experience = memory_results[0]
                memory_thought = (
                    f"I remember discussing {ongoing_ctx} before: "
                    f"{past_experience['summary']}"
                )
                
                self.processor.thought_buffer.add_processed_thought(
                    memory_thought, 'memory_integration', past_experience['summary']
                )
                
                self.logger.memory("Integrated relevant memory")
        except Exception as e:
            self.logger.warning(f"Memory integration error: {e}")