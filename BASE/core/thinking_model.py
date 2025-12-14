# Filename: BASE/core/thinking_model.py
"""
Enhanced Thinking Model Module - Cleaned
All game references removed - games are now tools
Uses modular prompt construction from personality_prompt_parts.py
"""
import time
import re
from typing import List, Dict, Tuple, Optional
from collections import deque
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from personality.bot_info import agentname
from personality.prompts.personality_prompt_parts import PersonalityPromptParts

THINK_PATTERN = re.compile(r'<think>(.*?)</think>', re.DOTALL)


class ThoughtBuffer:
    """Manages the thinking model's thought accumulation"""
    
    def __init__(self, max_thoughts=10):
        self.thoughts = deque(maxlen=max_thoughts * 2)
        self.max_thoughts = max_thoughts
        self.last_user_interaction = None
        self.last_response_time = time.time()
        
    def add_thought(self, thought: str, source: str, original_text: str = ""):
        """Add a new thought to the buffer with priority tracking"""
        self.thoughts.append({
            'content': thought,
            'source': source,
            'priority': source,
            'timestamp': time.time(),
            'original_text': original_text
        })
        
        if source in ['user_input', 'direct_mention']:
            self.last_user_interaction = time.time()
    
    def get_thoughts(self, last_n: Optional[int] = None) -> List[Dict]:
        """Get thoughts from buffer"""
        if last_n is not None:
            return list(self.thoughts)[-last_n:]
        return list(self.thoughts)
    
    def clear(self):
        """Clear thought buffer after response"""
        self.thoughts.clear()
    
    def should_respond(self) -> Tuple[bool, Optional[str]]:
        """Determine if agent should respond based on accumulated thoughts"""
        if not self.thoughts:
            return False, None
        
        t = time.time()
        since_response = t - self.last_response_time
        
        # P1: Direct mentions - IMMEDIATE (user explicitly called the bot)
        for th in self.thoughts:
            if th.get('priority') == 'direct_mention':
                return True, "direct_mention"
        
        # P2: Direct questions with explicit queries
        user_ths = [th for th in self.thoughts if th['source'] in ['user_input', 'direct_mention']]
        if user_ths:
            txt = user_ths[-1]['original_text'].lower()
            
            # Explicit question mark or bot name
            if '?' in txt or agentname.lower() in txt:
                return True, "direct_question"
            
            # Strong command verbs
            if any(cmd in txt for cmd in ['search', 'tell me', 'explain', 'show me']):
                return True, "command"
            
            # Greetings only if recent
            if since_response > 10 and any(g in txt.split() for g in ['hi', 'hello', 'hey', 'sup']):
                return True, "greeting"
        
        # P4: User waiting (but give them time for follow-up)
        if self.last_user_interaction:
            wait = t - self.last_user_interaction
            if 8 < wait < 15:
                return True, "user_waiting"
        
        # P5: Significant thought accumulation
        if len(self.thoughts) >= 6:
            non_obs = [th for th in self.thoughts if th.get('source') != 'observation']
            if len(non_obs) >= 3 and since_response > 25:
                return True, "thought_buffer_full"
        
        # P6: Natural conversation flow (more selective)
        if since_response > 30:
            actionable = [th for th in self.thoughts if th.get('source') in 
                        ['user_input', 'direct_mention', 'search', 'memory']]
            if len(actionable) >= 2:
                return True, "conversation_flow"
        
        # P7: Significant context after long silence
        if len(self.thoughts) >= 4 and since_response > 45:
            return True, "accumulated_context"
        
        return False, "accumulating"


class ThinkingModelProcessor:
    """Processes thinking model logic with modular prompt construction"""
    
    def __init__(self, config, ollama_caller, system_prompt_getter, logger):
        self.config = config
        self._call_ollama = ollama_caller
        self._get_system_prompt = system_prompt_getter
        self._log = logger
        
    def generate_interpretation(self, experience_type: str, experience_data: str, 
                            thought_buffer: ThoughtBuffer, original_text: str = "") -> str:
        """Generate internal thought about an experience using modular prompts"""
        from personality.bot_info import agentname
        
        recent_thoughts = thought_buffer.get_thoughts(last_n=3)
        thoughts_text = "\n".join([f"- {t['content']}" for t in recent_thoughts]) if recent_thoughts else "None yet"
        
        # Build context hint based on experience type
        context_hint = self._get_context_hint(experience_type, thought_buffer)
        
        # Get unified personality
        personality = PersonalityPromptParts.get_unified_personality()
        
        # Build personality-aware prompt using modular components
        prompt = f"""{personality}

## Your Recent Thoughts
{thoughts_text}

## New Experience: {experience_type}
{experience_data}

{context_hint}

Write {agentname}'s brief internal reaction to this incoming data or experience. 
Keep your reaction to 1-2 sentences max, and stay in character.
This is your INTERNAL thought, not a response to others. Think from {agentname}'s perspective.
Stay conversational and casual, not formal or scholarly. This internal thought will be used to inform your response, 
not shared directly with the user or others, so do not respond directly to them in this thought.


Your thought:"""
        
        thought = self._call_ollama(
            prompt=prompt,
            model=self.config.text_llm_model,
            system_prompt=None
        )
        
        thought = THINK_PATTERN.sub('', thought).strip()
        thought = thought.replace('</think>', '').strip()
        
        return thought if thought else f"Processing {experience_type}..."
    
    def _get_context_hint(self, experience_type: str, thought_buffer: ThoughtBuffer) -> str:
        """Get appropriate context hint based on current environment and task"""
        return ""
    
    def synthesize_response_from_thoughts(self, thought_buffer: ThoughtBuffer, 
                                        urgency_reason: str, use_system_prompt: bool) -> str:
        """Synthesize final response using modular prompt construction"""
        from personality.bot_info import agentname, username
        from BASE.core.clean_response import remove_emoji
        
        thoughts = thought_buffer.get_thoughts()
        
        if not thoughts:
            return "Hmm, let me think about that..."
        
        # Response style based on trigger
        is_direct = urgency_reason in ["direct_mention", "direct_question", "greeting", "command"]
        is_thoughtful = urgency_reason in ["thought_buffer_full", "conversation_flow", "accumulated_context"]
        
        # Select thought window
        if is_direct:
            sel = thoughts[-3:]
            max_len = "1-2 sentences"
        elif is_thoughtful:
            sel = thoughts[-7:]
            max_len = "2-4 sentences"
        else:
            sel = thoughts[-5:]
            max_len = "2-3 sentences"
        
        thoughts_txt = "\n".join([f"- {t['content']}" for t in sel])
        
        # Get unified personality
        personality = PersonalityPromptParts.get_unified_personality()
        
        # Add urgency context
        urgency_txt = self._get_urgency_context(urgency_reason)
        
        # Construct full prompt
        prompt = f"""{personality}

## Your Stream of Consciousness
{thoughts_txt}

## Situation
{urgency_txt}

Respond naturally based on your accumulated thoughts.

## Constraints
- {max_len} maximum (under 700 characters)
- First person ("I", "me", "my")
- Address user as {username}
- No labels/tags/timestamps
- Conversational gamer style
- ONLY reference things explicitly shown in your data
- NO hallucinating or inventing details
- Be honest if you don't see something specific

Response:"""
        
        resp = self._call_ollama(prompt=prompt, model=self.config.text_llm_model, system_prompt=None)
        
        resp = THINK_PATTERN.sub('', resp).strip().replace('</think>', '').strip()
        resp = remove_emoji(resp)
        
        if resp in ["...", ".", "", "***"]:
            return ""
        
        return resp
    
    def _get_urgency_context(self, urgency_reason: str) -> str:
        """Get urgency context description"""
        urgency_map = {
            "direct_mention": "You were directly addressed. Respond naturally using ONLY real data.",
            "direct_question": "Answer the question clearly using ONLY what you actually observe.",
            "command": "Acknowledge and act on the request.",
            "thought_buffer_full": "You've processed a lot. Share your informed perspective.",
            "conversation_flow": "You've been thinking. Add meaningful input.",
            "accumulated_context": "You have substantial context. Provide a thoughtful response.",
            "user_waiting": "The user is waiting. Respond based on REAL observations.",
            "greeting": "Greet them warmly."
        }
        return urgency_map.get(urgency_reason, "Respond naturally based on your thoughts.")