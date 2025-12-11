# Filename: BASE/core/constructors/modes/responsive_thought_constructor.py
"""
Responsive Thought Mode Constructor
Handles thought generation in response to incoming passive data
Isolated mode - can be modified/tested independently
"""
from typing import List, Optional, Any


class ResponsiveThoughtConstructor:
    """
    Constructs mode-specific sections for responsive thinking
    Processes incoming events/data into internal thoughts
    """
    
    def __init__(self, logger=None):
        """
        Initialize responsive thought constructor
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
    
    def build_mode_instructions(self) -> str:
        """
        Build mode-specific instructions for responsive thinking
        
        Returns:
            Markdown-formatted instructions
        """
        return """## Responsive Thinking Mode

You are processing new incoming data and generating internal thoughts about it.

### Your Task:
- Observe what happened in each event
- Generate one natural thought per event
- Thoughts should be 1-2 sentences each
- Think in your own voice and personality

### Guidelines:
- Base thoughts ONLY on data explicitly provided
- Don't invent or assume information
- Stay grounded in what you directly observe
- Be genuine and natural in your thinking"""
    
    def build_current_context(
        self,
        raw_events: List[Any],
        last_user_msg: Optional[str] = None,
        pending_actions: Optional[str] = None,
        additional_context: Optional[List[str]] = None
    ) -> str:
        """
        Build current context for responsive thinking
        
        Args:
            raw_events: List of raw event objects
            last_user_msg: Last user message (if any)
            pending_actions: Summary of pending actions
            additional_context: Additional context strings
        
        Returns:
            Markdown-formatted context
        """
        sections = []
        
        # Events section (required)
        if raw_events:
            sections.append("## NEW INCOMING DATA\n")
            for i, event in enumerate(raw_events, 1):
                source = getattr(event, 'source', 'unknown')
                data = getattr(event, 'data', str(event))
                sections.append(f"**[Event {i}]** `{source}`: {data}")
        
        # Last user message (if present)
        if last_user_msg:
            from personality.bot_info import username
            sections.append(f"\n## LAST USER MESSAGE\n\n**{username}:** \"{last_user_msg}\"")
        
        # Pending actions (if any)
        if pending_actions and pending_actions.strip():
            sections.append(f"\n## PENDING ACTIONS\n\n{pending_actions}")
        
        # Additional context (if any)
        if additional_context:
            sections.append("\n## ADDITIONAL CONTEXT\n")
            sections.append("\n\n".join(additional_context))
        
        return "\n".join(sections) if sections else "## CURRENT CONTEXT\n\nNo additional context."
    
    def build_response_format(self) -> str:
        """
        Build expected response format for responsive thinking
        
        Returns:
            Markdown-formatted response format
        """
        return """## Expected Output Format
```xml
<thoughts>
[1] Your thought about event 1
[2] Your thought about event 2
[3] Your thought about event 3
</thoughts>

<think>Optional strategic planning thought</think>

<action_list>[]</action_list>
```

### Rules:
- Generate one numbered thought per event
- Each thought should be 1-2 sentences
- Use `<action_list>[]</action_list>` if no actions needed
- Actions are optional - only include if you want to use a tool
- Strategic plan is optional - only if you're planning ahead"""