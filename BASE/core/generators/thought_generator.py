# Filename: BASE/core/generators/thought_generator.py
"""
Unified Thinking Processor - REFACTORED
Single-stage cognitive processing with integrated tool planning
Uses ThoughtPromptBuilder for consistent tool instruction injection
"""
import time
import re
import json
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path

from personality.bot_info import username

# Regex patterns for parsing
THINK_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)
ACTION_PATTERN = re.compile(r"<action_list>(.*?)</action_list>", re.DOTALL)


class ThoughtGenerator:
    """
    Unified thinking processor using single-stage prompts
    NOW: Uses ThoughtPromptBuilder for all prompt construction
    """
    
    def __init__(self, config, ollama_caller, logger, controls):
        self.config = config
        self._call_ollama = ollama_caller
        self.logger = logger
        self.controls = controls
        
        # Initialize unified prompt builder (will be set later via dependency injection)
        self.prompt_builder = None
        
        # Batch processing settings
        self._event_batch_size = 3
    
    def set_prompt_builder(self, prompt_builder):
        """
        Inject ThoughtPromptBuilder dependency
        
        Args:
            prompt_builder: ThoughtPromptBuilder instance
        """
        self.prompt_builder = prompt_builder
        
        if self.logger:
            self.logger.system("[ThoughtGenerator] Prompt builder injected")
    

    def parse_thought_response(self, response: str) -> dict:
        """
        Parse thought response into structured components
        
        Args:
            response: LLM response text
        
        Returns:
            Dict with 'thoughts', 'strategic_plan', 'actions'
        """
        result = {
            'thoughts': [],
            'strategic_plan': '',
            'actions': []
        }
        
        # Extract thoughts
        thoughts_match = re.search(r'<thoughts>(.*?)</thoughts>', response, re.DOTALL | re.IGNORECASE)
        if thoughts_match:
            thoughts_text = thoughts_match.group(1).strip()
            if thoughts_text.lower() != 'none':
                thought_lines = re.findall(r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|$)', thoughts_text, re.DOTALL)
                result['thoughts'] = [thought.strip() for _, thought in thought_lines if thought.strip()]
        
        # Extract strategic plan
        think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL | re.IGNORECASE)
        if think_match:
            result['strategic_plan'] = think_match.group(1).strip()
        
        # Extract actions
        action_match = re.search(r'<action_list>(.*?)</action_list>', response, re.DOTALL | re.IGNORECASE)
        if action_match:
            action_json = action_match.group(1).strip()
            action_json = re.sub(r'```json|```', '', action_json).strip()
            action_json = re.sub(r',\s*]', ']', action_json)
            
            if action_json and action_json != '[]':
                try:
                    actions = json.loads(action_json)
                    if isinstance(actions, list):
                        result['actions'] = actions
                except json.JSONDecodeError as e:
                    if self.logger:
                        self.logger.error(f"[Parse] JSON decode error: {e}")
        
        return result
    

    # ========================================================================
    # REACTIVE PROCESSING (Events → Thoughts + Actions)
    # ========================================================================
    
    def batch_interpret_events(
        self,
        raw_events: List,
        thought_buffer,
        context_parts: List[str] = None,
        pending_actions: str = ""
    ) -> List[Tuple[str, str, str, Optional[int]]]:
        """
        Interpret raw events into thoughts
        NOW: Uses ThoughtPromptBuilder for consistent tool instruction injection
        """
        if not raw_events:
            return []
        
        if not self.prompt_builder:
            if self.logger:
                self.logger.error("[ThoughtGenerator] Prompt builder not set!")
            return []
        
        batch = raw_events[:self._event_batch_size]
        self.logger.tool(f"[RAW DATA]\n{batch}")
        context_parts = context_parts or []
        
        has_vision = any(e.source == 'vision_result' for e in batch)
        has_urgent_reminders = thought_buffer.has_urgent_reminders
        
        # Get CLEAN recent thoughts
        recent_thoughts_raw = thought_buffer.get_thoughts_for_response()[-10:]
        recent_thoughts_str = []
        
        for t in recent_thoughts_raw:
            t_str = str(t)
            # Skip artifacts
            if t_str.startswith('<thought about') or '<acti' in t_str:
                continue
            if 'Strategic planning' in t_str and len(t_str) < 30:
                continue
            if t_str.strip().startswith('{"tool":'):
                continue
            recent_thoughts_str.append(t_str)
        
        last_user_msg = thought_buffer.get_last_user_input()
        game_context_summary = thought_buffer.get_game_context_summary()
        
        # Build prompt using ThoughtPromptBuilder (handles tool instructions automatically)
        prompt = self.prompt_builder.build_reactive_thinking_prompt(
            raw_events=batch,
            recent_thoughts=recent_thoughts_str,
            context_parts=context_parts,
            last_user_msg=last_user_msg,
            pending_actions=pending_actions,
            has_vision=has_vision,
            has_urgent_reminders=has_urgent_reminders,
            game_context_summary=game_context_summary
        )
        
        response = self._call_ollama(
            prompt=prompt,
            model=self.config.thought_model,
            system_prompt=None
        )
        
        # Extract thoughts
        thoughts = []
        for i, event in enumerate(batch):
            pattern = rf"\[{i+1}\]\s*(.+?)(?=\[\d+\]|<think>|<action|$)"
            match = re.search(pattern, response, re.DOTALL)
            
            if match:
                thought = match.group(1).strip()
                
                # Clean thought text
                thought = thought.replace('<thoughts>', '').replace('</thoughts>', '')
                thought = re.sub(r'<action_list>.*?</action_list>', '', thought, flags=re.DOTALL)
                thought = thought.strip()
                
                # CRITICAL: For user_input events, use ACTUAL message as thought
                if event.source == 'user_input' and event.data:
                    thought = f"{username} said: {event.data}"
                
                # Skip empty or artifact thoughts
                if not thought or len(thought) < 5:
                    continue
                if thought.startswith('<thought about'):
                    continue
                
                urgency_override = None
                if 'chat' in event.source.lower():
                    urgency_override = self._detect_chat_urgency(event.data)
                
                thoughts.append((thought, event.source, event.data[:100], urgency_override))
            else:
                # Fallback: use actual event data
                if event.source == 'user_input' and event.data:
                    thoughts.append(
                        (f"{username} said: {event.data}", event.source, event.data, 8)
                    )
                elif event.source != 'vision_result':
                    # For non-user_input events, create descriptive thought
                    thoughts.append(
                        (f"Noticed: {event.data}", event.source, event.data, None)
                    )
        
        return thoughts
    
    def _detect_chat_urgency(self, chat_message: str) -> int:
        """
        Detect urgency level for chat messages
        
        Returns:
            Urgency level (1-10):
            - 9: Direct bot mention
            - 7: Question
            - 6: Exclamation
            - 3: General chat
        """
        from personality.bot_info import agentname
        
        msg_lower = chat_message.lower()
        bot_name_lower = agentname.lower()
        
        # Direct mention = high urgency
        if bot_name_lower in msg_lower:
            return 9
        
        # Question = medium-high urgency
        if '?' in chat_message:
            return 7
        
        # Exclamation = medium urgency
        if '!' in chat_message:
            return 6
        
        # General chat = low urgency
        return 3
    
    # ========================================================================
    # PROACTIVE PROCESSING (Self-Reflection)
    # ========================================================================
    
    def generate_proactive_thought(
        self, 
        thought_buffer,
        context_parts: List[str] = None
    ) -> Optional[str]:
        """
        Generate proactive thought during idle periods
        NOW: Uses ThoughtPromptBuilder for consistent tool instruction injection
        """
        if not self.prompt_builder:
            if self.logger:
                self.logger.error("[ThoughtGenerator] Prompt builder not set!")
            return None
        
        recent_thoughts = thought_buffer.get_recent_context(last_n=5)
        thoughts_text = "\n".join([f"- {t}" for t in recent_thoughts]) if recent_thoughts else ""
        
        # Get ongoing context
        ongoing_ctx = thought_buffer.get_ongoing_context()
        if not ongoing_ctx:
            # Build from context parts
            if context_parts:
                ongoing_ctx = "\n".join(context_parts[:2])
            else:
                ongoing_ctx = "Free time - no active tasks"
        
        # Build proactive prompt using ThoughtPromptBuilder
        prompt = self.prompt_builder.build_standard_proactive_prompt(
            recent_thoughts=recent_thoughts,
            ongoing_context=ongoing_ctx
        )
        
        self.logger.thinking(f"[Proactive Thought]\n{prompt}")
        
        response = self._call_ollama(
            prompt=prompt,
            model=self.config.thought_model,
            system_prompt=None
        )
        
        thought = response.strip()
        
        # Validate length and content
        if 10 <= len(thought) <= 200:
            return thought
        
        return None
    
    # ========================================================================
    # STRATEGIC PLANNING WITH MEMORY INTEGRATION
    # ========================================================================
    
    def generate_strategic_plan(
        self,
        thought_buffer,
        context_parts: List[str],
        user_query: str = ""
    ) -> Optional[str]:
        """
        Generate strategic plan for complex tasks
        Integrates memory search for relevant past experiences
        
        Args:
            thought_buffer: ThoughtBuffer instance
            context_parts: Full context (game, chat, etc.)
            user_query: Optional user query to plan for
        
        Returns:
            Strategic plan text or None
        """
        recent_thoughts = thought_buffer.get_thoughts_for_response()[-10:]
        thoughts_text = "\n".join([f"- {t}" for t in recent_thoughts])
        
        last_user_msg = thought_buffer.get_last_user_input() or user_query
        
        # Build planning prompt
        prompt = f"""You are {username}'s AI assistant. Generate a brief strategic plan.

RECENT THOUGHTS:
{thoughts_text}

CONTEXT:
{chr(10).join(context_parts[:3]) if context_parts else "No additional context"}

USER REQUEST:
{last_user_msg if last_user_msg else "No specific request"}

Generate a concise strategic plan (1-2 sentences) for what to do next.
Focus on:
- Immediate next steps
- Required tools or information
- Expected outcomes

Strategic plan:"""
        
        response = self._call_ollama(
            prompt=prompt,
            model=self.config.thought_model,
            system_prompt=None
        )
        
        plan = response.strip()
        
        if 10 <= len(plan) <= 300:
            return plan
        
        return None
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def extract_strategic_thought(self, response: str) -> Optional[str]:
        """
        Extract strategic planning thought from unified response
        
        Args:
            response: LLM response text
        
        Returns:
            Strategic thought or None
        """
        # Try to extract from <think> tags
        think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL | re.IGNORECASE)
        if think_match:
            return think_match.group(1).strip()
        
        # Fallback: Look for planning indicators
        plan_match = re.search(
            r'(?:Strategic [Pp]lanning?|Planning|Next steps?):?\s*(.+?)(?=\n\n|Tool Actions|$)',
            response,
            re.DOTALL
        )
        if plan_match:
            return plan_match.group(1).strip()
        
        return None
    
    def extract_tool_actions(self, response: str) -> List[Dict]:
        """
        Extract tool actions from unified response
        
        Args:
            response: LLM response text
        
        Returns:
            List of action dictionaries
        """
        # Extract from <action_list> tags
        action_match = re.search(
            r'<action_list>(.*?)</action_list>',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        if not action_match:
            return []
        
        action_json = action_match.group(1).strip()
        
        # Clean JSON
        action_json = re.sub(r'```json|```', '', action_json).strip()
        action_json = re.sub(r',\s*]', ']', action_json)  # Remove trailing commas
        
        if not action_json or action_json == '[]':
            return []
        
        try:
            actions = json.loads(action_json)
            if isinstance(actions, list):
                return actions
        except json.JSONDecodeError as e:
            self.logger.error(f"[Parse] JSON decode error: {e}")
            self.logger.error(f"[Parse] Problematic JSON: {action_json}")
        
        return []