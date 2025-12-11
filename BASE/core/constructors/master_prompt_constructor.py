# Filename: BASE/core/constructors/master_prompt_constructor.py
"""
Master Prompt Constructor
Orchestrates all prompt construction with unified format
Single source of truth for prompt assembly
NOW: Reflective mode handles startup automatically via thought_count parameter
"""
from typing import List, Optional, Any

from BASE.core.prompts.master_prompt_templates import MasterPromptTemplates
from BASE.core.utils.thought_chain_formatter import ThoughtChainFormatter
from BASE.core.modes.responsive_thought_constructor import ResponsiveThoughtConstructor
from BASE.core.modes.reflective_thought_constructor import ReflectiveThoughtConstructor
from BASE.core.modes.planning_thought_constructor import PlanningThoughtConstructor
from BASE.core.modes.response_mode_constructor import ResponseModeConstructor

from personality.prompts.personality_prompt_parts import PersonalityPromptParts


class MasterPromptConstructor:
    """
    Master constructor orchestrating all prompt types
    Ensures consistent structure: Personality → Thoughts → Mode → Context → Format
    """
    
    def __init__(
        self,
        memory_search=None,
        logger=None
    ):
        """
        Initialize master prompt constructor
        
        Args:
            memory_search: MemorySearch instance (optional)
            logger: Logger instance (optional)
        """
        self.memory_search = memory_search
        self.logger = logger
        
        # Initialize mode constructors
        self.responsive_constructor = ResponsiveThoughtConstructor(logger=logger)
        self.reflective_constructor = ReflectiveThoughtConstructor(
            memory_search=memory_search,
            logger=logger
        )
        self.planning_constructor = PlanningThoughtConstructor(logger=logger)
        self.response_constructor = ResponseModeConstructor(
            memory_search=memory_search,
            logger=logger
        )
        
        # Initialize utilities
        self.templates = MasterPromptTemplates()
        self.chain_formatter = ThoughtChainFormatter()
        self.personality = PersonalityPromptParts()
        
        if logger:
            logger.system("[MasterPromptConstructor] Initialized with unified format")
    
    # ========================================================================
    # THOUGHT PROMPTS
    # ========================================================================
    
    def build_responsive_thought_prompt(
        self,
        thought_chain: List[str],
        raw_events: List[Any],
        last_user_msg: Optional[str] = None,
        pending_actions: Optional[str] = None,
        additional_context: Optional[List[str]] = None
    ) -> str:
        """
        Build prompt for responsive thinking mode
        
        Args:
            thought_chain: List of recent thoughts
            raw_events: List of raw event objects
            last_user_msg: Last user message
            pending_actions: Summary of pending actions
            additional_context: Additional context strings
        
        Returns:
            Complete responsive thinking prompt
        """
        # 1. Personality (unified)
        personality = self.personality.get_unified_personality()
        
        # 2. Thought chain (formatted)
        formatted_chain = self.chain_formatter.format_thought_chain(thought_chain)
        
        # 3. Mode instructions
        mode_instructions = self.responsive_constructor.build_mode_instructions()
        
        # 4. Current context
        current_context = self.responsive_constructor.build_current_context(
            raw_events=raw_events,
            last_user_msg=last_user_msg,
            pending_actions=pending_actions,
            additional_context=additional_context
        )
        
        # 5. Response format
        response_format = self.responsive_constructor.build_response_format()
        
        # Assemble
        return self.templates.assemble_prompt(
            personality=personality,
            thought_chain=formatted_chain,
            mode_instructions=mode_instructions,
            current_context=current_context,
            response_format=response_format
        )
    
    def build_reflective_thought_prompt(
        self,
        thought_chain: List[str],
        ongoing_context: str,
        query: Optional[str] = None
    ) -> str:
        """
        Build prompt for reflective thinking mode
        AUTOMATIC STARTUP: Detects thought_count < 10 and loads startup context
        
        Args:
            thought_chain: List of recent thoughts
            ongoing_context: Current situation description
            query: Optional query for memory search (not used for startup)
        
        Returns:
            Complete reflective thinking prompt
        """
        # 1. Personality (unified)
        personality = self.personality.get_unified_personality()
        
        # 2. Thought chain (formatted)
        formatted_chain = self.chain_formatter.format_thought_chain(thought_chain)
        
        # CRITICAL: Detect startup based on thought count
        thought_count = len(thought_chain)
        is_startup = thought_count < 10
        
        if is_startup and self.logger:
            self.logger.system(
                f"[Reflective Prompt] STARTUP MODE detected ({thought_count} thoughts)"
            )
        
        # 3. Mode instructions (adapts to startup)
        mode_instructions = self.reflective_constructor.build_mode_instructions(
            is_startup=is_startup
        )
        
        # 4. Current context (automatically loads startup context if thought_count < 10)
        current_context = self.reflective_constructor.build_current_context(
            ongoing_context=ongoing_context,
            query=query,
            is_startup=is_startup,
            thought_count=thought_count
        )
        
        # 5. Response format (adapts to startup)
        response_format = self.reflective_constructor.build_response_format(
            is_startup=is_startup
        )
        
        # Assemble
        return self.templates.assemble_prompt(
            personality=personality,
            thought_chain=formatted_chain,
            mode_instructions=mode_instructions,
            current_context=current_context,
            response_format=response_format
        )
    
    def build_planning_thought_prompt(
        self,
        thought_chain: List[str],
        ongoing_context: str,
        time_context: Optional[str] = None
    ) -> str:
        """
        Build prompt for planning thinking mode
        
        Args:
            thought_chain: List of recent thoughts
            ongoing_context: Current situation description
            time_context: Optional time-based context
        
        Returns:
            Complete planning thinking prompt
        """
        # 1. Personality (unified)
        personality = self.personality.get_unified_personality()
        
        # 2. Thought chain (formatted)
        formatted_chain = self.chain_formatter.format_thought_chain(thought_chain)
        
        # 3. Mode instructions
        mode_instructions = self.planning_constructor.build_mode_instructions()
        
        # 4. Current context
        current_context = self.planning_constructor.build_current_context(
            ongoing_context=ongoing_context,
            time_context=time_context
        )
        
        # 5. Response format
        response_format = self.planning_constructor.build_response_format()
        
        # Assemble
        return self.templates.assemble_prompt(
            personality=personality,
            thought_chain=formatted_chain,
            mode_instructions=mode_instructions,
            current_context=current_context,
            response_format=response_format
        )
    
    # ========================================================================
    # RESPONSE PROMPTS
    # ========================================================================
    
    def build_response_prompt(
        self,
        thought_chain: List[str],
        urgency_level: int = 5,
        user_text: Optional[str] = None,
        chat_context: Optional[str] = None,
        additional_context: Optional[List[str]] = None,
        is_chat_engagement: bool = False,
        has_reminders: bool = False,
        use_compact: bool = False
    ) -> str:
        """
        Build prompt for spoken response generation
        
        Args:
            thought_chain: List of recent thoughts
            urgency_level: Urgency level (1-10)
            user_text: Current user input
            chat_context: Live chat context
            additional_context: Additional context strings
            is_chat_engagement: Whether responding to chat
            has_reminders: Whether urgent reminders present
            use_compact: Whether to use compact format
        
        Returns:
            Complete response generation prompt
        """
        # 1. Personality (unified)
        personality = self.personality.get_unified_personality()
        
        # 2. Thought chain (formatted, possibly compact)
        if use_compact:
            formatted_chain = self.chain_formatter.format_compact_chain(thought_chain, max_thoughts=5)
        else:
            formatted_chain = self.chain_formatter.format_thought_chain(thought_chain)
        
        # 3. Mode instructions
        mode_instructions = self.response_constructor.build_mode_instructions(
            urgency_level=urgency_level,
            is_chat_engagement=is_chat_engagement,
            has_reminders=has_reminders
        )
        
        # 4. Response format
        response_format = self.response_constructor.build_response_format()
        
        # Use compact format for high urgency
        if use_compact or urgency_level >= 9:
            return self.templates.assemble_compact_prompt(
                personality=personality,
                thought_chain=formatted_chain,
                mode_instructions=mode_instructions,
                response_format=response_format
            )
        
        # 5. Current context (full format)
        current_context = self.response_constructor.build_current_context(
            user_text=user_text,
            chat_context=chat_context,
            additional_context=additional_context,
            is_chat_engagement=is_chat_engagement
        )
        
        # Assemble full format
        return self.templates.assemble_prompt(
            personality=personality,
            thought_chain=formatted_chain,
            mode_instructions=mode_instructions,
            current_context=current_context,
            response_format=response_format
        )