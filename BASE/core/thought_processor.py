# Filename: BASE/core/thought_processor.py
"""
Enhanced Thought Processor - Core Orchestration
All urgency_override → priority_override
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from dataclasses import dataclass, asdict
import re

from BASE.core.thought_buffer import ThoughtBuffer
# from BASE.core.constructors.thought_response_parser import ThoughtResponseParser
from BASE.core.logger import Logger
from BASE.core.thinking_modes import ThinkingModes

from personality.bot_info import username


@dataclass
class ThoughtState:
    """Serializable thought state for persistence"""
    thoughts: List[Dict]
    unspoken_count: int
    max_urgency: int
    last_user_input: str
    ongoing_context: str
    last_update: float
    has_urgent_reminders: bool
    current_goal: Optional[Dict]
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class ThoughtProcessor:
    """
    Core thought processor with continuous cognitive loop
    Uses tool_manager for all tool operations
    """
    __slots__ = (
        'config', 'controls', 'project_root', 'memory_search',
        'session_file_manager', 'prompt_builder', 'logger', 'thought_buffer',
        'parser', '_is_processing', '_last_memory_integration',
        '_thought_cache', '_cache_dirty', 'cognitive_loop', 'event_loop',
        '_ai_core_ref',
        'thinking_modes', 'action_state_manager',
        'tool_manager',
        '_last_tool_exploration'
    )
    
    def __init__(
        self, config, controls_module, project_root: Path,
        memory_search=None, session_file_manager=None,
        gui_logger=None
    ):
        """Initialize thought processor"""
        self.config = config
        self.controls = controls_module
        self.project_root = project_root
        self.memory_search = memory_search
        self.session_file_manager = session_file_manager
        
        # Create logger FIRST
        self.logger = Logger(name="ThoughtProcessor", gui_callback=gui_logger, config=config)
        
        # Initialize prompt builder
        from BASE.core.constructors.thought_prompt_builder import ThoughtPromptBuilder
        
        self.prompt_builder = ThoughtPromptBuilder(
            controls_module=controls_module,
            memory_search=memory_search,
            logger=self.logger
        )
        
        # Initialize other components
        self.thought_buffer = ThoughtBuffer(max_thoughts=25)
        # self.parser = ThoughtResponseParser()
        
        # State tracking
        self._is_processing = False
        self._last_memory_integration = 0.0
        self._last_tool_exploration = 0.0
        
        # Tool system references (injected later)
        self.tool_manager = None
        self.action_state_manager = None
        
        # Cognitive loop manager
        self.cognitive_loop = None
        self.event_loop = None
        self._ai_core_ref = None
        
        # Initialize thinking modes
        self.thinking_modes = ThinkingModes(
            processor=self,
            config=config,
            controls=controls_module,
            logger=self.logger
        )
        
        # Inject prompt builder into thinking modes
        self.thinking_modes.set_prompt_builder(self.prompt_builder)
        
        # Log initialization
        if memory_search:
            self.logger.system("Enhanced processor: unified prompts + personality + memory")
        else:
            self.logger.system("Enhanced processor: unified prompts (basic mode)")
    
    # ========================================================================
    # DEPENDENCY INJECTION - REFACTORED
    # ========================================================================
    
    def set_tool_manager(self, tool_manager):
        """
        Inject tool manager into prompt builder
        Uses tool_manager naming
        
        Args:
            tool_manager: ToolManager instance
        """
        self.tool_manager = tool_manager
        self.action_state_manager = tool_manager.action_state_manager
        
        # Inject into prompt_builder
        if hasattr(self, 'prompt_builder') and self.prompt_builder:
            self.prompt_builder.set_tool_manager(tool_manager)
            
            # Also inject persistence manager
            if hasattr(tool_manager, 'instruction_persistence_manager'):
                self.prompt_builder.set_instruction_persistence_manager(
                    tool_manager.instruction_persistence_manager
                )
                
                self.logger.system(
                    "[Thought Processor] [SUCCESS] Persistence manager injected into prompt builder"
                )
            
            # Verification
            setup = self.prompt_builder.validate_setup()
            
            # Get tool counts directly from tool manager (safer than relying on setup dict)
            enabled_count = len(tool_manager.get_enabled_tool_names())
            active_count = 0
            
            if hasattr(tool_manager, 'instruction_persistence_manager') and tool_manager.instruction_persistence_manager:
                try:
                    active_count = len(tool_manager.instruction_persistence_manager.get_active_tool_names())
                except:
                    pass
            
            self.logger.system(
                f"[Thought Processor] [SUCCESS] Prompt builder configured: "
                f"{enabled_count} tools available, "
                f"{active_count} with active instructions"
            )
        else:
            self.logger.error("[Thought Processor] [FAILED] No prompt_builder attribute!")
        
        # Update thinking_modes references
        if hasattr(self, 'thinking_modes'):
            self.thinking_modes.tool_manager = tool_manager
            self.thinking_modes.action_state_manager = self.action_state_manager
    
    def _call_ollama(self, prompt: str, model: str, system_prompt: Optional[str] = None, 
                    image_data: str = "") -> str:
        """Call Ollama API with keep-alive"""
        import requests
        
        try:
            if image_data:
                url = f"{self.config.ollama_endpoint}/api/chat"
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt, "images": [image_data]})
                payload = {"model": model, "messages": messages, "stream": False, "keep_alive": "24h"}
            else:
                url = f"{self.config.ollama_endpoint}/api/generate"
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                
                self.logger.prompt(f"{full_prompt}")
                
                payload = {
                    "model": model, "prompt": full_prompt, "stream": False,
                    "temperature": self.config.ollama_temperature,
                    "top_p": self.config.ollama_top_p,
                    "top_k": self.config.ollama_top_k,
                    "repeat_penalty": self.config.ollama_repeat_penalty,
                    "num_predict": self.config.ollama_max_tokens,
                    "keep_alive": "24h"
                }
                
                if self.config.ollama_seed is not None:
                    payload["seed"] = self.config.ollama_seed
            
            response = requests.post(url, json=payload, timeout=self.config.ollama_timeout)
            response.raise_for_status()
            result = response.json()
            content = result.get("response", "") or result.get("message", {}).get("content", "")
            
            self.logger.thinking(f"{content}")
            
            return content.strip()
        except Exception as e:
            self.logger.error(f"Ollama API error: {e}")
            return ""
        
    def _parse_thought_response(self, response: str) -> dict:
        """
        Parse thought response into structured components
        Integrated parser - no external dependency
        
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
                    self.logger.error(f"[Parse] JSON decode error: {e}")
                    if self.controls.LOG_RESPONSE_PROCESSING:
                        self.logger.error(f"[Parse] Problematic JSON: {action_json[:200]}")
        
        return result
                
    # ========================================================================
    # DATA INGESTION
    # ========================================================================
    
    def ingest_data(self, source: str, data: str):
        """Fast data ingestion for background processing"""
        self.thought_buffer.ingest_raw_data(source, data)
        self.logger.system(f"Ingested: {source} ({len(data)} chars)")
    
    def ingest_user_directive(self, user_input: str):
        """Ingest user input"""
        if not user_input or not user_input.strip():
            self.logger.system("[Input] Empty input - checking for proactive processing")
            return
        
        self.logger.tool(
            f"[USER DIRECTIVE INGESTION]\n"
            f"Raw Input: {user_input}"
        )
        
        self.ingest_data('user_input', user_input)
        
        self.logger.system(f"[Input] User: {user_input}")
    
    # ========================================================================
    # CONTINUOUS THINKING CONTROL
    # ========================================================================
    
    def start_continuous_thinking(self):
        """Start continuous autonomous thinking loop"""
        if self.cognitive_loop is not None:
            self.logger.warning("[Continuous] Loop already started")
            return
        
        from BASE.core.cognitive_loop_manager import CognitiveLoopManager
        
        self.cognitive_loop = CognitiveLoopManager(
            thought_processor=self, controls=self.controls, logger=self.logger
        )
        
        if hasattr(self, '_ai_core_ref'):
            self.cognitive_loop.set_ai_core(self._ai_core_ref)
        else:
            self.logger.warning("[Continuous] No AI core reference - responses may not work")
        
        if hasattr(self, 'event_loop') and self.event_loop:
            asyncio.run_coroutine_threadsafe(
                self.cognitive_loop.start_continuous_loop(), self.event_loop
            )
        else:
            self.logger.error("No event loop available for continuous thinking")
            return
        
        self.logger.system("Continuous autonomous thinking ENABLED")
    
    def set_ai_core_reference(self, ai_core):
        """Store reference to AI core for autonomous responses"""
        self._ai_core_ref = ai_core
        if self.cognitive_loop:
            self.cognitive_loop.set_ai_core(ai_core)
    
    async def stop_continuous_thinking(self):
        """Stop continuous thinking"""
        if self.cognitive_loop:
            await self.cognitive_loop.stop_continuous_loop()
            self.cognitive_loop = None
            self.logger.system("Continuous thinking DISABLED")
    
    # ========================================================================
    # MAIN COGNITIVE PROCESSING
    # ========================================================================

    async def process_thoughts(self, context_parts: List[str] = None) -> bool:
        """
        Main cognitive processing loop
        Uses tool_manager for all tool operations
        All priority_override instead of urgency_override
        """
        if self._is_processing:
            return False
        
        self._is_processing = True
        
        try:
            processing_occurred = False
            
            if not context_parts:
                context_parts = await self.thinking_modes.build_thought_context()
            
            # Check chat engagement
            chat_engagement_needed = self._check_chat_engagement_need()
            if chat_engagement_needed:
                chat_thought = self._create_chat_engagement_thought()
                if chat_thought:
                    # Use priority_override
                    self.thought_buffer.add_processed_thought(
                        chat_thought['content'], 
                        chat_thought['source'],
                        chat_thought.get('original_ref'), 
                        priority_override=chat_thought.get('priority_override')
                    )
                    processing_occurred = True
            
            raw_events = self.thought_buffer.get_unprocessed_events()
            
            if raw_events:
                # Reactive processing
                self.thought_buffer.reset_consecutive_counter()
                
                # Get pending actions from tool system
                pending_actions = ""
                if hasattr(self, 'action_state_manager') and self.action_state_manager:
                    pending_actions = self.action_state_manager.get_context_summary()
                
                thoughts, actions = await self._reactive_processing(
                    raw_events, context_parts, pending_actions
                )
                
                if thoughts:
                    for thought_data in thoughts:
                        # Use priority_override
                        self.thought_buffer.add_processed_thought(
                            thought_data['content'], 
                            thought_data['source'],
                            thought_data.get('original_ref'),
                            priority_override=thought_data.get('priority_override')
                        )
                
                # Execute actions via tool manager
                if actions and hasattr(self, 'tool_manager') and self.tool_manager:
                    await self.tool_manager.execute_structured_actions(
                        actions, self.thought_buffer
                    )
                
                self.thought_buffer.mark_events_processed(len(raw_events))
                processing_occurred = True
            else:
                # Proactive processing
                thinking_mode = self.thinking_modes.determine_thinking_mode(context_parts)
                
                if thinking_mode == 'memory_reflection':
                    result = await self.thinking_modes.memory_reflective_thinking(context_parts)
                elif thinking_mode == 'future_planning':
                    result = await self.thinking_modes.future_planning_thinking(context_parts)
                else:
                    result = await self.thinking_modes.proactive_processing(context_parts)
                
                if isinstance(result, dict):
                    proactive_thought = result.get('thought')
                    proactive_actions = result.get('actions', [])
                else:
                    proactive_thought = result
                    proactive_actions = []
                
                if proactive_thought:
                    self.thought_buffer.add_proactive_thought(proactive_thought)
                    processing_occurred = True
            
            # Background maintenance
            await self._check_urgent_reminders()
            
            if time.time() - self._last_memory_integration > 120.0:
                await self.thinking_modes.periodic_memory_integration()
                self._last_memory_integration = time.time()
            
            return processing_occurred
        finally:
            self._is_processing = False
    
    def _check_chat_engagement_need(self) -> bool:
        """Check if chat engagement needed"""
        chat_enabled = getattr(self.controls, 'CHAT_ENGAGEMENT', False)
        if not chat_enabled:
            return False
        return self.thought_buffer.should_engage_with_chat()
    
    def _create_chat_engagement_thought(self) -> Optional[Dict]:
        """
        Create chat engagement thought
        Returns priority_override
        """
        from BASE.core.thought_buffer import Priority
        
        unengaged = self.thought_buffer.get_unengaged_messages(max_messages=5)
        if not unengaged:
            return None
        
        chat_summary_parts = []
        has_mention, has_question = False, False
        
        for msg in unengaged:
            platform = msg.get('platform', 'Chat')
            chat_username = msg.get('username', 'Someone')
            message = msg.get('message', '')
            
            if msg.get('has_mention', False):
                has_mention = True
                chat_summary_parts.append(f"{chat_username} mentioned me: {message}")
            elif '?' in message:
                has_question = True
                chat_summary_parts.append(f"{chat_username} asked: {message}")
            else:
                chat_summary_parts.append(f"{chat_username}: {message}")
        
        if has_mention:
            priority, thought_prefix = Priority.CRITICAL, "I was mentioned in chat!"
        elif has_question:
            priority, thought_prefix = Priority.HIGH, "There are questions in chat"
        else:
            priority, thought_prefix = Priority.MEDIUM, "Chat is active"
        
        summary = "\n".join(chat_summary_parts[:3])
        thought_content = f"{thought_prefix}\n{summary}"
        
        # Return priority_override
        return {
            'content': thought_content, 
            'source': 'chat_engagement',
            'original_ref': summary, 
            'priority_override': priority
        }
    
    # ========================================================================
    # REACTIVE PROCESSING
    # ========================================================================
    
    async def _reactive_processing(self, raw_events, context_parts, pending_actions):
        """
        Process events reactively using centralized prompt builder
        All priority_override instead of urgency_override
        """
        from BASE.core.thought_buffer import Priority
        
        self.logger.tool(
            f"[REACTIVE PROCESSING START]\n"
            f"Event Count: {len(raw_events)}\n"
            f"Events:\n" + 
            "\n".join([f"  [{i}] {e.source}: {e.data}" for i, e in enumerate(raw_events)])
        )
        
        recent_thoughts_list = self.thought_buffer.get_thoughts_for_response()[-10:]
        recent_thoughts_str = [str(t) for t in recent_thoughts_list]
        last_user_msg = self.thought_buffer.get_last_user_input()
        
        has_vision = any(hasattr(e, 'source') and e.source == 'vision_result' for e in raw_events)
        has_urgent_reminders = self.thought_buffer.has_urgent_reminders
        
        # Build prompt using ThoughtPromptBuilder
        prompt = self.prompt_builder.build_reactive_thinking_prompt(
            raw_events=raw_events,
            recent_thoughts=recent_thoughts_str,
            context_parts=context_parts,
            last_user_msg=last_user_msg,
            pending_actions=pending_actions,
            has_vision=has_vision,
            has_urgent_reminders=has_urgent_reminders,
        )
        
        response = self._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        # Parse response
        parsed = self._parse_thought_response(response)
        
        self.logger.tool(
            f"[REACTIVE PROCESSING RESULT]\n"
            f"Thoughts: {len(parsed['thoughts'])}\n"
            f"Actions: {len(parsed['actions'])}\n"
            f"Plan: {bool(parsed['strategic_plan'])}"
        )
        
        # Convert to internal format
        thoughts = []
        for i, thought_text in enumerate(parsed['thoughts']):
            event = raw_events[i] if i < len(raw_events) else raw_events[-1]
            
            if not isinstance(thought_text, str):
                thought_text = str(thought_text)
            
            priority_override = None
            if hasattr(event, 'source'):
                if event.source == 'user_input':
                    priority_override = Priority.HIGH
                elif 'chat' in event.source.lower() and hasattr(event, 'data'):
                    priority_override = self._detect_chat_urgency(event.data)
            
            # Use priority_override
            thoughts.append({
                'content': thought_text,
                'source': event.source if hasattr(event, 'source') else 'unknown',
                'original_ref': event.data if hasattr(event, 'data') else '',
                'priority_override': priority_override
            })
        
        # Add strategic plan
        if parsed['strategic_plan']:
            plan_text = str(parsed['strategic_plan'])
            # Use priority_override
            thoughts.append({
                'content': plan_text, 
                'source': 'internal',
                'original_ref': '', 
                'priority_override': None
            })
            
            self.logger.thinking(f"[Plan] {plan_text}")
        
        # Validate actions
        actions = self._validate_actions(parsed['actions'])
        
        if actions:
            tool_names = [a['tool'] for a in actions]
            self.logger.tool(f"[Actions Validated] {tool_names}")
        
        return thoughts, actions
    
    def _detect_chat_urgency(self, chat_message: str) -> str:
        """
        Detect priority for chat messages
        Returns: Priority level (Low/Medium/High/Critical)
        """
        from BASE.core.thought_buffer import Priority
        from personality.bot_info import agentname
        
        msg_lower = chat_message.lower()
        bot_name_lower = agentname.lower()
        
        if bot_name_lower in msg_lower:
            return Priority.CRITICAL
        if '?' in chat_message:
            return Priority.HIGH
        if '!' in chat_message:
            return Priority.MEDIUM
        return Priority.LOW
    
    def _validate_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Validate actions against available tools
        """
        if not actions:
            return []
        
        valid_actions = []
        
        # Get enabled tools from tool manager
        if not hasattr(self, 'tool_manager') or not self.tool_manager:
            return []
        
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        
        for action in actions:
            if not isinstance(action, dict) or 'tool' not in action or 'args' not in action:
                continue
            
            tool_name = action['tool']
            tool_category = tool_name.split('.')[0] if '.' in tool_name else tool_name
            
            # [CRITICAL] "instructions" is always valid
            if tool_category == 'instructions':
                valid_actions.append(action)
                self.logger.system(
                    f"[Action Validation] [SUCCESS] Instruction retrieval request: {action}"
                )
                continue
            
            # Check if tool is enabled
            if tool_category in enabled_tools:
                valid_actions.append(action)
                self.logger.system(
                    f"[Action Validation] [SUCCESS] Tool action validated: {action}"
                )
            else:
                self.logger.warning(
                    f"[Action Validation] [FAILED] Rejected (tool not enabled): {action}\n"
                    f"  Available tools: {enabled_tools}"
                )
        
        if valid_actions:
            self.logger.system(
                f"[Action Validation] Validated {len(valid_actions)} of {len(actions)} actions"
            )
        
        return valid_actions
    
    # ========================================================================
    # BACKGROUND MAINTENANCE
    # ========================================================================
    
    async def _check_urgent_reminders(self):
        # Reminders handled by modular tool system
        pass
    
    # ========================================================================
    # STATE PERSISTENCE
    # ========================================================================
    
    def get_performance_stats(self) -> Dict:
        """Get processing statistics"""
        pending_count = 0
        if hasattr(self, 'action_state_manager') and self.action_state_manager:
            pending_count = len(self.action_state_manager.get_pending_actions())
        
        return {
            'thought_buffer_size': len(self.thought_buffer._thoughts),
            'raw_events_pending': len(self.thought_buffer.get_unprocessed_events()),
            'unspoken_thoughts': self.thought_buffer.count_unspoken_thoughts(),
            'max_urgency': self.thought_buffer.get_highest_priority(),
            'pending_actions': pending_count,
            'has_memory_search': self.memory_search is not None,
            'last_memory_integration': self._last_memory_integration,
            'cognitive_loop_active': self.cognitive_loop is not None
        }