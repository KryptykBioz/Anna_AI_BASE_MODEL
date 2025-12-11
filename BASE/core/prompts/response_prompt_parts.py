# Filename: BASE/core/prompts/response_prompt_parts.py
"""
Response Prompt Parts - REFACTORED
Mode-specific details only - no personality or generic content
"""

from typing import Dict
from personality.bot_info import agentname, username


class ResponsePromptParts:
    """Container for mode-specific response prompt components"""
    
    # ========================================================================
    # URGENCY INSTRUCTIONS (Mode-specific)
    # ========================================================================
    
    @staticmethod
    def get_urgency_instructions() -> Dict[str, str]:
        """
        Returns dict mapping urgency conditions to instruction text
        """
        return {
            'reminder': f"**URGENT:** Acknowledge reminder immediately: 'Hey {username}, reminder: [description]!'",
            '9+': f"**RESPOND:** {username} mentioned you or asked directly. Answer naturally.",
            '8': f"**ANSWER:** {username} asked a question. Be clear and direct.",
            '7': "**REACT:** High priority event. Comment appropriately.",
            '5+': "**RESPOND:** Notable situation. Say something meaningful.",
            'default': "**COMMENT:** Natural opportunity to speak based on your thoughts."
        }
    
    @staticmethod
    def get_chat_engagement_instruction() -> str:
        """Specialized chat engagement instruction"""
        return """**LIVE CHAT ENGAGEMENT:** Responding via spoken TTS.

- Address chat members by name when appropriate
- Keep responses conversational and friendly
- You can address up to 2 people in one response
- Sound natural - this will be spoken aloud"""
    
    # ========================================================================
    # FORMATTING UTILITIES
    # ========================================================================
    
    @staticmethod
    def format_section(title: str, content: str) -> str:
        """Helper to format sections consistently"""
        if not content:
            return ""
        return f"\n\n## {title}\n\n{content}"
    
    @staticmethod
    def format_user_message(msg: str, is_chat_engagement: bool = False) -> str:
        """Format user message section"""
        if not msg:
            return ""
        
        if is_chat_engagement:
            return f'\n\n## CHAT TO ADDRESS\n\n{msg}'
        else:
            return f'\n\n**{username}:** "{msg}"'