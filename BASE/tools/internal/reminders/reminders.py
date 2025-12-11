# Filename: BASE/tools/reminder_tool.py
"""
Reminder and Timer Tool for AI Agent
Manages persistent reminders and timers with context injection
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class Reminder:
    """Individual reminder/timer entry"""
    id: str
    description: str
    trigger_time: float  # Unix timestamp
    created_at: float
    reminder_type: str  # 'reminder', 'timer', 'event'
    repeat_interval: Optional[float] = None  # Seconds, None = no repeat
    notified: bool = False
    is_urgent: bool = False  # ADD THIS LINE
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'Reminder':
        # Handle old reminders without is_urgent field
        if 'is_urgent' not in data:
            data['is_urgent'] = False
        return Reminder(**data)
    
    def is_due(self, current_time: float) -> bool:
        """Check if reminder is due"""
        return current_time >= self.trigger_time and not self.notified
    
    def is_upcoming(self, current_time: float, window_seconds: float = 3600) -> bool:
        """Check if reminder is coming up within window"""
        return 0 < (self.trigger_time - current_time) <= window_seconds
    
    def get_time_until(self, current_time: float) -> str:
        """Get human-readable time until reminder"""
        diff = self.trigger_time - current_time
        
        if diff < 0:
            return "overdue"
        elif diff < 60:
            return f"{int(diff)} seconds"
        elif diff < 3600:
            return f"{int(diff / 60)} minutes"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = int(diff / 86400)
            return f"{days} day{'s' if days != 1 else ''}"
    
    def get_datetime_str(self) -> str:
        """Get formatted datetime string"""
        dt = datetime.fromtimestamp(self.trigger_time)
        return dt.strftime("%Y-%m-%d %I:%M %p")


class ReminderTool:
    """
    Manages reminders and timers with persistent storage
    Integrates with thinking model for context-aware reminders
    """
    
    def __init__(self, project_root: Path, controls_module=None):
        self.project_root = project_root
        self.controls = controls_module
        self.storage_file = project_root / "personality" / "memory" / "reminders.json"
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory reminder list
        self.reminders: List[Reminder] = []
        
        # Tracking
        self.last_check_time = 0
        self.check_interval = 30  # Check every 30 seconds
        self.pending_notifications: List[Reminder] = []
        
        # ADD THIS: Track which reminders have been announced to user
        self.announced_reminder_ids = set()
        
        # Load existing reminders
        self._load_reminders()
        
        # ADD THIS: Flag urgent missed reminders
        self._flag_urgent_missed_reminders()
        
        # Process any overdue reminders from when agent was offline
        self._process_missed_reminders()
    
    # === PERSISTENCE ===
    
    def _load_reminders(self):
        """Load reminders from persistent storage"""
        if not self.storage_file.exists():
            self.reminders = []
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            self.reminders = [Reminder.from_dict(r) for r in data.get('reminders', [])]
            print(f"[Reminders] Loaded {len(self.reminders)} reminders from storage")
            
        except Exception as e:
            print(f"[Reminders] Error loading reminders: {e}")
            self.reminders = []
    
    def _save_reminders(self):
        """Save reminders to persistent storage"""
        try:
            data = {
                'reminders': [r.to_dict() for r in self.reminders],
                'last_saved': time.time()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print(f"[Reminders] Error saving reminders: {e}")
    
    # === REMINDER MANAGEMENT ===

    def _flag_urgent_missed_reminders(self):
        """Flag reminders that were missed while offline as urgent"""
        current_time = time.time()
        missed_count = 0
        
        for reminder in self.reminders:
            if reminder.trigger_time < current_time and not reminder.notified:
                # This is a missed reminder - mark as urgent
                reminder.is_urgent = True
                missed_count += 1
                print(f"[Reminders] MISSED: '{reminder.description}' (was due at {reminder.get_datetime_str()})")
        
        if missed_count > 0:
            print(f"[Reminders] Found {missed_count} urgent missed reminder(s) on startup")
    
    def add_reminder(self, description: str, trigger_time: float, 
                    reminder_type: str = 'reminder', 
                    repeat_interval: Optional[float] = None) -> Reminder:
        """
        Add a new reminder
        
        Args:
            description: What to remind about
            trigger_time: Unix timestamp when to trigger
            reminder_type: 'reminder', 'timer', or 'event'
            repeat_interval: Seconds between repeats (None = no repeat)
        
        Returns:
            Created Reminder object
        """
        reminder_id = f"{int(time.time() * 1000)}"
        
        reminder = Reminder(
            id=reminder_id,
            description=description,
            trigger_time=trigger_time,
            created_at=time.time(),
            reminder_type=reminder_type,
            repeat_interval=repeat_interval,
            notified=False
        )
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        print(f"[Reminders] Added {reminder_type}: '{description}' at {reminder.get_datetime_str()}")
        return reminder
    
    def add_reminder_from_natural_language(self, description: str, time_phrase: str) -> Optional[Reminder]:
        """
        Add reminder from natural language time phrase
        
        Examples:
            - "in 5 minutes"
            - "in 2 hours"
            - "tomorrow at 3pm"
            - "next monday at 10am"
            - "january 15 at 2:30pm"
        
        Returns:
            Reminder if successful, None if parsing failed
        """
        trigger_time = self._parse_natural_time(time_phrase)
        
        if trigger_time is None:
            print(f"[Reminders] Failed to parse time phrase: '{time_phrase}'")
            return None
        
        return self.add_reminder(description, trigger_time)
    
    def remove_reminder(self, reminder_id: str) -> bool:
        """Remove a reminder by ID"""
        for i, reminder in enumerate(self.reminders):
            if reminder.id == reminder_id:
                removed = self.reminders.pop(i)
                self._save_reminders()
                print(f"[Reminders] Removed: '{removed.description}'")
                return True
        return False
    
    def get_all_reminders(self) -> List[Reminder]:
        """Get all active reminders"""
        return [r for r in self.reminders if not r.notified]
    
    def get_upcoming_reminders(self, window_seconds: float = 3600) -> List[Reminder]:
        """Get reminders coming up within time window"""
        current_time = time.time()
        upcoming = [
            r for r in self.reminders 
            if not r.notified and r.is_upcoming(current_time, window_seconds)
        ]
        return sorted(upcoming, key=lambda r: r.trigger_time)
    
    def get_due_reminders(self) -> List[Reminder]:
        """Get all reminders that are currently due"""
        current_time = time.time()
        return [r for r in self.reminders if r.is_due(current_time)]
    
    # === TIME PARSING ===
    
    def _parse_natural_time(self, time_phrase: str) -> Optional[float]:
        """
        Parse natural language time phrases to Unix timestamp
        ...
        """
        time_phrase = time_phrase.lower().strip()
        now = datetime.now()
        
        # --- CORRECTION STARTS HERE ---
        # Map number words to digits for relative time parsing
        word_to_num = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            # Add more as needed, or use a library for full robustness
        }
        
        # Substitute number words in the time_phrase (e.g., "five minutes" -> "5 minutes")
        for word, num in word_to_num.items():
            # Check for pattern like "five minutes" or "in five minutes"
            time_phrase = re.sub(r'\b' + word + r'\b', num, time_phrase)
        # --- CORRECTION ENDS HERE ---

        # Pattern: "in X minutes/hours/days/weeks"
        relative_match = re.match(r'in (\d+)\s*(minute|hour|day|week)s?', time_phrase)
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)
            
            if unit == 'minute':
                delta = timedelta(minutes=amount)
            elif unit == 'hour':
                delta = timedelta(hours=amount)
            elif unit == 'day':
                delta = timedelta(days=amount)
            elif unit == 'week':
                delta = timedelta(weeks=amount)
            else:
                return None
            
            target = now + delta
            return target.timestamp()
        
        # Pattern: "tomorrow at Xpm/Xam"
        if 'tomorrow' in time_phrase:
            time_part = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', time_phrase)
            if time_part:
                hour = int(time_part.group(1))
                minute = int(time_part.group(2)) if time_part.group(2) else 0
                am_pm = time_part.group(3)
                
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                target = now + timedelta(days=1)
                target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return target.timestamp()
        
        # Pattern: "next monday/tuesday/etc at Xpm"
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if day in time_phrase:
                time_part = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)', time_phrase)
                if time_part:
                    hour = int(time_part.group(1))
                    minute = int(time_part.group(2)) if time_part.group(2) else 0
                    am_pm = time_part.group(3)
                    
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    # Find next occurrence of this weekday
                    days_ahead = (i - now.weekday() + 7) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # Next week if it's today
                    
                    target = now + timedelta(days=days_ahead)
                    target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    return target.timestamp()
        
        # Pattern: "in X seconds" (for testing)
        seconds_match = re.match(r'in (\d+)\s*seconds?', time_phrase)
        if seconds_match:
            seconds = int(seconds_match.group(1))
            target = now + timedelta(seconds=seconds)
            return target.timestamp()
        
        return None
    
    # === CONTEXT GENERATION FOR AI ===
    
    def check_and_get_context(self) -> Optional[str]:
        """
        Check for due reminders and return context string for AI
        
        Called periodically by tool orchestrator
        Returns context string if there are due or upcoming reminders
        """
        current_time = time.time()
        
        # Rate limit checks
        if current_time - self.last_check_time < self.check_interval:
            return None
        
        self.last_check_time = current_time
        
        # Get due reminders that haven't been announced yet
        due_reminders = [
            r for r in self.get_due_reminders()
            if r.id not in self.announced_reminder_ids
        ]
        
        if not due_reminders:
            return None
        
        # Mark as notified and handle repeats
        for reminder in due_reminders:
            self._handle_due_reminder(reminder)
            self.announced_reminder_ids.add(reminder.id)  # ADD THIS
        
        # Build context string
        context = self._build_notification_context(due_reminders)
        return context
    
    def get_upcoming_context(self) -> Optional[str]:
        """
        Get context about upcoming reminders (for proactive mentions)
        
        Returns context about reminders in next hour
        """
        upcoming = self.get_upcoming_reminders(window_seconds=3600)
        
        # Filter out already announced reminders
        upcoming = [
            r for r in upcoming 
            if r.id not in self.announced_reminder_ids
        ]
        
        if not upcoming:
            return None
        
        context_parts = ["📅 Upcoming reminders:"]
        
        for reminder in upcoming[:3]:  # Show top 3
            time_until = reminder.get_time_until(time.time())
            context_parts.append(
                f"- In {time_until}: {reminder.description}"
            )
        
        if len(upcoming) > 3:
            context_parts.append(f"... and {len(upcoming) - 3} more")
        
        return "\n".join(context_parts)
    
    def _build_notification_context(self, due_reminders: List[Reminder]) -> str:
        """Build context string for due reminders"""
        context_parts = ["🔔 **REMINDERS NOW DUE**"]
        context_parts.append(f"Current time: {datetime.now().strftime('%I:%M %p')}")
        context_parts.append("")
        
        for reminder in due_reminders:
            scheduled_time = reminder.get_datetime_str()
            icon = "[WARNING]️" if getattr(reminder, 'is_urgent', False) else "🔔"
            context_parts.append(f"{icon} {reminder.reminder_type.upper()}: {reminder.description}")
            context_parts.append(f"   Scheduled for: {scheduled_time}")
            context_parts.append("")
        
        context_parts.append("**YOU MUST NOTIFY THE USER ABOUT THESE IN YOUR RESPONSE!**")
        
        return "\n".join(context_parts)
    
    def _handle_due_reminder(self, reminder: Reminder):
        """Handle a due reminder (mark notified, handle repeats)"""
        # Handle repeating reminders
        if reminder.repeat_interval:
            # Schedule next occurrence
            reminder.trigger_time += reminder.repeat_interval
            reminder.notified = False
            print(f"[Reminders] Rescheduled repeating reminder: '{reminder.description}'")
        else:
            # Mark as notified (will be cleaned up later)
            reminder.notified = True
            print(f"[Reminders] Triggered: '{reminder.description}'")
        
        self._save_reminders()
    
    def _process_missed_reminders(self):
        """Process reminders that occurred while agent was offline"""
        current_time = time.time()
        missed = []
        
        for reminder in self.reminders:
            if reminder.trigger_time < current_time and not reminder.notified:
                missed.append(reminder)
        
        if missed:
            print(f"[Reminders] Found {len(missed)} missed reminders from offline period")
            
            # Add to pending notifications (will be shown on first interaction)
            self.pending_notifications.extend(missed)
            
            # Mark as handled
            for reminder in missed:
                self._handle_due_reminder(reminder)
    
    def get_missed_reminders_context(self) -> Optional[str]:
        """Get context for reminders that were missed while offline"""
        
        unannounced = [
            r for r in self.pending_notifications 
            if r.id not in self.announced_reminder_ids
        ]
        
        if not unannounced:
            return None
        
        context_parts = ["[WARNING]️ **URGENT: MISSED REMINDERS**"]
        context_parts.append("These reminders occurred while I was offline:")
        context_parts.append("")
        
        for reminder in unannounced:
            scheduled_time = reminder.get_datetime_str()
            overdue_seconds = time.time() - reminder.trigger_time
            
            # Calculate how overdue
            if overdue_seconds < 3600:
                overdue_str = f"{int(overdue_seconds / 60)} minutes ago"
            elif overdue_seconds < 86400:
                overdue_str = f"{int(overdue_seconds / 3600)} hours ago"
            else:
                overdue_str = f"{int(overdue_seconds / 86400)} days ago"
            
            context_parts.append(f"🔔 {reminder.description}")
            context_parts.append(f"   Was scheduled for: {scheduled_time} ({overdue_str})")
            context_parts.append("")
        
        context_parts.append("**YOU MUST NOTIFY THE USER ABOUT THESE IMMEDIATELY!**")
        
        # Mark these as announced
        for reminder in unannounced:
            self.announced_reminder_ids.add(reminder.id)
        
        return "\n".join(context_parts)

    def get_unannounced_due_count(self) -> int:
        """Get count of due reminders that haven't been announced yet"""
        due = self.get_due_reminders()
        unannounced = [r for r in due if r.id not in self.announced_reminder_ids]
        return len(unannounced)
    
    # === CLEANUP ===

    def cleanup_announced_reminders(self, older_than_seconds: int = 120) -> int:
        """
        Remove reminders that have been announced and are old enough
        
        Args:
            older_than_seconds: Only delete if reminder was due this long ago
            
        Returns:
            Number of reminders deleted
        """
        current_time = time.time()
        
        # Find reminders that are:
        # 1. Marked as notified
        # 2. Have been announced to user (in announced_reminder_ids)
        # 3. Are past due by at least older_than_seconds
        to_delete = [
            r for r in self.reminders
            if r.notified 
            and r.id in self.announced_reminder_ids
            and r.trigger_time <= (current_time - older_than_seconds)
            and not r.repeat_interval  # Don't delete repeating reminders
        ]
        
        deleted_count = 0
        for reminder in to_delete:
            # Remove from list
            self.reminders.remove(reminder)
            # Remove from announced tracking
            self.announced_reminder_ids.discard(reminder.id)
            deleted_count += 1
            print(f"[Reminders] Auto-deleted old reminder: '{reminder.description}'")
        
        if deleted_count > 0:
            self._save_reminders()
        
        return deleted_count
    
    def cleanup_old_reminders(self, days_old: int = 7):
        """Remove notified reminders older than specified days"""
        cutoff_time = time.time() - (days_old * 86400)
        
        original_count = len(self.reminders)
        self.reminders = [
            r for r in self.reminders
            if not (r.notified and r.trigger_time < cutoff_time)
        ]
        
        removed_count = original_count - len(self.reminders)
        
        if removed_count > 0:
            self._save_reminders()
            print(f"[Reminders] Cleaned up {removed_count} old reminders")
        
        return removed_count
    
    # === TOOL AVAILABILITY ===
    
    def is_available(self) -> bool:
        """Check if reminder tool is available"""
        return self.storage_file.parent.exists()
    
    def get_stats(self) -> Dict:
        """Get reminder statistics"""
        current_time = time.time()
        active = [r for r in self.reminders if not r.notified]
        due = self.get_due_reminders()
        upcoming = self.get_upcoming_reminders(3600)
        unannounced_due = self.get_unannounced_due_count()
        
        return {
            'total_reminders': len(self.reminders),
            'active_reminders': len(active),
            'due_reminders': len(due),
            'unannounced_due': unannounced_due,  # ADD THIS
            'upcoming_hour': len(upcoming),
            'pending_notifications': len(self.pending_notifications),
            'announced_count': len(self.announced_reminder_ids),  # ADD THIS
        }


# === NATURAL LANGUAGE COMMAND PARSER ===

class ReminderCommandParser:
    """
    Parse natural language commands to create/manage reminders
    Used by tool orchestrator to detect reminder requests
    """
    
    @staticmethod
    def parse_reminder_request(text: str) -> Optional[Dict]:
        """
        Parse text for reminder creation requests
        
        Returns dict with 'description' and 'time_phrase' or None
        """
        text_lower = text.lower().strip()
        
        # Pattern: "remind me to X in Y"
        match1 = re.search(r'remind me to (.+?) in (.+)', text_lower)
        if match1:
            return {
                'description': match1.group(1).strip(),
                'time_phrase': f"in {match1.group(2).strip()}"
            }
        
        # Pattern: "remind me to X tomorrow/monday/etc"
        match2 = re.search(r'remind me to (.+?) (tomorrow|next \w+) at (.+)', text_lower)
        if match2:
            return {
                'description': match2.group(1).strip(),
                'time_phrase': f"{match2.group(2)} at {match2.group(3).strip()}"
            }
        
        # Pattern: "set a timer for X minutes/hours"
        match3 = re.search(r'set (?:a |an )?timer for (\d+)\s*(minute|hour|second)s?', text_lower)
        if match3:
            amount = match3.group(1)
            unit = match3.group(2)
            return {
                'description': f"Timer ({amount} {unit}s)",
                'time_phrase': f"in {amount} {unit}s",
                'type': 'timer'
            }
        
        # Pattern: "remind me about X"
        match4 = re.search(r'remind me about (.+)', text_lower)
        if match4:
            # Need to extract time from the description
            desc = match4.group(1).strip()
            # Look for time phrase at the end
            time_match = re.search(r'(.+?)\s+(in .+|tomorrow.+|next .+)', desc)
            if time_match:
                return {
                    'description': time_match.group(1).strip(),
                    'time_phrase': time_match.group(2).strip()
                }
        
        return None
    
    @staticmethod
    def should_check_reminders(text: str) -> bool:
        """Check if user is asking about their reminders"""
        text_lower = text.lower()
        
        phrases = [
            'what reminders',
            'any reminders',
            'show reminders',
            'list reminders',
            'upcoming reminders',
            'do i have any reminders',
        ]
        
        return any(phrase in text_lower for phrase in phrases)