# Filename: BASE/core/constructors/response_prompt_constructor.py
"""
Response Prompt Constructor - Uses Centralized Personality
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass

from BASE.core.context_detector import ContextDetector
from BASE.handlers.content_filter import ContentFilter

from BASE.core.prompts.shared_prompt_segments import SharedPromptSegments, PromptSegment
from BASE.core.prompts.response_prompt_parts import ResponsePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts
from personality.bot_info import agentname, username


class ResponsePromptConstructor:
    """
    Builds prompts for synthesizing natural spoken responses
    NOW: Uses centralized personality injection
    """
    
    def __init__(self, controls_module, memory_search=None, game_manager=None):
        self.controls = controls_module
        self.memory_search = memory_search
        self.game_manager = game_manager
        self._token_budget = 1200
        self.shared = SharedPromptSegments()
        self.detector = ContextDetector()
        self.parts = ResponsePromptParts()
        self.personality = PersonalityPromptParts()
        self._context_filter = ContentFilter(use_ai_filter=False)
    
    def get_minimal_identity(self) -> str:
        """Ultra-minimal identity for high urgency - uses centralized personality"""
        return self.personality.get_personality_injection('response')
    
    def get_response_rules_compact(self) -> str:
        """Compact rules for medium urgency"""
        return self.parts.get_response_rules_compact()
    
    def get_urgency_instruction(self, urgency_level: int, has_reminders: bool = False) -> str:
        """Get concise instruction based on urgency"""
        instructions = self.parts.get_urgency_instructions()
        
        if has_reminders:
            return instructions['reminder']
        elif urgency_level >= 9:
            return instructions['9+']
        elif urgency_level == 8:
            return instructions['8']
        elif urgency_level == 7:
            return instructions['7']
        elif urgency_level >= 5:
            return instructions['5+']
        else:
            return instructions['default']
    
    def get_chat_instruction(self) -> str:
        """Compact chat handling instruction"""
        return self.parts.get_chat_instruction()
    
    def _build_memory_context_sections(self) -> str:
        """Build memory context sections for response prompts"""
        if not self.memory_search:
            return ""
        
        short_memory = self.memory_search.get_short_memory()
        if short_memory:
            return self.parts.format_section("RECENT CONVERSATION", short_memory)
        
        return ""

    def _get_top_long_term_memory(self, query: str) -> str:
        """Get single most relevant long-term memory"""
        if not self.memory_search:
            return ""
        
        long_results = self.memory_search.search_long_memory(query, k=1)
        
        if not long_results:
            return ""
        
        result = long_results[0]
        date = result.get('date', 'Unknown')
        summary = result.get('summary', '')
        similarity = result.get('similarity', 0.0)
        
        if similarity < 0.3:
            return ""
        
        return f"\n\n## RELEVANT PAST MEMORY\n\n**[{date}]** (relevance: {similarity:.2f})\n{summary}"

    def build_response_prompt_simple(
        self,
        user_text: str,
        context_parts: List[str],
        chat_context: Optional[str] = None,
        is_chat_engagement: bool = False
    ) -> str:
        """
        Build response prompt using thought buffer directly
        NO state management - gets thoughts from buffer via injected reference
        
        Args:
            user_text: Current user input
            context_parts: Additional context (memory, game, etc.)
            chat_context: Live chat context
            is_chat_engagement: Whether this is chat engagement
        
        Returns:
            Complete response prompt
        """
        
        # Minimal identity with personality
        identity = self.get_minimal_identity()
        
        # Build instruction based on context
        if is_chat_engagement:
            instruction = self.parts.get_chat_engagement_instruction()
        else:
            instruction = "Respond naturally based on your recent thoughts and the current situation."
        
        # Format sections
        sections = [identity]
        
        # Add context
        if context_parts:
            context_text = "\n\n".join(context_parts[:3])
            if context_text:
                sections.append(f"\n## CONTEXT\n\n{context_text}")
        
        # Add chat if present
        if chat_context:
            sections.append(self.parts.format_section("LIVE CHAT", chat_context))
        
        # Add user message if present
        if user_text and not is_chat_engagement:
            sections.append(f'\n**{username}:** "{user_text}"')
        elif is_chat_engagement and user_text:
            sections.append(f'\n## CHAT TO ADDRESS\n\n{user_text}')
        
        # Add instruction
        sections.append(f"\n{instruction}")
        
        # Add personality examples if available
        if self.memory_search:
            query_parts = []
            if user_text:
                query_parts.append(user_text)
            if chat_context:
                chat_lines = chat_context.split('\n')
                query_parts.extend(chat_lines[-2:])
            
            query = " ".join(query_parts) if query_parts else ""
            
            if query:
                examples = self.memory_search.get_response_generation_examples(context=query, k=2)
                if examples:
                    sections.append(self.parts.format_section("PERSONALITY EXAMPLES", examples))
        
        sections.append("\n**Respond naturally (1-2 sentences):**")
        
        return "\n".join(sections)
    
    def _build_memory_context_with_search(self, query: str, k: int = 2) -> str:
        """Build memory context with intelligent search"""
        if not self.memory_search:
            return ""
        
        sections = []
        
        short_memory = self.memory_search.get_short_memory()
        if short_memory:
            sections.append("## RECENT CONVERSATION\n\n" + short_memory)
        
        long_results = self.memory_search.search_long_memory(query, k=k)
        if long_results:
            sections.append("\n\n## RELEVANT PAST CONTEXT\n")
            for result in long_results:
                date = result.get('date', 'Unknown')
                summary = result.get('summary', '')
                similarity = result.get('similarity', 0.0)
                sections.append(f"\n**[{date}]** (relevance: {similarity:.2f})")
                sections.append(f"{summary}")
        
        return "\n".join(sections) if sections else ""

    def _detect_memory_needs(self, user_msg: str, thoughts_text: str) -> bool:
        """Detect if long-term memory search is needed"""
        text = f"{user_msg} {thoughts_text}".lower()
        
        memory_triggers = [
            'remember', 'recall', 'before', 'earlier', 'last time',
            'you said', 'we talked', 'yesterday', 'previous', 'past',
            'mentioned', 'told me', 'discussed', 'conversation about',
            'when we', 'you told', 'last week', 'few days ago'
        ]
        
        return any(trigger in text for trigger in memory_triggers)

# In build_response_prompt(), remove all filtering:
    def build_response_prompt(
        self,
        thoughts_text: str,
        last_user_msg: str,
        urgency_level: int,
        context_parts: List[str],
        has_reminders: bool = False,
        chat_context: Optional[str] = None,
        is_chat_engagement: bool = False
    ) -> str:
        """Build response prompt - no filtering (done upstream)"""
        
        # Directly use inputs - already filtered by ai_core
        if urgency_level >= 9:
            return self._build_critical_prompt(
                thoughts_text, last_user_msg, urgency_level, 
                has_reminders, chat_context, is_chat_engagement
            )
        elif urgency_level >= 7:
            return self._build_high_priority_prompt(
                thoughts_text, last_user_msg, urgency_level,
                context_parts, chat_context, is_chat_engagement
            )
        else:
            return self._build_standard_prompt(
                thoughts_text, last_user_msg, urgency_level,
                context_parts, chat_context, is_chat_engagement
            )
    
    def _build_critical_prompt(
        self,
        thoughts_text: str,
        last_user_msg: str,
        urgency_level: int,
        has_reminders: bool,
        chat_context: Optional[str],
        is_chat_engagement: bool
    ) -> str:
        """TIER 1: Critical urgency (9-10) WITH personality injection"""
        templates = self.parts.get_prompt_templates()
        
        instruction = self.parts.get_chat_engagement_instruction() if is_chat_engagement else self.get_urgency_instruction(urgency_level, has_reminders)
        
        context_section = ""
        if chat_context and urgency_level == 9:
            context_section = self.parts.format_section("CHAT", chat_context)
        
        user_section = self.parts.format_user_message(last_user_msg, is_chat_engagement) if last_user_msg else ""
        
        memory_context = ""
        if self.memory_search:
            short_memory = self.memory_search.get_short_memory()
            if short_memory:
                lines = short_memory.split('\n')
                recent_lines = lines[-5:] if len(lines) > 5 else lines
                memory_context = self.parts.format_section("RECENT CONTEXT", '\n'.join(recent_lines))
        
        personality_section = ""
        if self.memory_search:
            query_parts = []
            if last_user_msg:
                query_parts.append(last_user_msg)
            if chat_context:
                chat_lines = chat_context.split('\n')
                query_parts.extend(chat_lines[-2:])
            
            query = " ".join(query_parts) if query_parts else ""
            
            if query:
                examples = self.memory_search.get_response_generation_examples(context=query, k=1)
                if examples:
                    personality_section = self.parts.format_section("PERSONALITY EXAMPLES", examples)
        
        return templates['critical'].format(
            minimal_identity=self.get_minimal_identity(),
            thoughts_text=thoughts_text,
            memory_context=memory_context,
            context_section=context_section,
            personality_section=personality_section,
            instruction=instruction,
            user_section=user_section
        )

    def _build_high_priority_prompt(
        self,
        thoughts_text: str,
        last_user_msg: str,
        urgency_level: int,
        context_parts: List[str],
        chat_context: Optional[str],
        is_chat_engagement: bool
    ) -> str:
        """TIER 2: High priority (7-8) WITH personality injection"""
        templates = self.parts.get_prompt_templates()
        
        instruction = self.parts.get_chat_engagement_instruction() if is_chat_engagement else self.get_urgency_instruction(urgency_level, False)
        
        game_instruction = ""
        if self.game_manager:
            game_response_instr = self.game_manager.get_active_game_instructions(stage='response')
            if game_response_instr:
                game_instruction = self.parts.format_section("GAME RESPONSE MODE", game_response_instr)
        
        memory_context = self._build_memory_context_sections()
        
        query = last_user_msg if last_user_msg else thoughts_text
        top_memory = self._get_top_long_term_memory(query)
        
        chat_section = ""
        if chat_context and not is_chat_engagement:
            chat_section = self.parts.format_section("LIVE CHAT", chat_context)
        
        user_section = ""
        if urgency_level >= 8 and last_user_msg and not is_chat_engagement:
            user_section = self.parts.format_user_message(last_user_msg, False)
        elif is_chat_engagement and last_user_msg:
            user_section = self.parts.format_user_message(last_user_msg, True)
        
        personality_section = ""
        if self.memory_search:
            query_parts = []
            if last_user_msg:
                query_parts.append(last_user_msg)
            if chat_context:
                chat_lines = chat_context.split('\n')
                query_parts.extend(chat_lines[-2:])
            
            query = " ".join(query_parts) if query_parts else thoughts_text
            
            examples = self.memory_search.get_response_generation_examples(context=query, k=2)
            if examples:
                personality_section = self.parts.format_section("PERSONALITY EXAMPLES", examples)
        
        return templates['high_priority'].format(
            minimal_identity=self.get_minimal_identity(),
            response_rules_compact=self.get_response_rules_compact(),
            game_instruction=game_instruction,
            thoughts_text=thoughts_text,
            memory_context=memory_context,
            top_memory=top_memory,
            chat_section=chat_section,
            personality_section=personality_section,
            instruction=instruction,
            user_section=user_section
        )

    def _build_standard_prompt(
        self,
        thoughts_text: str,
        last_user_msg: str,
        urgency_level: int,
        context_parts: List[str],
        chat_context: Optional[str],
        is_chat_engagement: bool
    ) -> str:
        """TIER 3: Standard (5-6) WITH personality injection"""
        templates = self.parts.get_prompt_templates()
        
        # Use centralized personality instead of hardcoded traits
        instructions = [
            self.personality.get_core_identity(),
            self.parts.get_standard_rules()
        ]
        
        has_chat = bool(chat_context)
        has_vision = self.detector.has_vision_data(context_parts, [thoughts_text])
        
        if is_chat_engagement:
            instructions.append(self.parts.get_chat_engagement_instruction())
        elif has_chat:
            instructions.append(self.get_chat_instruction())
        
        if self.game_manager:
            game_response_instr = self.game_manager.get_active_game_instructions(stage='response')
            if game_response_instr:
                instructions.append(f"## GAME RESPONSE MODE\n\n{game_response_instr}")
        
        if has_vision:
            instructions.append(self.parts.get_vision_instruction())
        
        if has_vision or (self.game_manager and self.game_manager.get_active_game()):
            instructions.append(self.shared.get_grounding_rules().content)
        
        memory_context = self._build_memory_context_sections()
        
        query = last_user_msg if last_user_msg else thoughts_text
        top_memory = self._get_top_long_term_memory(query)
        
        chat_section = ""
        if chat_context and not is_chat_engagement:
            chat_section = self.parts.format_section("LIVE CHAT", chat_context)
        
        user_section = ""
        if urgency_level >= 8 and last_user_msg and not is_chat_engagement:
            user_section = self.parts.format_user_message(last_user_msg, False)
        elif is_chat_engagement and last_user_msg:
            user_section = self.parts.format_user_message(last_user_msg, True)
        
        situation = "You are speaking to the people in the live chat via TTS. Address them naturally." if is_chat_engagement else self.get_urgency_instruction(urgency_level, False)
        
        personality_section = ""
        if self.memory_search:
            query_parts = []
            if last_user_msg:
                query_parts.append(last_user_msg)
            if chat_context:
                chat_lines = chat_context.split('\n')
                query_parts.extend(chat_lines[-3:])
            if not query_parts:
                query_parts.append(thoughts_text)
            
            query = " ".join(query_parts)
            
            examples = self.memory_search.get_response_generation_examples(context=query, k=3)
            if examples:
                personality_section = self.parts.format_section("PERSONALITY EXAMPLES", examples)
        
        return templates['standard'].format(
            instructions=chr(10).join(instructions),
            thoughts_text=thoughts_text,
            memory_context=memory_context,
            top_memory=top_memory,
            chat_section=chat_section,
            personality_section=personality_section,
            situation=situation,
            user_section=user_section
        )

    def _detect_response_contexts(
        self,
        thoughts_text: str,
        context_parts: List[str],
        user_text: str
    ) -> Set[str]:
        """Detect response contexts"""
        response_contexts = set()
        
        base_contexts = self.detector.detect_active_contexts(context_parts, [thoughts_text])
        response_contexts.update(base_contexts)
        
        user_lower = user_text.lower()
        
        if "?" in user_text or any(q in user_lower for q in ["what", "how", "why", "when", "where", "who"]):
            response_contexts.add('direct_question')
        
        if any(g in user_lower for g in ["hello", "hi ", "hey ", "greetings", "good morning", "good evening"]):
            response_contexts.add('greeting')
        
        return response_contexts
    
    # ========================================================================
    # LEGACY METHODS (for compatibility)
    # ========================================================================
    
    @staticmethod
    def get_response_identity() -> PromptSegment:
        """Legacy method - now uses centralized personality"""
        segments = ResponsePromptParts.get_legacy_segments()
        data = segments['response_identity']
        return PromptSegment(
            content=data['content'],
            priority=data['priority'],
            token_estimate=data['token_estimate'],
            category=data['category']
        )
    
    @staticmethod
    def get_response_rules() -> PromptSegment:
        """Legacy method for backward compatibility"""
        segments = ResponsePromptParts.get_legacy_segments()
        data = segments['response_rules']
        return PromptSegment(
            content=data['content'],
            priority=data['priority'],
            token_estimate=data['token_estimate'],
            category=data['category']
        )
    
    @staticmethod
    def get_communication_style() -> PromptSegment:
        """Legacy method - now uses centralized personality"""
        segments = ResponsePromptParts.get_legacy_segments()
        data = segments['communication_style']
        return PromptSegment(
            content=data['content'],
            priority=data['priority'],
            token_estimate=data['token_estimate'],
            category=data['category']
        )
    
    @staticmethod
    def get_context_guidance(context_type: str) -> Optional[PromptSegment]:
        """Legacy method for backward compatibility"""
        segments = ResponsePromptParts.get_legacy_segments()
        
        key_map = {
            'reminder_due': 'context_reminder_due',
            'chat_messages': 'context_chat_messages'
        }
        
        key = key_map.get(context_type)
        if not key:
            return None
        
        data = segments[key]
        return PromptSegment(
            content=data['content'],
            priority=data['priority'],
            token_estimate=data['token_estimate'],
            category=data['category']
        )
    
    @staticmethod
    def get_urgency_situation(urgency_level: int, has_reminders: bool = False) -> str:
        """Legacy method for backward compatibility"""
        constructor = ResponsePromptConstructor(None)
        return constructor.get_urgency_instruction(urgency_level, has_reminders)