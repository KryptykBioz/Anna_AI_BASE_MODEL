# Filename: BASE/core/planning/planning_parts.py
"""
Planning Thinking Prompt Parts
================================
Contains reusable prompt components for planning thinking
"""


class PlanningPromptParts:
    """Reusable prompt parts for planning thinking"""
    
    @staticmethod
    def get_mode_instructions() -> str:
        """Planning mode instructions"""
        return """
## PLANNING THINKING MODE

You are planning ahead and anticipating future needs.

**Your Task:**
- Assess the current trajectory
- Identify likely next events or needs
- Generate ONE forward-looking thought (15-50 words)
- Plan actionable next steps

**Guidelines:**
- Think in your own voice and personality
- Be proactive and helpful
- Consider what the user might need
- Be specific about what you should prepare"""
    
    @staticmethod
    def get_output_format() -> str:
        """Output format instructions"""
        return """
## EXPECTED OUTPUT FORMAT

```xml
<think>Your forward-looking planning thought</think>
<action_list>[]</action_list>
```

**Rules:**
- ONE planning thought (15-50 words)
- Focus on future needs and preparation
- Be proactive and action-oriented
- Use your own voice and personality
- Can include tool actions if needed: `[{"tool": "tool_name", "args": {...}}]`"""
    
    @staticmethod
    def get_planning_guidelines() -> str:
        """Additional planning guidelines"""
        return """
## PLANNING GUIDELINES

**Good planning thoughts:**
- "Given the current situation, I should prepare X"
- "If Y happens next, I'll need Z ready"
- "To accomplish A, I should first do B"
- "Thinking ahead, I could set up X for when user returns"

**Avoid:**
- Repeating recent thoughts
- Generic observations without actionable plans
- Planning without considering current context
- Aimless speculation

**Focus on:**
- Anticipating user needs
- Preparing tools or information
- Setting up helpful actions
- Maintaining conversation readiness"""
    
    @staticmethod
    def get_grounding_rules() -> str:
        """Grounding rules for planning"""
        return """
## GROUNDING RULES

**When planning:**
- Base plans on current context and recent activity
- Don't invent user needs or preferences
- Acknowledge uncertainty about future events
- Plan realistically based on available tools

**Hallucination prevention:**
- "User might need X" only if context suggests it
- "I should prepare Y" only if Y is feasible
- Don't plan for events you have no reason to expect
- Don't assume user intentions without evidence"""