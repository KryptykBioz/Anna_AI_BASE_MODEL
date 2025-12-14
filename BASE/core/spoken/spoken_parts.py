# Filename: BASE/core/spoken/spoken_parts.py
"""
Spoken Response Prompt Parts
=============================
Contains reusable prompt components for spoken response generation
"""

from personality.bot_info import username


class SpokenPromptParts:
    """Reusable prompt parts for spoken responses"""
    
    @staticmethod
    def get_output_format() -> str:
        """Output format instructions"""
        return """
## RESPOND

Respond naturally in 1-2 sentences. Just write your response directly - no XML tags needed.

**Rules:**
- Maximum 2-3 sentences
- Natural conversational tone
- No labels, timestamps, or meta-text
- Base response on your recent thoughts"""
    
    @staticmethod
    def get_critical_guidance() -> str:
        """Guidance for critical priority responses"""
        return f"""
## CRITICAL RESPONSE REQUIRED

**Respond immediately to {username}.**

This is urgent - acknowledge directly and naturally. Keep it brief (1-2 sentences)."""
    
    @staticmethod
    def get_high_priority_guidance() -> str:
        """Guidance for high priority responses"""
        return f"""
## HIGH PRIORITY RESPONSE

**{username} asked you directly or mentioned you.**

Answer clearly and directly. Be concise but helpful (1-2 sentences)."""
    
    @staticmethod
    def get_chat_engagement_guidance() -> str:
        """Guidance for chat engagement responses"""
        return """
## LIVE CHAT ENGAGEMENT

**You are responding via spoken TTS to the live chat.**

Guidelines:
- Address chat members by name when appropriate
- Keep responses conversational and friendly
- You can address up to 2 people in one response
- Sound natural - this will be spoken aloud
- 1-2 sentences maximum"""
    
    @staticmethod
    def get_standard_guidance() -> str:
        """Guidance for standard responses"""
        return """
## RESPOND NATURALLY

Based on your recent thoughts and the current situation, respond in 1-2 sentences.

Guidelines:
- Speak naturally in your own voice
- Keep it conversational
- Don't repeat what you just said
- Base response on your thoughts"""
    
    @staticmethod
    def get_response_rules() -> str:
        """General response rules"""
        return """
## RESPONSE RULES

**Style:**
- Speak naturally and conversationally
- Use your personality and voice
- Keep responses concise (1-2 sentences)
- No emojis, no labels, no meta-text

**Content:**
- Base responses on your recent thoughts
- Don't repeat yourself
- Don't invent information
- Acknowledge uncertainty if needed"""