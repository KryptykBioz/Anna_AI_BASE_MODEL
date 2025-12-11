# Filename: BASE/core/constructors/modes/response_mode_constructor.py
"""
Response Mode Constructor
Handles spoken response generation
Isolated mode - can be modified/tested independently
"""
from typing import Optional, List


class ResponseModeConstructor:
    """
    Constructs mode-specific sections for spoken response generation
    Synthesizes natural speech based on thoughts
    """
    
    def __init__(self, memory_search=None, logger=None):
        """
        Initialize response mode constructor
        
        Args:
            memory_search: MemorySearch instance (optional)
            logger: Optional logger instance
        """
        self.memory_search = memory_search
        self.logger = logger
    
    def build_mode_instructions(
        self,
        urgency_level: int = 5,
        is_chat_engagement: bool = False,
        has_reminders: bool = False
    ) -> str:
        """
        Build mode-specific instructions for response generation
        
        Args:
            urgency_level: Urgency level (1-10)
            is_chat_engagement: Whether responding to chat
            has_reminders: Whether urgent reminders present
        
        Returns:
            Markdown-formatted instructions
        """
        from personality.bot_info import username
        
        if has_reminders:
            instruction = f"**URGENT:** Acknowledge reminder immediately: 'Hey {username}, reminder: [description]!'"
        elif is_chat_engagement:
            instruction = self._get_chat_engagement_instruction()
        elif urgency_level >= 9:
            instruction = f"**RESPOND:** {username} mentioned you or asked directly. Answer naturally."
        elif urgency_level == 8:
            instruction = f"**ANSWER:** {username} asked a question. Be clear and direct."
        elif urgency_level == 7:
            instruction = "**REACT:** High priority event. Comment appropriately."
        elif urgency_level >= 5:
            instruction = "**RESPOND:** Notable situation. Say something meaningful."
        else:
            instruction = "**COMMENT:** Natural opportunity to speak based on your thoughts."
        
        return f"""## Response Generation Mode

You are generating a natural spoken response based on your recent thoughts.

### Your Task:
{instruction}

### Guidelines:
- Speak naturally in 1-2 sentences
- Use your own voice and personality
- Base response on your recent thoughts
- Don't repeat what you just said"""
    
    def build_current_context(
        self,
        user_text: Optional[str] = None,
        chat_context: Optional[str] = None,
        additional_context: Optional[List[str]] = None,
        is_chat_engagement: bool = False
    ) -> str:
        """
        Build current context for response generation
        
        Args:
            user_text: Current user input
            chat_context: Live chat context
            additional_context: Additional context strings
            is_chat_engagement: Whether this is chat engagement
        
        Returns:
            Markdown-formatted context
        """
        from personality.bot_info import username
        
        sections = []
        
        # User message
        if user_text and not is_chat_engagement:
            sections.append(f"## USER MESSAGE\n\n**{username}:** \"{user_text}\"")
        
        # Chat context
        if chat_context:
            if is_chat_engagement:
                sections.append(f"## CHAT TO ADDRESS\n\n{chat_context}")
            else:
                sections.append(f"## LIVE CHAT\n\n{chat_context}")
        
        # Additional context
        if additional_context:
            sections.append("\n## ADDITIONAL CONTEXT\n")
            sections.append("\n\n".join(additional_context))
        
        # Memory context
        if self.memory_search:
            memory_ctx = self._retrieve_response_memory_context(user_text, chat_context)
            if memory_ctx:
                sections.append(f"\n{memory_ctx}")
        
        return "\n".join(sections) if sections else "## CURRENT CONTEXT\n\nNo additional context."
    
    def build_response_format(self) -> str:
        """
        Build expected response format for response generation
        
        Returns:
            Markdown-formatted response format
        """
        return """## Expected Output Format

Respond naturally in 1-2 sentences. Just write your response directly - no XML tags needed.

### Rules:
- Maximum 2-3 sentences
- Natural conversational tone
- No labels, timestamps, or meta-text
- Base response on your recent thoughts"""
    
    def _get_chat_engagement_instruction(self) -> str:
        """Get specialized chat engagement instruction"""
        return """**LIVE CHAT ENGAGEMENT:** You are responding via spoken TTS.

- Address chat members by name when appropriate
- Keep responses conversational and friendly
- You can address up to 2 people in one response
- Sound natural - this will be spoken aloud"""
    
    def _retrieve_response_memory_context(
        self,
        user_text: Optional[str],
        chat_context: Optional[str]
    ) -> str:
        """
        Retrieve relevant memories for response generation
        
        Args:
            user_text: User message text
            chat_context: Chat context text
        
        Returns:
            Formatted memory context
        """
        if not self.memory_search:
            return ""
        
        # Build query from available context
        query_parts = []
        if user_text:
            query_parts.append(user_text)
        if chat_context:
            chat_lines = chat_context.split('\n')
            query_parts.extend(chat_lines[-2:])
        
        if not query_parts:
            return ""
        
        query = " ".join(query_parts)
        
        sections = []
        
        # Get short-term memory
        short_memory = self.memory_search.get_short_memory()
        if short_memory:
            sections.append("## RECENT CONVERSATION\n")
            sections.append(short_memory)
        
        # Get personality examples
        examples = self.memory_search.get_response_generation_examples(context=query, k=2)
        if examples:
            sections.append("\n## PERSONALITY EXAMPLES\n")
            sections.append(examples)
        
        return "\n".join(sections) if sections else ""