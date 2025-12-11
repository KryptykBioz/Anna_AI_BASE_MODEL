# Filename: BASE/core/constructors/thought_prompt_builder.py
"""
Thought Prompt Builder - REFACTORED
NOW: Thin wrapper delegating to MasterPromptConstructor
Maintains backward compatibility while using new unified system
"""
from typing import List, Optional, Dict, Any

from BASE.core.constructors.master_prompt_constructor import MasterPromptConstructor


class ThoughtPromptBuilder:
    """
    Thought prompt builder - thin wrapper for backward compatibility
    Delegates all construction to MasterPromptConstructor
    """
    
    def __init__(
        self,
        controls_module,
        memory_search=None,
        tool_manager=None,
        tool_execution_manager=None,
        instruction_persistence_manager=None,
        logger=None
    ):
        """
        Initialize thought prompt builder
        
        Args:
            controls_module: Controls module (unused, for compatibility)
            memory_search: MemorySearch instance
            tool_manager: ToolManager instance
            tool_execution_manager: Legacy name (backward compatibility)
            instruction_persistence_manager: InstructionPersistenceManager
            logger: Logger instance
        """
        self.controls = controls_module
        self.memory_search = memory_search
        self.tool_manager = tool_manager or tool_execution_manager
        self.instruction_persistence_manager = instruction_persistence_manager
        self.logger = logger
        
        # Initialize master constructor (does all the work)
        self.master = MasterPromptConstructor(
            memory_search=memory_search,
            logger=logger
        )
        
        if logger:
            logger.system("[ThoughtPromptBuilder] Initialized as wrapper for MasterPromptConstructor")
    
    # ========================================================================
    # PUBLIC API - Maintains backward compatibility
    # ========================================================================
    
    def build_reactive_thinking_prompt(
        self,
        raw_events: List[Any],
        recent_thoughts: List[str],
        context_parts: List[str],
        last_user_msg: str = "",
        pending_actions: str = "",
        has_vision: bool = False,
        has_urgent_reminders: bool = False,
        game_context_summary: str = ""
    ) -> str:
        """
        Build responsive thinking prompt
        Delegates to MasterPromptConstructor.build_responsive_thought_prompt()
        
        Args:
            raw_events: List of raw events to process
            recent_thoughts: List of recent thought strings
            context_parts: Additional context strings
            last_user_msg: Last user message
            pending_actions: Pending actions summary
            has_vision: Whether vision data present (unused)
            has_urgent_reminders: Whether urgent reminders present (unused)
            game_context_summary: Game context (unused)
        
        Returns:
            Complete responsive thinking prompt
        """
        return self.master.build_responsive_thought_prompt(
            thought_chain=recent_thoughts,
            raw_events=raw_events,
            last_user_msg=last_user_msg,
            pending_actions=pending_actions,
            additional_context=context_parts
        )
    
    def build_standard_proactive_prompt(
        self,
        recent_thoughts: List[str],
        ongoing_context: str,
        memory_context: str = "",
        repetition_warning: str = "",
        tool_hints: Optional[List[str]] = None,
        consecutive_count: int = 0
    ) -> str:
        """
        Build reflective thinking prompt
        Delegates to MasterPromptConstructor.build_reflective_thought_prompt()
        
        Args:
            recent_thoughts: List of recent thought strings
            ongoing_context: Current situation description
            memory_context: Memory context (unused - retrieved internally)
            repetition_warning: Repetition warning (unused)
            tool_hints: Tool hints (unused)
            consecutive_count: Consecutive count (unused)
        
        Returns:
            Complete reflective thinking prompt
        """
        # Extract query from ongoing context for memory search
        query = ongoing_context[:100] if ongoing_context else None
        
        return self.master.build_reflective_thought_prompt(
            thought_chain=recent_thoughts,
            ongoing_context=ongoing_context,
            query=query
        )
    
    def build_memory_reflection_prompt(
        self,
        recent_thoughts: List[str],
        ongoing_context: str,
        memory_context: str
    ) -> str:
        """
        Build memory reflection prompt
        Delegates to MasterPromptConstructor.build_reflective_thought_prompt()
        
        Args:
            recent_thoughts: List of recent thought strings
            ongoing_context: Current situation description
            memory_context: Memory context for query
        
        Returns:
            Complete memory reflection prompt
        """
        # Extract query from memory context
        query = memory_context[:100] if memory_context else ongoing_context[:100]
        
        return self.master.build_reflective_thought_prompt(
            thought_chain=recent_thoughts,
            ongoing_context=ongoing_context,
            query=query
        )
    
    def build_future_planning_prompt(
        self,
        recent_thoughts: List[str],
        ongoing_context: str,
        time_context: str
    ) -> str:
        """
        Build planning thinking prompt
        Delegates to MasterPromptConstructor.build_planning_thought_prompt()
        
        Args:
            recent_thoughts: List of recent thought strings
            ongoing_context: Current situation description
            time_context: Time-based context
        
        Returns:
            Complete planning thinking prompt
        """
        return self.master.build_planning_thought_prompt(
            thought_chain=recent_thoughts,
            ongoing_context=ongoing_context,
            time_context=time_context
        )
    
    def build_startup_thinking_prompt(
        self,
        startup_context_parts: List[str]
    ) -> str:
        """
        Build startup thinking prompt
        Uses reflective mode with startup context
        
        Args:
            startup_context_parts: List of startup context strings
        
        Returns:
            Complete startup thinking prompt
        """
        from datetime import datetime
        
        current_time = datetime.now().strftime("%A, %B %d at %I:%M %p")
        ongoing_context = f"System startup at {current_time}\n\n" + "\n".join(startup_context_parts)
        
        return self.master.build_reflective_thought_prompt(
            thought_chain=[],  # No thoughts yet
            ongoing_context=ongoing_context,
            query="startup initialization"
        )
    
    # ========================================================================
    # DEPENDENCY INJECTION
    # ========================================================================
    
    def set_tool_manager(self, tool_manager):
        """Inject tool manager (no-op for now)"""
        self.tool_manager = tool_manager
        if self.logger:
            self.logger.system("[ThoughtPromptBuilder] Tool manager set (not used in new system)")
    
    def set_instruction_persistence_manager(self, persistence_manager):
        """Inject persistence manager (no-op for now)"""
        self.instruction_persistence_manager = persistence_manager
        if self.logger:
            self.logger.system("[ThoughtPromptBuilder] Persistence manager set (not used in new system)")
    
    def validate_setup(self) -> Dict[str, bool]:
        """Validate setup"""
        return {
            'has_memory_search': self.memory_search is not None,
            'has_tool_manager': self.tool_manager is not None,
            'has_master_constructor': self.master is not None
        }