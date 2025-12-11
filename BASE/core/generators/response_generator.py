# Filename: BASE/core/generators/response_generator.py
"""
RESPONSE GENERATOR - Spoken Communication Synthesis
====================================================
Independent pathway for generating spoken responses separate from cognitive processing.
Synthesizes natural speech based on accumulated thoughts, not directly coupled to thought generation.

Key Responsibilities:
- Generate spoken TTS responses using accumulated thought context
- Integrate personality examples for consistent voice
- Apply post-processing (emoji removal, game command execution)
- Remain completely independent of thought processing loop

Architecture:
- Reads from thought buffer (read-only access to accumulated state)
- Does NOT manage thought state or trigger thought processing
- Uses ResponsePromptConstructor for prompt assembly
- Outputs final spoken text for TTS system

Separation of Concerns:
- Thoughts = Internal cognitive processing (thought_processor.py)
- Responses = External spoken communication (this file)
- No direct coupling between the two pathways
"""

import time
from pathlib import Path
from typing import List, Optional

from BASE.core.logger import Logger
from BASE.handlers.content_filter import ContentFilter
from BASE.core.constructors.response_prompt_constructor import ResponsePromptConstructor
from BASE.core.utils.thought_chain_formatter import ThoughtChainFormatter

from personality.bot_info import username

import re
THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)


class ResponseGenerator:
    """
    Independent response synthesis system.
    Generates spoken output from accumulated thought state.
    """
    
    def __init__(
        self,
        config,
        controls_module,
        project_root: Path,
        memory_manager=None,
        memory_search=None,
        game_manager=None,
        gui_logger=None
    ):
        """
        Initialize response generator.
        
        Args:
            config: Configuration object
            controls_module: Controls module
            project_root: Project root path
            memory_manager: MemoryManager instance (optional)
            memory_search: MemorySearch instance (optional)
            game_manager: GameManager instance (optional)
            gui_logger: GUI logger callback (optional)
        """
        self.config = config
        self.controls = controls_module
        self.project_root = project_root
        self.memory_manager = memory_manager
        self.memory_search = memory_search
        self.chain_formatter = ThoughtChainFormatter()
        
        # Initialize response prompt constructor
        self.prompt_constructor = ResponsePromptConstructor(
            controls_module,
            memory_search=memory_search,
            game_manager=game_manager
        )
        
        # FIXED: Initialize logger WITH config
        self.logger = Logger(
            name="ResponseGenerator", 
            gui_callback=gui_logger,
            config=config  # CRITICAL: Pass config here
        )
        
        # Verify config was set
        if not hasattr(self.logger, 'config') or self.logger.config is None:
            raise RuntimeError("Logger config not set during initialization!")
        
        # Verify same instance
        if id(self.logger.config) != id(self.config):
            raise RuntimeError(
                f"Logger has different config instance!\n"
                f"  ResponseGenerator config: {id(self.config)}\n"
                f"  Logger config: {id(self.logger.config)}"
            )
        
        # Content filter (post-processing only)
        self.content_filter = ContentFilter(
            ollama_endpoint=config.ollama_endpoint,
            use_ai_filter=self.controls.USE_AI_CONTENT_FILTER
        )
        
        # Statistics
        self.interaction_count = 0
        
        # Optional tool references
        self.minecraft_tool = None
        
        # Log initialization
        if memory_search and game_manager:
            self.logger.system("Response generator: personality + games + memory")
        elif memory_search:
            self.logger.system("Response generator: personality + memory")
        else:
            self.logger.system("Response generator: basic mode")
    # ========================================================================
    # LLM API CALL
    # ========================================================================
    
    def _call_ollama(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        image_data: str = ""
    ) -> str:
        """Call Ollama API for response generation."""
        import requests
        
        try:
            if image_data:
                url = f"{self.config.ollama_endpoint}/api/chat"
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({
                    "role": "user", 
                    "content": prompt, 
                    "images": [image_data]
                })
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "24h"
                }
            else:
                url = f"{self.config.ollama_endpoint}/api/generate"
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                self.logger.prompt(f"[RESPONSE SYNTHESIS]\n{full_prompt}")
                
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "keep_alive": "24h"
                }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            content = (result.get("response", "") or 
                      result.get("message", {}).get("content", ""))
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            return ""
    
    # ========================================================================
    # TOOL INJECTION
    # ========================================================================
    
    def set_minecraft_tool(self, minecraft_tool):
        """Set Minecraft tool for command execution."""
        self.minecraft_tool = minecraft_tool
    
    # ========================================================================
    # MAIN ENTRY POINT - Independent response synthesis
    # ========================================================================
    
    async def generate_response(
        self,
        user_text: str,
        context_parts: List[str],
        is_chat_engagement: bool = False
    ) -> Optional[str]:
        """
        Generate spoken response independently of thought processing.
        
        This method:
        - Reads accumulated thought state (read-only)
        - Builds memory context for coherent responses
        - Synthesizes natural spoken output
        - Does NOT trigger thought processing
        - Does NOT modify thought state (except adding response echo)
        
        Args:
            user_text: Current user input (for context)
            context_parts: Additional context (game, chat, memory)
            is_chat_engagement: Whether responding to chat
        
        Returns:
            Spoken response text or None
        """
        # Build memory context
        memory_context = self._build_memory_context_for_response(
            user_text,
            context_parts
        )
        
        # Add memory to context
        response_context_parts = list(context_parts)
        if memory_context:
            response_context_parts.insert(0, memory_context)
        
        # Extract chat context
        chat_context = self._extract_chat_context(context_parts)
        
        # Build response prompt
        prompt = self.prompt_constructor.build_response_prompt_simple(
            user_text=user_text,
            context_parts=response_context_parts,
            chat_context=chat_context,
            is_chat_engagement=is_chat_engagement
        )
        self.logger.prompt(f"[Response Synthesis]\n{prompt}")
        
        # Generate response
        response = self._call_ollama(
            prompt=prompt,
            model=self.config.text_model,
            system_prompt=None
        )
        
        # Clean response
        response = THINK_PATTERN.sub('', response).strip()
        
        # Validate
        if not response:
            return None
        
        # Post-process
        response = await self._apply_post_processing(response)
        
        # Update statistics
        if response:
            # Create echo for thought chain (caller adds to buffer)
            echo = self.create_response_echo(response)
            # Note: Caller (ai_core) should add this echo to thought buffer
            
            self.interaction_count += 1
        
        return response
    
    def create_response_echo(self, spoken_text: str) -> str:
        """
        Create echo of spoken response for thought chain
        
        Args:
            spoken_text: What was just spoken
        
        Returns:
            Echo thought string
        """
        return self.chain_formatter.create_response_echo(spoken_text)
    
    # ========================================================================
    # CONTEXT EXTRACTION
    # ========================================================================
    
    def _extract_chat_context(self, context_parts: List[str]) -> Optional[str]:
        """Extract live chat context from context_parts."""
        chat_sections = [
            part for part in context_parts
            if part.startswith('## LIVE CHAT')
        ]
        
        if not chat_sections:
            return None
        
        combined_chat = '\n\n'.join(chat_sections)
        combined_chat = combined_chat.replace('## LIVE CHAT\n', '')
        
        return combined_chat.strip() if combined_chat.strip() else None
    
    # ========================================================================
    # POST-PROCESSING
    # ========================================================================
    
    async def _apply_post_processing(self, reply: str) -> str:
        """
        Apply post-processing to response.
        Note: Content filtering done upstream in ai_core.
        """
        from BASE.core.clean_response import remove_emoji
        reply = remove_emoji(reply)
        
        return reply
    
    # ========================================================================
    # MEMORY INTEGRATION
    # ========================================================================
    
    def _build_memory_context_for_response(
        self,
        user_text: str,
        context_parts: List[str]
    ) -> str:
        """
        ENHANCED: Build memory context using user input + thought chain
        Now leverages the agent's current cognitive state
        """
        if not self.memory_search:
            return ""
        
        # CRITICAL: Get recent thoughts from thought processor
        recent_thoughts = []
        if hasattr(self, '_thought_processor_ref') and self._thought_processor_ref:
            recent_thoughts = self._thought_processor_ref.thought_buffer.get_thoughts_for_response()[-5:]
        
        # Build query - now considers thoughts!
        query = user_text if user_text else " ".join(context_parts[:2])
        
        if not query and not recent_thoughts:
            return ""
        
        query_lower = query.lower()
        memory_sections = []
        
        # Check for yesterday trigger
        if any(trigger in query_lower for trigger in [
            'yesterday', 'last night', 'this morning'
        ]):
            yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=8)
            if yesterday_ctx:
                from datetime import datetime, timedelta
                yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                memory_sections.append(f"## YESTERDAY ({yesterday_date})")
                memory_sections.append(yesterday_ctx)
        
        # Check for recall triggers
        recall_triggers = [
            'remember', 'recall', 'before', 'earlier', 'last time',
            'you said', 'we talked', 'previous', 'mentioned'
        ]
        if any(trigger in query_lower for trigger in recall_triggers):
            # ENHANCED: Use combined search with thought chain
            medium_results = self.memory_search.search_medium_memory_combined(
                user_input=query,
                recent_thoughts=recent_thoughts,
                k=3,
                use_embedding_combination=True
            )
            if medium_results:
                memory_sections.append("\n## EARLIER TODAY")
                for r in medium_results:
                    role = (
                        username
                        if r['role'] == 'user'
                        else self.memory_search.memory_manager.agentname
                    )
                    memory_sections.append(
                        f"{role}: {r['content']} (relevance: {r['similarity']:.2f})"
                    )
            
            # ENHANCED: Long memory with thought chain
            long_results = self.memory_search.search_long_memory_combined(
                user_input=query,
                recent_thoughts=recent_thoughts,
                k=2,
                use_embedding_combination=True
            )
            if long_results:
                memory_sections.append("\n## PAST CONVERSATIONS")
                for r in long_results:
                    memory_sections.append(
                        f"[{r['date']}] {r['summary']} (relevance: {r['similarity']:.2f})"
                    )
        
        if not memory_sections:
            return ""
        
        return "\n".join(memory_sections)
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_response_stats(self) -> dict:
        """Get response generation statistics."""
        return {
            'total_responses': self.interaction_count,
            'has_personality_examples': self.memory_search is not None,
            'has_minecraft': self.minecraft_tool is not None,
            'content_filter_enabled': self.controls.ENABLE_CONTENT_FILTER
        }