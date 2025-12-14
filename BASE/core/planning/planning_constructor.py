# Filename: BASE/core/planning/planning_constructor.py
"""
Planning Thinking Prompt Constructor - FIXED
=============================================
Constructs prompts for goal-setting and future-oriented thinking.

FIX: Now properly retrieves and includes tool instructions from persistence manager

Prompt Components:
1. Personality (core identity + proactive style)
2. Thought chain (recent thoughts for continuity)
3. Tool list OR retrieved tool instructions (based on persistence)
4. Current situation (what's happening now)
5. Response guidance (how to plan ahead)

Focus: Looking forward, anticipating needs, setting goals
"""

from typing import List, Optional
from BASE.core.planning.planning_parts import PlanningPromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts
from personality.bot_info import username


class PlanningConstructor:
    """Constructs prompts for planning thinking"""
    
    def __init__(self, tool_manager=None, logger=None):
        """
        Initialize planning constructor
        
        Args:
            tool_manager: ToolManager instance for tool instructions
            logger: Optional logger instance
        """
        self.tool_manager = tool_manager
        self.logger = logger
        
        # Initialize prompt parts
        self.parts = PlanningPromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_planning_prompt(
        self,
        thought_chain: List[str],
        ongoing_context: str,
        time_context: Optional[str] = None
    ) -> str:
        """
        Build complete planning thinking prompt
        
        Args:
            thought_chain: Recent thoughts (for continuity)
            ongoing_context: Current situation description
            time_context: Optional time-based context (e.g., "5 minutes since user input")
        
        Returns:
            Complete planning thinking prompt
        """
        sections = []
        
        # 1. Personality injection (core identity)
        sections.append(self.personality.get_personality_injection('thought'))
        
        # 2. Recent thoughts (for continuity)
        sections.append(self._format_thought_chain(thought_chain))
        
        # 3. Mode instructions
        sections.append(self.parts.get_mode_instructions())
        
        # 4. Tool instructions (FIXED: Check persistence and include detailed instructions)
        if self.tool_manager:
            tool_section = self._get_tool_instructions_section()
            if tool_section:
                sections.append(tool_section)
        
        # 5. Current situation
        sections.append(self._format_current_situation(ongoing_context, time_context))
        
        # 6. Output format
        sections.append(self.parts.get_output_format())
        
        prompt = "\n".join(sections)
        
        if self.logger:
            self.logger.prompt(f"[Planning Thinking Prompt]\n{prompt}")
        
        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format recent thoughts"""
        if not thoughts:
            return "\n## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        recent = thoughts[-5:]
        formatted = "\n".join([f"- {t}" for t in recent])
        
        return f"\n## YOUR RECENT THOUGHTS\n\n{formatted}"
    
    def _get_tool_instructions_section(self) -> str:
        """
        Get tool instructions section - FIXED
        Checks instruction persistence and includes detailed instructions when available
        
        Returns:
            Tool section (either minimal list or detailed instructions)
        """
        if not self.tool_manager:
            return ""
        
        # Check if instruction persistence manager exists
        if not hasattr(self.tool_manager, 'instruction_persistence_manager'):
            # Fallback to minimal list
            return self.tool_manager._build_tool_list()
        
        persistence_manager = self.tool_manager.instruction_persistence_manager
        
        # Get tools with active instructions
        tools_with_instructions = persistence_manager.get_active_tool_names()
        
        if not tools_with_instructions:
            # No active instructions - return minimal tool list
            return self.tool_manager._build_tool_list()
        
        # Build detailed instructions for tools with active retrievals
        return self._build_detailed_tool_instructions(tools_with_instructions)
    
    def _build_detailed_tool_instructions(self, tool_names: List[str]) -> str:
        """
        Build detailed instructions for tools with active retrievals
        
        Args:
            tool_names: List of tools with active instruction persistence
        
        Returns:
            Formatted detailed tool instructions
        """
        # Import the instruction builder
        from BASE.handlers.tool_instruction_builder import ToolInstructionBuilder
        
        # Create builder instance
        builder = ToolInstructionBuilder(
            tool_manager=self.tool_manager,
            logger=self.logger
        )
        
        # Build detailed instructions
        detailed_instructions = builder.build_retrieved_tool_instructions(tool_names)
        
        if self.logger:
            self.logger.system(
                f"[Planning Constructor] Including detailed instructions for "
                f"{len(tool_names)} tools: {', '.join(tool_names)}"
            )
        
        return detailed_instructions
    
    def _format_current_situation(
        self,
        ongoing_context: str,
        time_context: Optional[str]
    ) -> str:
        """Format current situation and time context"""
        sections = []
        
        sections.append("## CURRENT SITUATION\n")
        sections.append(ongoing_context if ongoing_context else "Open time for planning")
        
        if time_context:
            sections.append("\n## TIME CONTEXT\n")
            sections.append(time_context)
        elif ongoing_context == "Open time for planning":
            # Provide helpful default context
            sections.append("\n## TIME CONTEXT\n")
            sections.append(f"{username} is not currently active. Good time to plan ahead.")
        
        return "\n".join(sections)