# Filename: BASE/core/constructors/modes/planning_thought_constructor.py
"""
Planning Thought Mode Constructor
Handles future planning and anticipation
Isolated mode - can be modified/tested independently
"""
from typing import Optional


class PlanningThoughtConstructor:
    """
    Constructs mode-specific sections for planning thinking
    Anticipates future needs and plans ahead
    """
    
    def __init__(self, logger=None):
        """
        Initialize planning thought constructor
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
    
    def build_mode_instructions(self) -> str:
        """
        Build mode-specific instructions for planning thinking
        
        Returns:
            Markdown-formatted instructions
        """
        return """## Planning Thinking Mode

You are planning ahead and anticipating future needs.

### Your Task:
- Assess the current trajectory
- Identify likely next events or needs
- Generate ONE forward-looking thought (15-50 words)
- Plan actionable next steps

### Guidelines:
- Think in your own voice and personality
- Be proactive and helpful
- Consider what the user might need
- Be specific about what you should prepare"""
    
    def build_current_context(
        self,
        ongoing_context: str,
        time_context: Optional[str] = None
    ) -> str:
        """
        Build current context for planning thinking
        
        Args:
            ongoing_context: Current situation description
            time_context: Optional time-based context
        
        Returns:
            Markdown-formatted context
        """
        sections = []
        
        # Current situation
        sections.append("## CURRENT SITUATION\n")
        sections.append(ongoing_context if ongoing_context else "Open time for planning")
        
        # Time context (if provided)
        if time_context:
            sections.append("\n## TIME CONTEXT\n")
            sections.append(time_context)
        
        return "\n".join(sections)
    
    def build_response_format(self) -> str:
        """
        Build expected response format for planning thinking
        
        Returns:
            Markdown-formatted response format
        """
        return """## Expected Output Format
```xml
<think>Your forward-looking planning thought</think>
<action_list>[]</action_list>
```

### Rules:
- ONE planning thought (15-50 words)
- Focus on future needs and preparation
- Be proactive and action-oriented
- Use your own voice and personality"""