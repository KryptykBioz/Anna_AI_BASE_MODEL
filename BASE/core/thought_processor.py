# Filename: BASE/core/thought_processor.py
"""
Thought Processor - REFACTORED for Modular Prompt System
========================================================
Uses new response_decider + modular constructors
Removed old ThoughtPromptBuilder completely
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
from dataclasses import dataclass, asdict
import re

from BASE.core.thought_buffer import ThoughtBuffer
from BASE.core.logger import Logger
from BASE.core.thinking_modes import ThinkingModes

# NEW: Import response decider and constructors
from BASE.core.response_decider import ResponseDecider, PromptType
from BASE.core.responsive.responsive_constructor import ResponsiveConstructor
from BASE.core.reflective.reflective_constructor import ReflectiveConstructor
from BASE.core.planning.planning_constructor import PlanningConstructor

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
    Core thought processor with modular prompt construction
    NEW: Uses ResponseDecider to choose constructor
    """
    __slots__ = (
        'config', 'controls', 'project_root', 'memory_search',
        'session_file_manager', 'logger', 'thought_buffer',
        '_is_processing', '_last_memory_integration',
        'cognitive_loop', 'event_loop', '_ai_core_ref',
        'thinking_modes', 'action_state_manager', 'tool_manager',
        '_last_tool_exploration',
        # NEW: Modular prompt system
        'response_decider', 'responsive_constructor',
        'reflective_constructor', 'planning_constructor'
    )
    
    def __init__(
        self, config, controls_module, project_root: Path,
        memory_search=None, session_file_manager=None,
        gui_logger=None
    ):
        """Initialize thought processor with modular prompt system"""
        self.config = config
        self.controls = controls_module
        self.project_root = project_root
        self.memory_search = memory_search
        self.session_file_manager = session_file_manager
        
        # Create logger
        self.logger = Logger(name="ThoughtProcessor", gui_callback=gui_logger, config=config)
        
        # Initialize thought buffer
        self.thought_buffer = ThoughtBuffer(max_thoughts=25)
        
        # NEW: Initialize modular prompt system
        from personality.bot_info import agentname
        
        self.response_decider = ResponseDecider(
            agentname=agentname,
            username=username,
            logger=self.logger
        )
        
        self.responsive_constructor = ResponsiveConstructor(
            tool_manager=None,  # Injected later
            logger=self.logger
        )
        
        self.reflective_constructor = ReflectiveConstructor(
            memory_search=memory_search,
            tool_manager=None,  # Injected later
            logger=self.logger
        )
        
        self.planning_constructor = PlanningConstructor(
            tool_manager=None,  # Injected later
            logger=self.logger
        )
        
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
        
        # Log initialization
        self.logger.system("Thought Processor initialized with modular prompt system")
    
    # ========================================================================
    # DEPENDENCY INJECTION
    # ========================================================================
    
    def set_tool_manager(self, tool_manager):
        """
        Inject tool manager into all constructors
        
        Args:
            tool_manager: ToolManager instance
        """
        self.tool_manager = tool_manager
        self.action_state_manager = tool_manager.action_state_manager
        
        # Inject into all constructors
        self.responsive_constructor.tool_manager = tool_manager
        self.reflective_constructor.tool_manager = tool_manager
        self.planning_constructor.tool_manager = tool_manager
        
        # Update thinking_modes references
        self.thinking_modes.tool_manager = tool_manager
        self.thinking_modes.action_state_manager = self.action_state_manager
        
        enabled_count = len(tool_manager.get_enabled_tool_names())
        self.logger.system(
            f"[Thought Processor] Tool manager injected: "
            f"{enabled_count} tools available to all constructors"
        )
    
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
        """Parse thought response into structured components"""
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
        
        self.logger.tool(f"[USER INPUT] {user_input}")
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
    # MAIN COGNITIVE PROCESSING - REFACTORED
    # ========================================================================

    async def process_thoughts(self, context_parts: List[str] = None) -> bool:
        """
        Main cognitive processing loop - REFACTORED
        NOW PASSES TIMESTAMP TO THOUGHT BUFFER
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
                    self.thought_buffer.add_processed_thought(
                        chat_thought['content'], 
                        chat_thought['source'],
                        chat_thought.get('original_ref'), 
                        priority_override=chat_thought.get('priority_override'),
                        timestamp=chat_thought.get('timestamp', time.time())  # PASS TIMESTAMP
                    )
                    processing_occurred = True
            
            raw_events = self.thought_buffer.get_unprocessed_events()
            
            if raw_events:
                # REACTIVE PROCESSING
                self.thought_buffer.reset_consecutive_counter()
                
                thoughts, actions = await self._reactive_processing(
                    raw_events, context_parts
                )
                
                if thoughts:
                    for thought_data in thoughts:
                        # PASS ALL METADATA INCLUDING TIMESTAMP
                        self.thought_buffer.add_processed_thought(
                            thought_data['content'], 
                            thought_data['source'],
                            thought_data.get('original_ref'),
                            priority_override=thought_data.get('priority_override'),
                            timestamp=thought_data.get('timestamp', time.time())
                        )
                
                # Execute actions
                if actions and self.tool_manager:
                    await self.tool_manager.execute_structured_actions(
                        actions, self.thought_buffer
                    )
                
                self.thought_buffer.mark_events_processed(len(raw_events))
                processing_occurred = True
            
            else:
                # PROACTIVE PROCESSING
                time_since_last_input = self.thought_buffer.get_time_since_last_user_input()
                
                decision = self.response_decider.decide_prompt_type(
                    has_incoming_input=False,
                    time_since_last_input=time_since_last_input,
                    thought_buffer=self.thought_buffer,
                    context_parts=context_parts
                )
                
                self.logger.system(f"[Proactive] {decision.reasoning}")
                
                result = await self._proactive_processing_by_type(
                    decision.prompt_type,
                    context_parts
                )
                
                if result:
                    proactive_thought = result.get('thought')
                    proactive_actions = result.get('actions', [])
                    
                    if proactive_thought:
                        self.thought_buffer.add_proactive_thought(proactive_thought)
                        processing_occurred = True
                    
                    if proactive_actions and self.tool_manager:
                        await self.tool_manager.execute_structured_actions(
                            proactive_actions, self.thought_buffer
                        )
            
            # Background maintenance
            await self._check_urgent_reminders()
            
            if time.time() - self._last_memory_integration > 120.0:
                await self.thinking_modes.periodic_memory_integration()
                self._last_memory_integration = time.time()
            
            return processing_occurred
        
        finally:
            self._is_processing = False
    
    # ========================================================================
    # REACTIVE PROCESSING - REFACTORED
    # ========================================================================
    
    async def _reactive_processing(self, raw_events, context_parts):
        """
        Process events reactively - REFACTORED
        NOW PRESERVES PRIORITY AND TIMESTAMP THROUGH PIPELINE
        """
        from BASE.core.thought_buffer import Priority
        
        self.logger.tool(
            f"[REACTIVE] Processing {len(raw_events)} events:\n" + 
            "\n".join([f"  [{i}] {e.source}: {e.data[:80]}" for i, e in enumerate(raw_events)])
        )
        
        # Get context
        recent_thoughts = self.thought_buffer.get_thoughts_for_response()[-10:]
        last_user_msg = self.thought_buffer.get_last_user_input()
        
        # Get pending actions
        pending_actions = ""
        if self.action_state_manager:
            pending_actions = self.action_state_manager.get_context_summary()
        
        # Detect special conditions
        has_vision = any(e.source == 'vision_result' for e in raw_events)
        
        # Build prompt using ResponsiveConstructor
        prompt = self.responsive_constructor.build_responsive_prompt(
            thought_chain=recent_thoughts,
            raw_events=raw_events,
            context_parts=context_parts,
            last_user_msg=last_user_msg,
            pending_actions=pending_actions,
            has_vision=has_vision
        )
        
        # Call LLM
        response = self._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        # Parse response
        parsed = self._parse_thought_response(response)
        
        self.logger.tool(
            f"[REACTIVE RESULT] "
            f"Thoughts: {len(parsed['thoughts'])}, "
            f"Actions: {len(parsed['actions'])}, "
            f"Plan: {bool(parsed['strategic_plan'])}"
        )
        
        # Convert to internal format WITH PRIORITY AND TIMESTAMP PRESERVATION
        thoughts = []
        for i, thought_text in enumerate(parsed['thoughts']):
            event = raw_events[i] if i < len(raw_events) else raw_events[-1]
            
            # Get event timestamp
            event_timestamp = getattr(event, 'timestamp', time.time())
            
            # Determine priority from event source
            priority_override = Priority.from_source(event.source)
            
            # Additional priority logic
            if hasattr(event, 'source'):
                if event.source == 'user_input':
                    priority_override = Priority.HIGH
                elif 'chat' in event.source.lower():
                    priority_override = self._detect_chat_urgency(event.data)
            
            # Log priority assignment
            self.logger.system(
                f"[Priority Assignment] Event {i+1}: "
                f"source={event.source}, priority={priority_override}"
            )
            
            # Store thought data (will be formatted by add_processed_thought)
            thoughts.append({
                'content': str(thought_text),  # Raw content
                'source': event.source if hasattr(event, 'source') else 'unknown',
                'original_ref': event.data if hasattr(event, 'data') else '',
                'priority_override': priority_override,
                'timestamp': event_timestamp  # PRESERVE ORIGINAL TIMESTAMP
            })
        
        # Add strategic plan
        if parsed['strategic_plan']:
            thoughts.append({
                'content': str(parsed['strategic_plan']), 
                'source': 'internal',
                'original_ref': '', 
                'priority_override': Priority.LOW,
                'timestamp': time.time()
            })
        
        # Validate actions
        actions = self._validate_actions(parsed['actions'])
        
        return thoughts, actions
    
    # ========================================================================
    # PROACTIVE PROCESSING - REFACTORED
    # ========================================================================
    
    async def _proactive_processing_by_type(
        self,
        prompt_type: PromptType,
        context_parts: List[str]
    ) -> Optional[Dict]:
        """
        Generate proactive thought using appropriate constructor
        NEW: Dispatcher based on PromptType
        
        Args:
            prompt_type: Type of prompt to construct
            context_parts: Context strings
        
        Returns:
            Dict with 'thought' and optional 'actions'
        """
        recent_thoughts = self.thought_buffer.get_thoughts_for_response()[-5:]
        ongoing_ctx = self.thought_buffer.get_ongoing_context()
        
        if prompt_type == PromptType.REFLECTIVE:
            # Use ReflectiveConstructor
            thought_count = len(self.thought_buffer.get_thoughts_for_response())
            is_startup = thought_count < 3
            
            prompt = self.reflective_constructor.build_reflective_prompt(
                thought_chain=recent_thoughts,
                ongoing_context=ongoing_ctx if ongoing_ctx else "Reflecting on recent activity",
                query=ongoing_ctx[:100] if ongoing_ctx else None,
                is_startup=is_startup
            )
        
        elif prompt_type == PromptType.PLANNING:
            # Use PlanningConstructor
            time_since_user = self.thought_buffer.get_time_since_last_user_input()
            time_context = (
                f"{username} was active {time_since_user // 60:.0f} minutes ago"
                if time_since_user < 9999 else "No recent user input"
            )
            
            prompt = self.planning_constructor.build_planning_prompt(
                thought_chain=recent_thoughts,
                ongoing_context=ongoing_ctx if ongoing_ctx else "Open time for planning",
                time_context=time_context
            )
        
        else:
            # Default to planning
            prompt = self.planning_constructor.build_planning_prompt(
                thought_chain=recent_thoughts,
                ongoing_context=ongoing_ctx if ongoing_ctx else "Planning next actions",
                time_context=None
            )
        
        # Call LLM
        response = self._call_ollama(
            prompt=prompt, model=self.config.thought_model, system_prompt=None
        )
        
        # Parse response
        return self._parse_thinking_response(response)
    
    def _parse_thinking_response(self, response: str) -> Optional[Dict]:
        """Parse LLM response for thought and actions"""
        think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL | re.IGNORECASE)
        action_match = re.search(r'<action_list>(.*?)</action_list>', response, re.DOTALL | re.IGNORECASE)
        
        thought = None
        actions = []
        
        if think_match:
            thought = think_match.group(1).strip()
            if not (10 <= len(thought) <= 300):
                thought = None
        
        if action_match:
            action_json = action_match.group(1).strip()
            action_json = re.sub(r'```json|```', '', action_json).strip()
            if action_json and action_json != '[]':
                try:
                    actions = json.loads(action_json)
                    if not isinstance(actions, list):
                        actions = []
                except:
                    actions = []
        
        if thought:
            return {'thought': thought, 'actions': actions}
        
        return None
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _check_chat_engagement_need(self) -> bool:
        """Check if chat engagement needed"""
        chat_enabled = getattr(self.controls, 'CHAT_ENGAGEMENT', False)
        if not chat_enabled:
            return False
        return self.thought_buffer.should_engage_with_chat()
    
    def _create_chat_engagement_thought(self) -> Optional[Dict]:
        """Create chat engagement thought"""
        from BASE.core.thought_buffer import Priority
        
        unengaged = self.thought_buffer.get_unengaged_messages(max_messages=5)
        if not unengaged:
            return None
        
        chat_summary_parts = []
        has_mention, has_question = False, False
        
        for msg in unengaged:
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
        
        return {
            'content': thought_content, 
            'source': 'chat_engagement',
            'original_ref': summary, 
            'priority_override': priority
        }
    
    def _detect_chat_urgency(self, chat_message: str) -> str:
        """Detect priority for chat messages"""
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
        """Validate actions against available tools"""
        if not actions or not self.tool_manager:
            return []
        
        valid_actions = []
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        
        for action in actions:
            if not isinstance(action, dict) or 'tool' not in action or 'args' not in action:
                continue
            
            tool_name = action['tool']
            tool_category = tool_name.split('.')[0] if '.' in tool_name else tool_name
            
            # "instructions" is always valid
            if tool_category == 'instructions':
                valid_actions.append(action)
                continue
            
            # Check if tool is enabled
            if tool_category in enabled_tools:
                valid_actions.append(action)
            else:
                self.logger.warning(
                    f"[Action Validation] Rejected (tool not enabled): {tool_name}"
                )
        
        return valid_actions
    
    async def _check_urgent_reminders(self):
        """Background reminder check (handled by tool system)"""
        pass
    
    # ========================================================================
    # STATE ACCESS
    # ========================================================================
    
    def get_performance_stats(self) -> Dict:
        """Get processing statistics"""
        pending_count = 0
        if self.action_state_manager:
            pending_count = len(self.action_state_manager.get_pending_actions())
        
        return {
            'thought_buffer_size': len(self.thought_buffer._thoughts),
            'raw_events_pending': len(self.thought_buffer.get_unprocessed_events()),
            'unspoken_thoughts': self.thought_buffer.count_unspoken_thoughts(),
            'max_urgency': self.thought_buffer.get_highest_priority(),
            'pending_actions': pending_count,
            'has_memory_search': self.memory_search is not None,
            'last_memory_integration': self._last_memory_integration,
            'cognitive_loop_active': self.cognitive_loop is not None,
            'prompt_system': 'modular'  # Flag for new system
        }