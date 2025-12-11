# Filename: BASE/core/prompts/thought_prompt_parts.py
"""
Thought Prompt Parts - REFACTORED
Mode-specific details only - no personality or generic content
"""

from typing import Dict, Optional, List
from personality.bot_info import agentname, username


class ThoughtPromptParts:
    """Container for mode-specific thought prompt components"""
    
    # ========================================================================
    # TOOL SECTION (Generic - not mode-specific)
    # ========================================================================
    
    @staticmethod
    def get_no_tools_message() -> str:
        return """## NO TOOLS CURRENTLY AVAILABLE

You currently have no external tools available. Focus on internal reasoning."""
    
    @staticmethod
    def get_available_tools_header(count: int) -> str:
        return f"""## AVAILABLE TOOLS

You have access to **{count}** tool(s). Use them when appropriate."""
    
    # ========================================================================
    # OUTPUT FORMAT (Generic)
    # ========================================================================
    
    @staticmethod
    def get_output_format() -> str:
        return """# OUTPUT FORMAT - REQUIRED
```xml
<thoughts>
[1] <thought about event 1>
[2] <thought about event 2>
</thoughts>

<think>Strategic planning thought</think>

<action_list>[]</action_list>
```

**CRITICAL:**
- Use XML tags (NOT markdown)
- Empty array if no actions: `<action_list>[]</action_list>`"""
    
    # ========================================================================
    # LEGACY METHODS (for backward compatibility)
    # ========================================================================
    
    @staticmethod
    def get_chat_awareness_section(agentname: str) -> str:
        """DEPRECATED: Chat is now a tool"""
        return ""
    
    @staticmethod
    def get_proactive_tool_guidance() -> str:
        """DEPRECATED: Tools now modular"""
        return ""