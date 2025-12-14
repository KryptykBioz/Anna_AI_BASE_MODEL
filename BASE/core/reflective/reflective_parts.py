# Filename: BASE/core/reflective/reflective_parts.py
"""
Reflective Thinking Prompt Parts
=================================
Contains reusable prompt components for reflective thinking
"""


class ReflectivePromptParts:
    """Reusable prompt parts for reflective thinking"""
    
    @staticmethod
    def get_mode_instructions() -> str:
        """Standard reflective mode instructions"""
        return """
## REFLECTIVE THINKING MODE

You are reflecting on past experiences and connecting them to your current situation.

**Your Task:**
- Review the memory context provided
- Identify relevant patterns or lessons from the past
- Generate ONE reflective thought (15-50 words)
- Connect past experiences to present naturally

**Guidelines:**
- Think in your own voice and personality
- Make genuine connections, not forced ones
- Be specific about what you remember and why it matters
- Sound thoughtful, not robotic"""
    
    @staticmethod
    def get_startup_instructions() -> str:
        """Startup mode instructions"""
        return """
## STARTUP INITIALIZATION MODE

You are waking up and orienting yourself after being offline.

**Your Task:**
- Review the provided context from your recent past
- Orient yourself to what's been happening
- Generate ONE initial thought (15-50 words) about your current state
- Acknowledge what you remember and what you should focus on

**Guidelines:**
- Think in your own voice and personality
- Be genuine about resuming after downtime
- Connect to recent memories naturally
- Set a positive, engaged tone"""
    
    @staticmethod
    def get_output_format(is_startup: bool = False) -> str:
        """Output format instructions"""
        if is_startup:
            return """
## EXPECTED OUTPUT FORMAT

```xml
<think>Your initial orientation thought</think>
<action_list>[]</action_list>
```

**Rules:**
- ONE startup thought (15-50 words)
- Acknowledge what you remember from context
- Set a positive, engaged tone
- Use your own voice and personality"""
        
        return """
## EXPECTED OUTPUT FORMAT

```xml
<think>Your reflective thought connecting past to present</think>
<action_list>[]</action_list>
```

**Rules:**
- ONE reflective thought (15-50 words)
- Connect past memories to current situation naturally
- Use your own voice and personality
- Be specific and insightful
- Can include tool actions if needed: `[{"tool": "tool_name", "args": {...}}]`"""
    
    @staticmethod
    def get_grounding_rules() -> str:
        """Grounding rules for reflection"""
        return """
## GROUNDING RULES

**When reflecting on memories:**
- Only reference memories explicitly provided in context
- Don't invent past events or experiences
- Acknowledge if memories are unclear or incomplete
- Connect past to present thoughtfully but accurately

**Hallucination prevention:**
- "I remember X" only if X is in the memory context
- "Last time Y" only if Y is shown in memories
- If uncertain about past details, say "I think" or "I recall"
- Don't fill in gaps with invented details"""