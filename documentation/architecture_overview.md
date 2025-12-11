# System Architecture Overview

## Core Principle: Separation of Thought and Speech

This system maintains a **strict separation** between two independent pathways:

1. **Thought Processing** - Internal cognitive loop (continuous background)
2. **Response Generation** - External spoken output (triggered on demand)

```
┌─────────────────────────────────────────────────────────────┐
│                     AI CORE ORCHESTRATOR                     │
│                                                              │
│  ┌───────────────────────┐      ┌──────────────────────┐   │
│  │  THOUGHT PROCESSOR    │      │ RESPONSE GENERATOR   │   │
│  │  (Internal Cognition) │      │ (External Speech)    │   │
│  │                       │      │                      │   │
│  │  • Continuous loop    │      │  • On-demand only    │   │
│  │  • Processes events   │      │  • Reads thought     │   │
│  │  • Executes tools     │      │  • Synthesizes TTS   │   │
│  │  • Accumulates state  │      │  • Independent path  │   │
│  └───────────┬───────────┘      └──────────┬───────────┘   │
│              │                              │               │
│              │    ┌──────────────────┐     │               │
│              └───>│  THOUGHT BUFFER  │<────┘               │
│                   │  (Shared State)  │                     │
│                   │                  │                     │
│                   │  • Raw events    │                     │
│                   │  • Thoughts      │                     │
│                   │  • Priority tags │                     │
│                   │  • User context  │                     │
│                   └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## File Organization

### Core Cognitive Components

```
BASE/core/
├── thought_buffer.py          # Central state storage
├── thought_processor.py       # Cognitive orchestrator
├── generators/
│   ├── thought_generator.py   # LLM thought synthesis
│   └── response_generator.py  # LLM response synthesis
├── thinking_modes.py          # Specialized thought modes
└── cognitive_loop_manager.py  # Continuous thinking control
```

### Prompt Construction System

```
BASE/core/
├── constructors/
│   ├── prompt_assembler.py           # [NEW] Modular assembly
│   ├── section_builders.py           # [NEW] Section components
│   ├── thought_prompt_builder.py     # Thought prompt API
│   └── response_prompt_constructor.py # Response prompt API
└── prompts/
    ├── prompt_templates.py      # [NEW] Pure template strings
    ├── thought_prompt_parts.py  # Thought text components
    ├── response_prompt_parts.py # Response text components
    └── shared_prompt_segments.py # Shared components
```

## Key Design Decisions

### 1. Thought Buffer as Single Source of Truth

**thought_buffer.py** is the **only place** that stores cognitive state:

```python
class ThoughtBuffer:
    """
    Centralized state storage.
    Both processors read from here, only thought processor writes.
    """
    _raw_events: Deque[RawDataEvent]      # Unprocessed observations
    _thoughts: Deque[ProcessedThought]     # Interpreted cognitions
    last_user_input: str                   # Current user context
    ongoing_context: str                   # Current focus
    current_goal: Optional[Dict]           # Active goal
```

**Access Pattern:**
- **Thought Processor**: Read + Write (processes events → adds thoughts)
- **Response Generator**: Read Only (reads accumulated thoughts → generates speech)

### 2. Priority System Uses String Tags

No more magic numbers. All priorities are clear string constants:

```python
class Priority:
    LOW = "[LOW]"
    MEDIUM = "[MEDIUM]"
    HIGH = "[HIGH]"
    CRITICAL = "[CRITICAL]"
```

**Benefits:**
- Self-documenting code (`Priority.HIGH` vs `8`)
- IDE autocomplete support
- Easy to extend without breaking changes
- Numeric conversion only for internal comparisons

### 3. Prompt Construction is Modular

**Old Way (Monolithic):**
```python
# Everything in one massive function
def build_prompt(events, thoughts, tools, memory, ...):
    prompt = "# HUGE PROMPT\n"
    prompt += "..."  # 200+ lines
    return prompt
```

**New Way (Modular):**
```python
# Assemble from independent sections
sections = [
    identity_builder.build_cognitive_identity(agentname),
    context_builder.build_recent_thoughts(thoughts),
    tool_builder.build_tool_section(),
    memory_builder.build_memory_context(query),
]

prompt = assembler.assemble_prompt(sections)
```

**Architecture:**
```
PromptAssembler (orchestration)
    ├── IdentitySectionBuilder
    ├── ContextSectionBuilder
    ├── EventSectionBuilder
    ├── PersonalitySectionBuilder
    ├── MemorySectionBuilder
    ├── ToolSectionBuilder
    └── RepetitionSectionBuilder
```

Each builder is **responsible for one type of section** and can be modified independently.

### 4. Templates Separate from Logic

**prompt_templates.py** contains **only pure template strings**:

```python
class CorePromptTemplates:
    @staticmethod
    def get_reactive_thinking_header() -> str:
        return """# REACTIVE THINKING TASK
Process new events and generate thoughts."""
    
    @staticmethod
    def get_user_request_template() -> str:
        return """## CURRENT USER REQUEST
"{user_input}" """
```

**No logic, no construction, just text.**

Construction logic lives in **section_builders.py**:

```python
class ContextSectionBuilder:
    def build_user_request_section(self, user_input: str) -> PromptSection:
        if not user_input.strip():
            return None  # Logic here
        
        content = self.templates.get_user_request_template().format(
            user_input=user_input
        )
        
        return PromptSection(
            title="User Request",
            content=content,
            priority=10,
            required=False
        )
```

### 5. Independent Response Pathway

**Response Generator never triggers thought processing:**

```python
async def generate_response(self, user_text, context_parts):
    """
    INDEPENDENT PATHWAY:
    - Reads thought buffer (read-only)
    - Builds memory context
    - Synthesizes spoken output
    - Does NOT process thoughts
    - Does NOT modify thought state
    """
    # Build memory context
    memory_context = self._build_memory_context_for_response(
        user_text, context_parts
    )
    
    # Build prompt from accumulated state
    prompt = self.prompt_constructor.build_response_prompt_simple(
        user_text=user_text,
        context_parts=[memory_context] + context_parts,
        chat_context=self._extract_chat_context(context_parts)
    )
    
    # Generate speech (independent LLM call)
    response = self._call_ollama(prompt, model=self.config.text_model)
    
    # Post-process and return
    return await self._apply_post_processing(response)
```

**No coupling to thought processor.**

## Data Flow

### Event Processing (Reactive)

```
1. External Event
        ↓
2. thought_buffer.ingest_raw_data()  [Queued]
        ↓
3. thought_processor.process_thoughts()
        ↓
4. thought_generator.batch_interpret_events()  [LLM call]
        ↓
5. thought_buffer.add_processed_thought()  [With priority tag]
        ↓
6. [State accumulated in buffer]
```

### Response Generation (On-Demand)

```
1. User wants response OR autonomous trigger
        ↓
2. response_generator.generate_response()
        ↓
3. Read thought_buffer state [Read-only]
        ↓
4. Build memory context
        ↓
5. response_prompt_constructor.build_prompt()
        ↓
6. LLM call (independent from thought processing)
        ↓
7. Post-process (emoji removal, game commands)
        ↓
8. Return spoken text
        ↓
9. thought_buffer.add_response_echo()  [Optional]
```

### Continuous Thinking Loop

```
┌─────────────────────────────────────┐
│   Cognitive Loop (Background)       │
│                                     │
│   while True:                       │
│       if has_unprocessed_events:    │
│           process_reactive()        │
│       elif should_think_proactive:  │
│           generate_proactive()      │
│       else:                         │
│           sleep(interval)           │
└─────────────────────────────────────┘
```

**Key:** Loop runs **independently** of responses. Agent thinks continuously even when not speaking.

## Component Responsibilities

### thought_buffer.py
- Store raw events and processed thoughts
- Track user context and priorities
- Determine when to speak (decision logic)
- Provide formatted context for prompts
- [FAILED] Does NOT generate thoughts or responses

### thought_processor.py
- Orchestrate cognitive processing
- Call thought_generator for LLM synthesis
- Execute tool actions
- Manage proactive thinking
- [FAILED] Does NOT generate responses

### response_generator.py
- Generate spoken TTS output
- Integrate memory context
- Post-process responses
- [FAILED] Does NOT process thoughts
- [FAILED] Does NOT trigger thought processing
- [FAILED] Does NOT manage thought state

### prompt_assembler.py (NEW)
- Orchestrate section assembly
- Handle section ordering and filtering
- Provide high-level composition API
- [FAILED] Does NOT contain template text
- [FAILED] Does NOT contain construction logic

### section_builders.py (NEW)
- Build individual prompt sections
- Contain section construction logic
- Use templates from prompt_templates.py
- [FAILED] Does NOT contain template text
- [FAILED] Does NOT orchestrate full prompts

### prompt_templates.py (NEW)
- Contain pure template strings
- Provide formatting placeholders
- [FAILED] Does NOT contain logic
- [FAILED] Does NOT do construction

## Benefits of This Architecture

### 1. Clear Separation
- Thought processing and response generation are independent
- Can modify one without affecting the other
- Easier to test and debug

### 2. Modular Prompts
- Add new sections without touching existing code
- Reorder sections by changing priority
- Share sections across different prompt types

### 3. Maintainability
- Template text separate from logic
- Single responsibility for each component
- Easy to find and update specific parts

### 4. Flexibility
- Can swap out section builders
- Can add new prompt types easily
- Priority system extensible without breaking changes

### 5. Performance
- Response generation doesn't block thought processing
- Thought processing runs continuously
- Clear boundaries prevent unnecessary coupling