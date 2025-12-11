# Priority System Documentation

## Overview

The agent uses a **string-based priority system** with four clear levels. This replaces the previous numeric urgency system (1-10) with descriptive tags for better code clarity.

## Priority Levels

| Priority | Tag | Numeric (Internal) | Use Case |
|----------|-----|-------------------|----------|
| **Critical** | `[CRITICAL]` | 10 | Urgent reminders, direct bot mentions |
| **High** | `[HIGH]` | 8 | User input, direct questions, tool failures |
| **Medium** | `[MEDIUM]` | 5 | Chat messages, tool results, observations |
| **Low** | `[LOW]` | 1 | Ambient events, response echoes, background activity |

## Implementation

### String Tags (External API)

All public APIs use string tags for clarity:

```python
from BASE.core.thought_buffer import Priority

# Adding thoughts with priority
thought_buffer.add_processed_thought(
    content="User asked a question",
    source="user_input",
    priority_override=Priority.HIGH  # Uses [HIGH] tag
)

# Checking priority
max_priority = thought_buffer.get_highest_priority()
if max_priority == Priority.CRITICAL:
    # Handle urgent case
    pass
```

### Numeric Conversion (Internal Only)

Numeric values are used **only for internal comparisons**:

```python
# Internal comparison logic
priority_value = Priority.to_numeric("[HIGH]")  # Returns 8

if priority_value >= Priority.to_numeric("[MEDIUM]"):
    # Process medium+ priority thoughts
    pass
```

## Priority Assignment

### Automatic (from source)

Most thoughts get priority automatically based on their source:

```python
# Automatically assigned priorities
Priority.from_source("user_input")          # → [HIGH]
Priority.from_source("chat_direct_mention") # → [CRITICAL]
Priority.from_source("tool_result")         # → [MEDIUM]
Priority.from_source("proactive_reflection")# → [LOW]
```

### Manual Override

Can override automatic assignment when needed:

```python
# Override for special cases
thought_buffer.add_processed_thought(
    content="Emergency system alert",
    source="system_event",
    priority_override=Priority.CRITICAL  # Force critical
)
```

## Response Decision Logic

Priority influences when the agent speaks:

| Condition | Min Priority | Reason |
|-----------|-------------|--------|
| Has `[CRITICAL]` thoughts | N/A | Speak immediately |
| Has `[HIGH]` thoughts | N/A | Speak for direct address |
| 3+ unspoken thoughts | `[MEDIUM]` | Accumulated observations |
| 5+ unspoken + 30s | `[LOW]` | Natural conversation |
| 8+ unspoken + 15s | `[LOW]` | Many observations |

## Migration from Numeric System

### Old Code (Numeric)
```python
# DON'T USE ANYMORE
urgency_level = 8
if urgency_level >= 7:
    respond_urgently()
```

### New Code (String Tags)
```python
# USE THIS INSTEAD
priority = Priority.HIGH
if Priority.to_numeric(priority) >= Priority.to_numeric(Priority.HIGH):
    respond_urgently()
```

## Best Practices

### DO

- Use string constants from `Priority` class
- Let automatic assignment handle most cases
- Override only for special circumstances
- Compare priorities using `Priority.to_numeric()`

### [FAILED] DON'T

- Use raw numeric values (1-10)
- Use custom string tags not in `Priority` class
- Expose numeric values in public APIs
- Hardcode numeric comparisons

## Examples

### Example 1: Processing User Input
```python
# User input automatically gets [HIGH] priority
thought_buffer.add_processed_thought(
    content=f"{username} said: {user_text}",
    source="user_input"  # Auto-assigns [HIGH]
)

# Check if should respond
should_speak, reason, priority = thought_buffer.should_speak()
if priority == Priority.HIGH:
    # Generate response for user
    pass
```

### Example 2: Chat Urgency Detection
```python
def detect_chat_priority(message: str) -> str:
    """Detect priority for chat message."""
    if agentname.lower() in message.lower():
        return Priority.CRITICAL  # Direct mention
    elif '?' in message:
        return Priority.HIGH      # Question
    elif '!' in message:
        return Priority.MEDIUM    # Exclamation
    else:
        return Priority.LOW       # General chat
```

### Example 3: Response Filtering
```python
# Get only high-priority thoughts for urgent response
high_priority_thoughts = thought_buffer.get_thoughts_for_response(
    min_priority=Priority.HIGH,
    only_unspoken=True
)

# Or get all medium+ priority thoughts
medium_plus_thoughts = thought_buffer.get_thoughts_for_response(
    min_priority=Priority.MEDIUM
)
```

## Architecture Benefits

### Clear Intent
- `Priority.CRITICAL` is more readable than `10`
- Easier to understand priority decisions in logs
- Self-documenting code

### Flexibility
- Can change numeric mappings without touching business logic
- Easy to add new priority levels if needed
- Internal comparisons still efficient

### Type Safety
- IDE autocomplete for priority constants
- Reduces typos and magic numbers
- Clear API contracts

## Source Priority Mapping

Complete mapping of sources to automatic priorities:

```python
PRIORITY_MAP = {
    # Critical (10)
    'urgent_reminder': Priority.CRITICAL,
    'direct_mention': Priority.CRITICAL,
    'chat_direct_mention': Priority.CRITICAL,
    
    # High (8)
    'user_input': Priority.HIGH,
    'chat_question': Priority.HIGH,
    'tool_timeout': Priority.HIGH,
    'tool_failed': Priority.HIGH,
    'tool_enforcement': Priority.HIGH,
    'tool_disabled': Priority.HIGH,
    'tool_error': Priority.HIGH,
    
    # Medium (5)
    'chat_message': Priority.MEDIUM,
    'vision_result': Priority.MEDIUM,
    'search_result': Priority.MEDIUM,
    'memory_result': Priority.MEDIUM,
    'tool_initiated': Priority.MEDIUM,
    'tool_result': Priority.MEDIUM,
    'tool_instructions': Priority.MEDIUM,
    'chat_engagement': Priority.MEDIUM,
    
    # Low (1)
    'tool_pending': Priority.LOW,
    'observation': Priority.LOW,
    'internal': Priority.LOW,
    'proactive_reflection': Priority.LOW,
    'ambient': Priority.LOW,
    'response_echo': Priority.LOW,
}
```