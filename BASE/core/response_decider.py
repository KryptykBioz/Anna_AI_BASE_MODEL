# Filename: BASE/core/response_decider.py
"""
Response Decider - Determines Prompt Type and Response Strategy
===============================================================
Analyzes context to decide:
1. Which prompt constructor to use (spoken/responsive/reflective/planning)
2. Whether a spoken response is needed
3. Priority level of the response

Decision Flow:
- Incoming input → Responsive prompt (process new data)
- Recent input (<6 min) + no new input → Planning prompt (set goals)
- No input (6+ min) → Reflective prompt (review memories)
- HIGH/CRITICAL markers in thoughts → Spoken response prompt (verbal output)

Separation of Concerns:
- This module: Decision logic only
- Constructor modules: Prompt assembly
- Generator modules: LLM interaction and output synthesis
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class PromptType(Enum):
    """Types of prompts the agent can construct"""
    RESPONSIVE = "responsive"   # Process incoming data
    PLANNING = "planning"       # Set goals, plan ahead
    REFLECTIVE = "reflective"   # Review memories, reflect
    SPOKEN = "spoken"           # Generate verbal response


class PriorityLevel(Enum):
    """Priority levels for response urgency"""
    CRITICAL = 10    # Urgent reminders, direct address
    HIGH = 8         # Direct questions, mentions
    MEDIUM = 5       # Notable events, chat activity
    LOW = 3          # Background activity
    SILENT = 1       # No response needed


@dataclass
class PromptDecision:
    """
    Container for prompt decision results
    
    Attributes:
        prompt_type: Which prompt constructor to use
        needs_spoken_response: Whether to generate verbal output
        priority_level: Response priority (affects prompt complexity)
        reasoning: Human-readable reasoning for decision
        context_flags: Additional flags for prompt construction
    """
    prompt_type: PromptType
    needs_spoken_response: bool
    priority_level: PriorityLevel
    reasoning: str
    context_flags: dict = None
    
    def __post_init__(self):
        if self.context_flags is None:
            self.context_flags = {}


class ResponseDecider:
    """
    Analyzes context to determine which prompt type to construct
    
    Decision Priority:
    1. HIGH/CRITICAL markers in thoughts → Spoken response
    2. Incoming input → Responsive thinking
    3. Recent input (<6 min) → Planning thinking
    4. No input (6+ min) → Reflective thinking
    """
    
    def __init__(self, agentname: str, username: str, logger=None):
        """
        Initialize response decider
        
        Args:
            agentname: Agent's name
            username: User's name
            logger: Optional logger instance
        """
        self.agentname = agentname
        self.username = username
        self.logger = logger
        
        # Timing thresholds
        self.REFLECTION_THRESHOLD = 360.0  # 6 minutes in seconds
        
        # Priority markers in thoughts
        self.CRITICAL_MARKERS = ['URGENT', 'CRITICAL', 'IMMEDIATE']
        self.HIGH_MARKERS = ['HIGH', 'IMPORTANT', 'PRIORITY']
    
    # ========================================================================
    # MAIN DECISION ENTRY POINT
    # ========================================================================
    
    def decide_prompt_type(
        self,
        has_incoming_input: bool,
        time_since_last_input: float,
        thought_buffer = None,
        context_parts: List[str] = None
    ) -> PromptDecision:
        """
        Main entry point: Decide which prompt type to construct
        
        Args:
            has_incoming_input: Whether there's new input to process
            time_since_last_input: Seconds since last user input
            thought_buffer: ThoughtBuffer instance (for priority detection)
            context_parts: Additional context strings
        
        Returns:
            PromptDecision with complete analysis
        """
        context_parts = context_parts or []
        
        # 1. Check for priority markers in thought chain (highest priority)
        priority_level, has_spoken_trigger = self._detect_priority_markers(thought_buffer)
        
        # 2. If HIGH/CRITICAL markers present → Spoken response
        if has_spoken_trigger:
            return self._create_spoken_decision(priority_level)
        
        # 3. If incoming input → Responsive thinking
        if has_incoming_input:
            return self._create_responsive_decision(context_parts)
        
        # 4. If recent input (<6 min) → Planning thinking
        if time_since_last_input < self.REFLECTION_THRESHOLD:
            return self._create_planning_decision(time_since_last_input)
        
        # 5. If no input (6+ min) → Reflective thinking
        return self._create_reflective_decision(time_since_last_input)
    
    # ========================================================================
    # PRIORITY DETECTION
    # ========================================================================
    
    def _detect_priority_markers(
        self,
        thought_buffer
    ) -> Tuple[PriorityLevel, bool]:
        """
        Detect priority markers in thought chain - REFACTORED
        NOW SCANS FOR [HIGH] AND [CRITICAL] TAGS IN FORMATTED THOUGHTS
        
        Args:
            thought_buffer: ThoughtBuffer instance
        
        Returns:
            Tuple of (priority_level, has_spoken_trigger)
        """
        if not thought_buffer:
            return PriorityLevel.SILENT, False
        
        # Check for urgent reminders
        if hasattr(thought_buffer, 'has_urgent_reminders') and thought_buffer.has_urgent_reminders:
            if self.logger:
                self.logger.system("[Priority] CRITICAL: Urgent reminder detected")
            return PriorityLevel.CRITICAL, True
        
        # Get recent thoughts (already formatted with metadata)
        recent_thoughts = thought_buffer.get_thoughts_for_response()[-10:]
        
        if not recent_thoughts:
            return PriorityLevel.SILENT, False
        
        # Scan for priority tags in formatted thoughts
        has_critical = False
        has_high = False
        
        for thought in recent_thoughts:
            if '[CRITICAL]' in thought:
                has_critical = True
                if self.logger:
                    self.logger.system(f"[Priority] CRITICAL found: {thought[:100]}")
            elif '[HIGH]' in thought:
                has_high = True
                if self.logger:
                    self.logger.system(f"[Priority] HIGH found: {thought[:100]}")
        
        # Determine response priority
        if has_critical:
            if self.logger:
                self.logger.system("[Priority] → SPOKEN RESPONSE: CRITICAL priority detected")
            return PriorityLevel.CRITICAL, True
        
        if has_high:
            if self.logger:
                self.logger.system("[Priority] → SPOKEN RESPONSE: HIGH priority detected")
            return PriorityLevel.HIGH, True
        
        # Additional legacy checks (for backwards compatibility)
        thoughts_text = " ".join([str(t) for t in recent_thoughts]).upper()
        
        if self.agentname.upper() in thoughts_text:
            if self.logger:
                self.logger.system(f"[Priority] → SPOKEN RESPONSE: Agent mentioned")
            return PriorityLevel.HIGH, True
        
        # Check for question marks
        if '?' in thoughts_text:
            if self.logger:
                self.logger.system(f"[Priority] → SPOKEN RESPONSE: Question detected")
            return PriorityLevel.MEDIUM, True
        
        return PriorityLevel.SILENT, False
    
    # ========================================================================
    # DECISION CREATORS
    # ========================================================================
    
    def _create_spoken_decision(self, priority_level: PriorityLevel) -> PromptDecision:
        """Create decision for spoken response prompt"""
        reasoning = self._build_spoken_reasoning(priority_level)
        
        context_flags = {
            'is_urgent': priority_level == PriorityLevel.CRITICAL,
            'is_high_priority': priority_level == PriorityLevel.HIGH,
            'needs_personality_examples': True,
            'needs_memory_context': True
        }
        
        return PromptDecision(
            prompt_type=PromptType.SPOKEN,
            needs_spoken_response=True,
            priority_level=priority_level,
            reasoning=reasoning,
            context_flags=context_flags
        )
    
    def _create_responsive_decision(self, context_parts: List[str]) -> PromptDecision:
        """Create decision for responsive thinking prompt"""
        has_vision = self._detect_vision_data(context_parts)
        has_chat = self._detect_chat_data(context_parts)
        
        reasoning = "Incoming input detected → Responsive thinking mode"
        if has_vision:
            reasoning += " (vision data present)"
        if has_chat:
            reasoning += " (chat activity present)"
        
        context_flags = {
            'has_vision': has_vision,
            'has_chat': has_chat,
            'needs_tool_list': True,
            'needs_grounding_rules': has_vision
        }
        
        return PromptDecision(
            prompt_type=PromptType.RESPONSIVE,
            needs_spoken_response=False,
            priority_level=PriorityLevel.MEDIUM,
            reasoning=reasoning,
            context_flags=context_flags
        )
    
    def _create_planning_decision(self, time_since_last: float) -> PromptDecision:
        """Create decision for planning thinking prompt"""
        minutes = int(time_since_last / 60)
        reasoning = f"Recent input ({minutes}m ago) → Planning thinking mode"
        
        context_flags = {
            'needs_tool_list': True,
            'time_since_input': time_since_last,
            'is_proactive': True
        }
        
        return PromptDecision(
            prompt_type=PromptType.PLANNING,
            needs_spoken_response=False,
            priority_level=PriorityLevel.LOW,
            reasoning=reasoning,
            context_flags=context_flags
        )
    
    def _create_reflective_decision(self, time_since_last: float) -> PromptDecision:
        """Create decision for reflective thinking prompt"""
        minutes = int(time_since_last / 60)
        reasoning = f"No input for {minutes}m (6+ min threshold) → Reflective thinking mode"
        
        context_flags = {
            'needs_memory_retrieval': True,
            'needs_tool_list': True,
            'time_since_input': time_since_last,
            'is_reflection': True
        }
        
        return PromptDecision(
            prompt_type=PromptType.REFLECTIVE,
            needs_spoken_response=False,
            priority_level=PriorityLevel.LOW,
            reasoning=reasoning,
            context_flags=context_flags
        )
    
    # ========================================================================
    # CONTEXT DETECTION
    # ========================================================================
    
    def _detect_vision_data(self, context_parts: List[str]) -> bool:
        """Detect if vision data is present in context"""
        for part in context_parts:
            if any(indicator in part.lower() for indicator in [
                'vision', 'image', 'screenshot', 'visual', 'screen'
            ]):
                return True
        return False
    
    def _detect_chat_data(self, context_parts: List[str]) -> bool:
        """Detect if chat data is present in context"""
        for part in context_parts:
            if any(indicator in part.lower() for indicator in [
                'chat', 'live chat', 'twitch', 'viewer'
            ]):
                return True
        return False
    
    def _detect_memory_triggers(self, text: str) -> bool:
        """Detect if text contains memory-related keywords"""
        text_lower = text.lower()
        memory_triggers = [
            'remember', 'recall', 'before', 'earlier', 'yesterday',
            'last time', 'ago', 'used to', 'that time', 'we talked'
        ]
        return any(trigger in text_lower for trigger in memory_triggers)
    
    # ========================================================================
    # REASONING BUILDERS
    # ========================================================================
    
    def _build_spoken_reasoning(self, priority_level: PriorityLevel) -> str:
        """Build human-readable reasoning for spoken response"""
        if priority_level == PriorityLevel.CRITICAL:
            return "CRITICAL priority detected → Spoken response required"
        elif priority_level == PriorityLevel.HIGH:
            return "HIGH priority detected → Spoken response required"
        elif priority_level == PriorityLevel.MEDIUM:
            return "User question detected → Spoken response required"
        else:
            return "Priority marker detected → Spoken response mode"
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_prompt_constructor_path(self, prompt_type: PromptType) -> str:
        """
        Get the module path for the appropriate prompt constructor
        
        Args:
            prompt_type: Type of prompt to construct
        
        Returns:
            Module path string
        """
        constructor_map = {
            PromptType.SPOKEN: "BASE.core.spoken.spoken_constructor",
            PromptType.RESPONSIVE: "BASE.core.responsive.responsive_constructor",
            PromptType.REFLECTIVE: "BASE.core.reflective.reflective_constructor",
            PromptType.PLANNING: "BASE.core.planning.planning_constructor"
        }
        return constructor_map[prompt_type]
    
    def should_log_decision(self, decision: PromptDecision) -> bool:
        """Determine if this decision should be logged"""
        # Always log spoken responses and reflective mode
        return decision.needs_spoken_response or decision.prompt_type == PromptType.REFLECTIVE
    
    def format_decision_summary(self, decision: PromptDecision) -> str:
        """Format decision as summary string for logging"""
        parts = [
            f"Type: {decision.prompt_type.value}",
            f"Priority: {decision.priority_level.name}",
            f"Spoken: {decision.needs_spoken_response}"
        ]
        
        if decision.context_flags:
            flags = [k for k, v in decision.context_flags.items() if v]
            if flags:
                parts.append(f"Flags: {', '.join(flags)}")
        
        return " | ".join(parts)
    
    # ========================================================================
    # DEBUG METHODS
    # ========================================================================
    
    def log_priority_scan_results(self, thought_buffer):
        """
        Debug logging for priority detection.
        Call this after _detect_priority_markers for detailed diagnostics.
        """
        if not self.logger:
            return
        
        recent_thoughts = thought_buffer.get_thoughts_for_response()[-10:]
        
        if not recent_thoughts:
            self.logger.system("[Priority Scan] No thoughts in buffer")
            return
        
        self.logger.system("[Priority Scan] Analysis:")
        self.logger.system(f"  Total thoughts: {len(recent_thoughts)}")
        
        # Count by priority
        critical_count = sum(1 for t in recent_thoughts if '[CRITICAL]' in t)
        high_count = sum(1 for t in recent_thoughts if '[HIGH]' in t)
        medium_count = sum(1 for t in recent_thoughts if '[MEDIUM]' in t)
        low_count = sum(1 for t in recent_thoughts if '[LOW]' in t)
        
        self.logger.system(f"  CRITICAL: {critical_count}")
        self.logger.system(f"  HIGH: {high_count}")
        self.logger.system(f"  MEDIUM: {medium_count}")
        self.logger.system(f"  LOW: {low_count}")
        
        # Show HIGH and CRITICAL thoughts
        if critical_count > 0 or high_count > 0:
            self.logger.system("  Priority thoughts:")
            for thought in recent_thoughts:
                if '[CRITICAL]' in thought or '[HIGH]' in thought:
                    self.logger.system(f"    {thought[:120]}")