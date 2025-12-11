# Filename: BASE/core/thought_buffer.py
"""
THOUGHT BUFFER - Core Cognitive State Management
==================================================
Central storage for the agent's internal thoughts and observations.
Manages thought accumulation, priority tracking, and response decision logic.

Key Responsibilities:
- Store and organize processed thoughts with priority levels
- Track raw incoming events before interpretation
- Determine when agent should speak based on thought accumulation
- Manage chat engagement state and user interaction tracking
- Provide formatted context for prompt construction

Priority System:
- Uses string tags: [LOW], [MEDIUM], [HIGH], [CRITICAL]
- Maps to numeric values internally for comparisons only
- All external APIs use string tags for clarity
"""
import time
from typing import List, Dict, Tuple, Optional, Deque, Any 
from collections import deque
from dataclasses import dataclass, field
import datetime

from personality.bot_info import agentname, username


# ============================================================================
# PRIORITY SYSTEM
# ============================================================================

class Priority:
    """
    String-based priority system for thought classification.
    Uses descriptive tags instead of numeric values for clarity.
    """
    LOW = "[LOW]"
    MEDIUM = "[MEDIUM]"
    HIGH = "[HIGH]"
    CRITICAL = "[CRITICAL]"
    
    @staticmethod
    def to_numeric(priority: str) -> int:
        """Convert priority tag to numeric for internal comparisons only."""
        mapping = {
            "[LOW]": 1,
            "[MEDIUM]": 5,
            "[HIGH]": 8,
            "[CRITICAL]": 10
        }
        return mapping.get(priority, 5)
    
    @staticmethod
    def from_source(source: str) -> str:
        """Determine priority tag from event source type."""
        priority_map = {
            'urgent_reminder': Priority.CRITICAL,
            'direct_mention': Priority.CRITICAL,
            'user_input': Priority.HIGH,
            'chat_direct_mention': Priority.CRITICAL,
            'chat_question': Priority.HIGH,
            'chat_message': Priority.MEDIUM,
            'tool_timeout': Priority.HIGH,
            'tool_failed': Priority.HIGH,
            'vision_result': Priority.MEDIUM,
            'search_result': Priority.MEDIUM,
            'memory_result': Priority.MEDIUM,
            'tool_initiated': Priority.MEDIUM,
            'tool_pending': Priority.LOW,
            'observation': Priority.LOW,
            'internal': Priority.LOW,
            'proactive_reflection': Priority.LOW,
            'ambient': Priority.LOW,
            'response_echo': Priority.LOW,
            'tool_result': Priority.MEDIUM,
            'tool_instructions': Priority.MEDIUM,
            'tool_enforcement': Priority.HIGH,
            'tool_disabled': Priority.HIGH,
            'tool_error': Priority.HIGH,
            'chat_engagement': Priority.MEDIUM
        }
        return priority_map.get(source, Priority.MEDIUM)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

def _format_timestamp(timestamp: float) -> str:
    """Format timestamp for context display."""
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object.strftime("[%A, %B %d, %Y at %I:%M:%S %p]")


@dataclass
class RawDataEvent:
    """Unprocessed incoming data awaiting interpretation."""
    source: str
    data: str
    timestamp: float = field(default_factory=time.time)
    processed: bool = False


@dataclass
class ProcessedThought:
    """Interpreted thought with priority and metadata."""
    content: str
    source: str
    timestamp: float
    priority: str  # [LOW], [MEDIUM], [HIGH], or [CRITICAL]
    original_ref: Optional[str] = None
    spoken_in_response: bool = False


# ============================================================================
# THOUGHT BUFFER
# ============================================================================

class ThoughtBuffer:
    """
    Central cognitive state manager for the agent.
    
    Maintains two parallel buffers:
    1. Raw events (unprocessed observations)
    2. Processed thoughts (interpreted cognitions with priority)
    
    Provides context formatting and decision logic for:
    - When to generate new thoughts (reactive vs proactive)
    - When to produce spoken responses
    - Chat engagement timing
    """
    
    __slots__ = (
        '_raw_events', '_thoughts', 'max_thoughts',
        'last_response_time', 'last_thought_generation', 
        'current_goal', 'goal_set_time', 'goal_progress_thoughts', 
        'goals_achieved', 'has_urgent_reminders', 'urgent_reminder_count',
        '_response_counter', 'last_proactive_thought_time', 
        'ongoing_context', 'last_user_input', 'last_user_input_time',
        'min_proactive_interval', 'max_proactive_interval',
        'thought_momentum', 'consecutive_proactive_thoughts',
        'last_cognitive_activity', '_shutdown_requested', 
        'chat_engagement'
    )
    
    def __init__(self, max_thoughts=25):
        # Core buffers
        self._raw_events: Deque[RawDataEvent] = deque(maxlen=50)
        self._thoughts: Deque[ProcessedThought] = deque(maxlen=max_thoughts)
        
        # Configuration
        self.max_thoughts = max_thoughts
        
        # Timing state
        self.last_response_time = 0.0
        self.last_thought_generation = 0.0
        self.last_proactive_thought_time = 0.0
        self.last_cognitive_activity = time.time()
        self._response_counter = 0
        
        # User interaction tracking
        self.last_user_input = ""
        self.last_user_input_time = 0.0
        
        # Context management
        self.ongoing_context = ""
        
        # Goal tracking
        self.current_goal = None
        self.goal_set_time = None
        self.goal_progress_thoughts = []
        self.goals_achieved = []
        
        # Urgent reminders
        self.has_urgent_reminders = False
        self.urgent_reminder_count = 0
        
        # Proactive thinking parameters
        self.min_proactive_interval = 5.0
        self.max_proactive_interval = 15.0
        self.thought_momentum = 0.5
        self.consecutive_proactive_thoughts = 0
        
        # System control
        self._shutdown_requested = False
        
        # Chat engagement subsystem
        from BASE.handlers.chat_engagement import ChatEngagement
        self.chat_engagement = ChatEngagement(thought_buffer_ref=self)

    # ========================================================================
    # CONTEXT FORMATTING - For prompt construction
    # ========================================================================

    def _format_thought(self, thought: ProcessedThought) -> str:
        """Format single thought for context display."""
        timestamp_str = _format_timestamp(thought.timestamp)
        content = thought.content
        
        # Special formatting for response echoes
        if thought.source == 'response_echo':
            content = f"I said: {content}"
        
        return f"{timestamp_str} {content}"

    def get_thoughts_for_context(self) -> str:
        """
        Get formatted thought history for prompt context.
        Returns last 25 thoughts with timestamps.
        """
        formatted_thoughts = [
            self._format_thought(thought)
            for thought in self._thoughts
        ]
        return "\n".join(formatted_thoughts)
    
    # ========================================================================
    # RESPONSE ECHO - Immediate feedback after speaking
    # ========================================================================

    def add_response_echo(self, response_text: str, timestamp: Optional[float] = None):
        """
        Add agent's spoken response as thought echo.
        Called immediately after TTS generation.
        """
        if timestamp is None:
            timestamp = time.time()
            
        echo_thought = ProcessedThought(
            content=response_text,
            source='response_echo',
            timestamp=timestamp,
            priority=Priority.LOW,
            spoken_in_response=True
        )
        self._thoughts.append(echo_thought)
        self.last_response_time = timestamp
    
    # ========================================================================
    # USER INPUT TRACKING
    # ========================================================================
    
    def set_last_user_input(self, user_input: str):
        """Track most recent user input for context."""
        if user_input and user_input.strip():
            self.last_user_input = user_input.strip()
            self.last_user_input_time = time.time()
    
    def get_last_user_input(self) -> str:
        """Get most recent user input."""
        return self.last_user_input
    
    def has_recent_user_input(self, max_age: float = 30.0) -> bool:
        """Check if user input is recent enough to be relevant."""
        if not self.last_user_input:
            return False
        return (time.time() - self.last_user_input_time) < max_age
    
    def get_user_context(self) -> str:
        """Get formatted user context for prompts (returns empty if stale)."""
        if not self.last_user_input:
            return ""
        
        age = time.time() - self.last_user_input_time
        if age > 60.0:  # Input older than 1 minute is stale
            return ""
        
        return f"Recent user request: {self.last_user_input}"
    
    def get_time_since_last_user_input(self) -> float:
        """Get seconds since last user input."""
        if not self.last_user_input:
            return 999999.0
        return time.time() - self.last_user_input_time
    
    def clear_stale_user_input(self, max_age: float = 20.0):
        """Clear user input if too old."""
        if not self.last_user_input:
            return
        
        age = time.time() - self.last_user_input_time
        if age > max_age:
            self.last_user_input = ""
            self.last_user_input_time = 0.0
    
    # ========================================================================
    # PROACTIVE THINKING CONTROL
    # ========================================================================
    
    def should_generate_proactive_thought(self) -> bool:
        """
        Determine if agent should generate proactive thought.
        True continuous thinking: always returns True if no reactive work pending.
        """
        # Block if reactive work pending
        if len(self.get_unprocessed_events()) > 0:
            return False
        return True
    
    def add_proactive_thought(self, content: str):
        """Add proactive thought with quality tracking."""
        self.add_processed_thought(
            content=content,
            source='proactive_reflection',
            original_ref=None
        )
        self.last_proactive_thought_time = time.time()
        self.last_cognitive_activity = time.time()
        self.consecutive_proactive_thoughts += 1
        
        # Adjust momentum based on thought quality
        content_lower = content.lower()
        high_quality_indicators = [
            'wonder', 'curious', 'should check', 'could', 'might want',
            'consider', 'need to', 'want to', 'plan', 'prepare',
            'notice', 'observe', 'realize', 'think about', 'remember',
            'recall', 'past', 'future', 'next', 'if', 'when'
        ]
        
        is_high_quality = sum(1 for ind in high_quality_indicators if ind in content_lower)
        
        if is_high_quality > 0:
            self.thought_momentum = min(1.0, self.thought_momentum + 0.1)
        else:
            self.thought_momentum = max(0.3, self.thought_momentum - 0.05)

    def reset_consecutive_counter(self):
        """Reset proactive counter when external input received."""
        self.consecutive_proactive_thoughts = 0
        self.thought_momentum = 0.6
        self.last_cognitive_activity = time.time()
    
    def get_thinking_stats(self) -> Dict[str, Any]:
        """Get current thinking state for diagnostics."""
        return {
            'consecutive_proactive': self.consecutive_proactive_thoughts,
            'momentum': self.thought_momentum,
            'can_think_proactively': self.should_generate_proactive_thought(),
            'time_since_last_proactive': time.time() - self.last_proactive_thought_time,
            'time_since_activity': time.time() - self.last_cognitive_activity
        }
    
    def decay_momentum(self):
        """
        Decay thought momentum when no processing occurs
        Called when idle cycles happen
        """
        # Gradual decay
        self.thought_momentum = max(0.3, self.thought_momentum - 0.02)
        
        # Update last activity time
        self.last_cognitive_activity = time.time()
    
    # ========================================================================
    # ONGOING CONTEXT MANAGEMENT
    # ========================================================================
    
    def set_ongoing_context(self, context: str):
        """Set current focus area for the agent."""
        self.ongoing_context = context

    def get_ongoing_context(self) -> str:
        """
        Get current focus area.
        Priority order: user input > manual context > current goal
        """
        user_ctx = self.get_user_context()
        if user_ctx:
            return user_ctx
        
        if self.ongoing_context:
            return self.ongoing_context
        
        if self.current_goal:
            return f"Goal: {self.current_goal['description']}"
        
        return ""
    
    # ========================================================================
    # RAW DATA INGESTION
    # ========================================================================

    def force_shutdown(self):
        """Request immediate shutdown (kill command)."""
        self._shutdown_requested = True
    
    def is_shutdown_requested(self) -> bool:
        """Check if shutdown was requested."""
        return self._shutdown_requested
    
    def ingest_raw_data(self, source: str, data: str):
        """Add raw event to processing queue."""
        if source == 'user_input':
            self.set_last_user_input(data)
        
        self._raw_events.append(RawDataEvent(source, data))

    def get_unprocessed_events(self) -> List[RawDataEvent]:
        """Get events awaiting interpretation."""
        return [e for e in self._raw_events if not e.processed]
    
    def mark_events_processed(self, count: int):
        """Mark N oldest events as processed."""
        for event in self._raw_events:
            if not event.processed and count > 0:
                event.processed = True
                count -= 1
    
    def clear_old_events(self, max_age: float = 30.0):
        """Remove old processed events."""
        cutoff = time.time() - max_age
        kept = [e for e in self._raw_events 
                if e.timestamp > cutoff or not e.processed]
        self._raw_events.clear()
        self._raw_events.extend(kept)
    
    # ========================================================================
    # PROCESSED THOUGHTS
    # ========================================================================
    
    def add_processed_thought(
        self, 
        content: str, 
        source: str, 
        original_ref: str = None,
        priority_override: Optional[str] = None
    ):
        """
        Add interpreted thought with priority.
        
        Args:
            content: Thought text
            source: Event source type
            original_ref: Original event data
            priority_override: Override priority ([LOW], [MEDIUM], [HIGH], [CRITICAL])
        """
        # Determine priority
        if priority_override and priority_override in [
            Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL
        ]:
            priority = priority_override
        else:
            priority = Priority.from_source(source)
        
        # Track urgent reminders
        if source == 'urgent_reminder':
            self.has_urgent_reminders = True
            self.urgent_reminder_count += 1
        
        self._thoughts.append(ProcessedThought(
            content=content,
            source=source,
            timestamp=time.time(),
            priority=priority,
            original_ref=original_ref,
            spoken_in_response=False
        ))
        
        self.last_thought_generation = time.time()

    def get_thoughts_for_response(
        self, 
        min_priority: str = Priority.LOW,
        only_unspoken: bool = False
    ) -> List[str]:
        """
        Get thought contents for response generation.
        
        Args:
            min_priority: Minimum priority level
            only_unspoken: Only return unspoken thoughts
        
        Returns:
            List of thought content strings
        """
        thoughts = list(self._thoughts)
        
        # Filter by priority
        if min_priority != Priority.LOW:
            min_priority_value = Priority.to_numeric(min_priority)
            thoughts = [
                t for t in thoughts 
                if Priority.to_numeric(t.priority) >= min_priority_value
            ]
        
        # Filter by spoken status
        if only_unspoken:
            thoughts = [t for t in thoughts if not t.spoken_in_response]
        
        # Extract content
        thought_contents = []
        for t in thoughts:
            content = t.content
            # Special handling for user input echoes
            if content == "I noticed: user_input" and t.source == 'user_input':
                content = f"{username} said: {self.get_last_user_input()}"
            thought_contents.append(content)
        
        return thought_contents
    
    def get_recent_context(self, last_n: int = 10) -> List[str]:
        """Get recent thought contents for context."""
        recent = list(self._thoughts)[-last_n:]
        return [t.content for t in recent]
    
    def mark_thoughts_spoken(self, count: Optional[int] = None):
        """Mark thoughts as spoken in response."""
        if count is None:
            # Mark all unspoken
            for thought in self._thoughts:
                if not thought.spoken_in_response:
                    thought.spoken_in_response = True
        else:
            # Mark last N unspoken
            unspoken = [t for t in self._thoughts if not t.spoken_in_response]
            for thought in unspoken[-count:]:
                thought.spoken_in_response = True
    
    def get_thoughts(self, last_n: Optional[int] = None) -> List[Dict]:
        """Get thoughts as dictionaries with metadata."""
        thoughts_list = []
        for t in self._thoughts:
            thoughts_list.append({
                'content': t.content,
                'source': t.source,
                'timestamp': t.timestamp,
                'priority': t.priority,
                'priority_numeric': Priority.to_numeric(t.priority),
                'original_text': t.original_ref or '',
                'spoken': t.spoken_in_response
            })
        
        if last_n is not None:
            return thoughts_list[-last_n:]
        return thoughts_list
    
    def get_highest_priority(self) -> str:
        """Get highest priority among all thoughts."""
        if not self._thoughts:
            return Priority.LOW
        
        max_priority_value = 0
        max_priority = Priority.LOW
        
        for thought in self._thoughts:
            priority_value = Priority.to_numeric(thought.priority)
            if priority_value > max_priority_value:
                max_priority_value = priority_value
                max_priority = thought.priority
        
        return max_priority
    
    def count_unspoken_thoughts(self) -> int:
        """Count thoughts not yet spoken about."""
        return sum(1 for t in self._thoughts if not t.spoken_in_response)
    
    # ========================================================================
    # RESPONSE DECISION LOGIC
    # ========================================================================
    
    def should_generate_thoughts(self) -> bool:
        """Check if cognitive processing should occur."""
        # Process pending events
        if len(self.get_unprocessed_events()) > 0:
            return True
        
        # Generate proactive thoughts
        if self.should_generate_proactive_thought():
            return True
        
        return False
    
    def should_speak(self) -> Tuple[bool, str, str]:
        """
        Determine if agent should produce spoken output.
        
        Returns:
            (should_speak, reason, priority_level)
        """
        if not self._thoughts:
            # Check chat engagement as fallback
            if self.chat_engagement.should_engage_with_chat():
                return True, "chat_engagement", Priority.HIGH
            return False, "no_thoughts", Priority.LOW
        
        # Urgent reminders take precedence
        if self.has_urgent_reminders:
            return True, "urgent_reminder", Priority.CRITICAL
        
        # Check max priority
        max_priority = self.get_highest_priority()
        max_priority_value = Priority.to_numeric(max_priority)
        
        # Direct address/questions
        if max_priority_value >= Priority.to_numeric(Priority.HIGH):
            return True, "direct_address", max_priority
        
        # Chat engagement check
        if self.chat_engagement.should_engage_with_chat():
            chat_priority, chat_reason = self.chat_engagement.get_chat_urgency_for_decision()
            if chat_priority != Priority.LOW:
                return True, chat_reason, chat_priority
        
        unspoken_count = self.count_unspoken_thoughts()
        
        if unspoken_count == 0:
            return False, "nothing_new_to_say", Priority.LOW
        
        # Accumulated high-value thoughts
        if unspoken_count >= 3 and max_priority_value >= Priority.to_numeric(Priority.MEDIUM):
            return True, "accumulated_observations", max_priority
        
        time_since_response = time.time() - self.last_response_time
        
        # Natural conversation rhythm
        if unspoken_count >= 5 and time_since_response > 30:
            return True, "natural_comment", max_priority
        
        if unspoken_count >= 8 and time_since_response > 15:
            return True, "many_observations", max_priority
        
        return False, "thinking_silently", Priority.LOW
    
    # ========================================================================
    # CHAT ENGAGEMENT DELEGATION
    # ========================================================================
    
    def ingest_chat_message(
        self, 
        platform: str, 
        username: str, 
        message: str,
        has_bot_mention: bool = False
    ):
        """Delegate to chat engagement module."""
        self.chat_engagement.ingest_chat_message(
            platform, username, message, has_bot_mention
        )
    
    def should_engage_with_chat(self) -> bool:
        """Delegate to chat engagement module."""
        return self.chat_engagement.should_engage_with_chat()
    
    def mark_chat_engaged(
        self, 
        message_ids: Optional[List[int]] = None,
        batch_mode: bool = False
    ):
        """Delegate to chat engagement module."""
        self.chat_engagement.mark_chat_engaged(message_ids, batch_mode)
    
    def get_unengaged_messages(self, max_messages: int = 5) -> List[Dict]:
        """Delegate to chat engagement module."""
        return self.chat_engagement.get_unengaged_messages(max_messages)
    
    def get_chat_engagement_stats(self) -> Dict[str, Any]:
        """Delegate to chat engagement module."""
        return self.chat_engagement.get_chat_engagement_stats()
    
    # ========================================================================
    # GOAL MANAGEMENT
    # ========================================================================
    
    def set_goal(self, goal_description: str, reason: str = ""):
        """Set new goal for agent."""
        self.current_goal = {
            "description": goal_description,
            "reason": reason,
            "set_at": time.time(),
            "progress_count": 0,
        }
        self.goal_set_time = time.time()
        self.goal_progress_thoughts = []
    
    def add_goal_progress(self, progress_note: str):
        """Track progress toward current goal."""
        if self.current_goal:
            self.goal_progress_thoughts.append({
                "note": progress_note, 
                "timestamp": time.time()
            })
            self.current_goal["progress_count"] += 1
    
    def achieve_goal(self, achievement_note: str = ""):
        """Mark current goal as achieved."""
        if self.current_goal:
            self.goals_achieved.append({
                "goal": self.current_goal["description"],
                "reason": self.current_goal["reason"],
                "achieved_at": time.time(),
                "duration": time.time() - self.current_goal["set_at"],
                "progress_count": self.current_goal["progress_count"],
                "achievement_note": achievement_note,
            })
            self.current_goal = None
            self.goal_set_time = None
            self.goal_progress_thoughts = []
    
    def get_goal_summary(self) -> str:
        """Get formatted goal summary for prompts."""
        if not self.current_goal:
            return ""
        
        duration = time.time() - self.current_goal["set_at"]
        progress = self.current_goal["progress_count"]
        
        summary = f"CURRENT GOAL: {self.current_goal['description']}"
        if self.current_goal["reason"]:
            summary += f"\nREASON: {self.current_goal['reason']}"
        summary += f"\nPROGRESS: {progress} actions ({duration:.0f}s elapsed)"
        
        if self.goal_progress_thoughts:
            recent = self.goal_progress_thoughts[-3:]
            summary += "\nRECENT PROGRESS:\n" + "\n".join(
                [f"- {p['note']}" for p in recent]
            )
        
        return summary
    
    # ========================================================================
    # URGENT REMINDERS
    # ========================================================================
    
    def acknowledge_urgent_reminders(self):
        """Clear urgent reminder flags after acknowledgment."""
        self.has_urgent_reminders = False
        self.urgent_reminder_count = 0