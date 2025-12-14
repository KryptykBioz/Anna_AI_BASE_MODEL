# Filename: BASE/core/responsive/responsive_constructor.py
"""
Responsive Thinking Prompt Constructor - FIXED
===============================================
Constructs prompts for processing incoming data and generating reactive thoughts.

FIX: Now properly retrieves and includes tool instructions from persistence manager

Prompt Components:
1. Personality (core identity + thinking style)
2. Thought chain (recent thoughts for continuity)
3. Tool list OR retrieved tool instructions (based on persistence)
4. Incoming data (events to process)
5. Response guidance (how to think about events)

Focus: Real-time processing of new information
"""

from typing import List, Optional, Any
from BASE.core.responsive.responsive_parts import ResponsivePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts
from personality.bot_info import username


class ResponsiveConstructor:
    """Constructs prompts for responsive thinking"""
    
    def __init__(self, tool_manager=None, logger=None):
        """
        Initialize responsive constructor
        
        Args:
            tool_manager: ToolManager instance for tool instructions
            logger: Optional logger instance
        """
        self.tool_manager = tool_manager
        self.logger = logger
        
        # Initialize prompt parts
        self.parts = ResponsivePromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_responsive_prompt(
        self,
        thought_chain: List[str],
        raw_events: List[Any],
        context_parts: List[str] = None,
        last_user_msg: Optional[str] = None,
        pending_actions: Optional[str] = None,
        has_vision: bool = False
    ) -> str:
        """
        Build complete responsive thinking prompt
        
        Args:
            thought_chain: Recent thoughts (for continuity)
            raw_events: Incoming events to process
            context_parts: Additional context
            last_user_msg: Last user message
            pending_actions: Summary of pending tool actions
            has_vision: Whether vision data is present
        
        Returns:
            Complete responsive thinking prompt
        """
        context_parts = context_parts or []
        
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
        
        # 5. Incoming data (events to process)
        sections.append(self._format_incoming_data(raw_events))
        
        # 6. Additional context
        if last_user_msg:
            sections.append(f"\n## LAST USER MESSAGE\n\n**{username}:** \"{last_user_msg}\"")
        
        if pending_actions and pending_actions.strip():
            sections.append(f"\n## PENDING ACTIONS\n\n{pending_actions}")
        
        if context_parts:
            sections.append(self._format_additional_context(context_parts))
        
        # 7. Grounding rules (especially important for vision)
        if has_vision:
            sections.append(self.parts.get_vision_grounding())
        
        sections.append(self.parts.get_grounding_rules())
        
        # 8. Output format
        sections.append(self.parts.get_output_format())
        
        prompt = "\n".join(sections)
        
        if self.logger:
            self.logger.prompt(f"[Responsive Thinking Prompt]\n{prompt}")
        
        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format recent thoughts"""
        if not thoughts:
            return "\n## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        recent = thoughts[-10:]
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
                f"[Responsive Constructor] Including detailed instructions for "
                f"{len(tool_names)} tools: {', '.join(tool_names)}"
            )
        
        return detailed_instructions
    
    def _format_incoming_data(self, raw_events: List[Any]) -> str:
        """Format incoming events"""
        if not raw_events:
            return "\n## NEW INCOMING DATA\n\nNo new data."
        
        lines = ["\n## NEW INCOMING DATA\n"]
        
        for i, event in enumerate(raw_events, 1):
            source = getattr(event, 'source', 'unknown')
            data = getattr(event, 'data', str(event))
            lines.append(f"**[Event {i}]** `{source}`: {data}")
        
        return "\n".join(lines)
    
    def _format_additional_context(self, context_parts: List[str]) -> str:
        """Format additional context"""
        formatted = "\n\n".join(context_parts)
        return f"\n## ADDITIONAL CONTEXT\n\n{formatted}"