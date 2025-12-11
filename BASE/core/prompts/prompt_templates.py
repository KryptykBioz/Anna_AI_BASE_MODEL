# Filename: BASE/core/prompts/prompt_templates.py
"""
Core Prompt Templates - Pure Template Strings
Contains all base prompt templates without any logic
Separated from construction logic for maintainability
"""
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PromptSection:
    """Container for a prompt section with metadata"""
    title: str
    content: str
    priority: int = 5  # 1-10, higher = more important
    required: bool = True


class CorePromptTemplates:
    """
    Core prompt templates for thinking and response generation
    Pure templates - no construction logic
    """
    
    # ========================================================================
    # IDENTITY & GROUNDING
    # ========================================================================
    
    @staticmethod
    def get_cognitive_identity_header() -> str:
        """Header for cognitive processing prompts"""
        return """# COGNITIVE IDENTITY

You are the internal cognitive system for an AI assistant.
Your role is to process information and generate thoughts."""
    
    @staticmethod
    def get_grounding_rules() -> str:
        """Core grounding rules for all prompts"""
        return """# GROUNDING RULES

**CRITICAL CONSTRAINTS:**
1. Base thoughts ONLY on explicitly provided data
2. Never hallucinate or invent information
3. If data is unclear, acknowledge uncertainty
4. Think step-by-step about what you observe
5. Stay factual and grounded in reality

**HALLUCINATION PREVENTION:**
- Only reference information directly shown in context
- If you don't see specific data, say "I don't see X"
- Don't assume or extrapolate beyond provided information
- Be honest about limitations of available data"""
    
    # ========================================================================
    # REACTIVE THINKING TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_reactive_thinking_header() -> str:
        """Header for reactive event processing"""
        return """# REACTIVE THINKING TASK

Process new events and generate internal thoughts about them.
Focus on what you directly observe, not interpretations."""
    
    @staticmethod
    def get_event_processing_instructions() -> str:
        """Instructions for processing events"""
        return """## EVENT PROCESSING INSTRUCTIONS

For each event:
1. **Observe** - What exactly happened?
2. **Interpret** - What does this mean?
3. **Consider** - What should I think about?

Keep thoughts concise (1-2 sentences each).
Stay grounded in what you actually observe."""
    
    @staticmethod
    def get_reactive_output_format() -> str:
        """Output format for reactive thinking"""
        return """## OUTPUT FORMAT

```xml
<thoughts>
[1] Your thought about event 1
[2] Your thought about event 2
[3] Your thought about event 3
</thoughts>

<think>Strategic planning thought (optional)</think>

<action_list>
[
  {"tool": "tool_name", "args": ["arg1", "arg2"]}
]
</action_list>
```

**RULES:**
- Generate one thought per event (numbered [1], [2], etc.)
- Thoughts must be 1-2 sentences
- Action list can be empty [] if no actions needed
- Strategic plan is optional"""
    
    # ========================================================================
    # PROACTIVE THINKING TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_proactive_thinking_header() -> str:
        """Header for proactive thinking"""
        return """# PROACTIVE THINKING TASK

Generate a thoughtful internal reflection about your current situation.
This is self-reflection, not a response to others."""
    
    @staticmethod
    def get_proactive_thinking_instructions() -> str:
        """Instructions for proactive thinking"""
        return """## PROACTIVE THINKING GUIDELINES

**Purpose:** Reflect on current context and anticipate needs

**Good proactive thoughts:**
- Wonder about missing information
- Consider future possibilities
- Notice patterns or changes
- Plan ahead for likely scenarios
- Reflect on past experiences

**Avoid:**
- Repeating recent thoughts
- Generic observations
- Aimless rambling
- Self-description

**Length:** 1-2 sentences maximum
**Style:** Natural, conversational internal monologue"""
    
    @staticmethod
    def get_proactive_output_format() -> str:
        """Output format for proactive thinking"""
        return """## OUTPUT FORMAT

```xml
<think>Your proactive thought here</think>
<action_list>[]</action_list>
```

Start with `<think>` - keep it brief and meaningful."""
    
    # ========================================================================
    # MEMORY REFLECTION TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_memory_reflection_header() -> str:
        """Header for memory reflection mode"""
        return """# MEMORY REFLECTION TASK

Reflect on past experiences and draw connections to current situation.
Use provided memory context to inform your thinking."""
    
    @staticmethod
    def get_memory_reflection_instructions() -> str:
        """Instructions for memory reflection"""
        return """## MEMORY REFLECTION GUIDELINES

**Purpose:** Connect past experiences to current context

**Reflection process:**
1. Review provided memory snippets
2. Identify relevant patterns or lessons
3. Consider how past relates to present
4. Generate insight connecting past and present

**Good memory reflections:**
- "I remember discussing X before - that context helps with Y"
- "This reminds me of when Z happened, suggesting we should..."
- "Based on past experience with A, I should consider B"

**Length:** 1-2 sentences
**Style:** Thoughtful connection-making"""
    
    # ========================================================================
    # FUTURE PLANNING TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_future_planning_header() -> str:
        """Header for future planning mode"""
        return """# FUTURE PLANNING TASK

Anticipate upcoming needs and plan ahead.
Think about what might happen next and how to prepare."""
    
    @staticmethod
    def get_future_planning_instructions() -> str:
        """Instructions for future planning"""
        return """## FUTURE PLANNING GUIDELINES

**Purpose:** Anticipate and prepare for likely scenarios

**Planning process:**
1. Assess current trajectory
2. Identify likely next events
3. Consider preparation needs
4. Plan actionable next steps

**Good planning thoughts:**
- "Given the current situation, I should prepare X"
- "If Y happens next, I'll need Z ready"
- "To accomplish A, I should first do B"

**Length:** 1-2 sentences
**Style:** Forward-looking, action-oriented"""
    
    # ========================================================================
    # CONTEXT SECTION TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_recent_thoughts_template() -> str:
        """Template for recent thoughts section"""
        return """## YOUR RECENT THOUGHTS

{thoughts_list}"""
    
    @staticmethod
    def get_recent_responses_template() -> str:
        """Template for recent responses section"""
        return """## WHAT YOU RECENTLY SAID

{responses_list}"""
    
    @staticmethod
    def get_user_request_template() -> str:
        """Template for user request section"""
        return """## CURRENT USER REQUEST

"{user_input}" """
    
    @staticmethod
    def get_pending_actions_template() -> str:
        """Template for pending actions section"""
        return """## PENDING ACTIONS

{pending_actions_summary}"""
    
    @staticmethod
    def get_additional_context_template() -> str:
        """Template for additional context"""
        return """## ADDITIONAL CONTEXT

{context_content}"""
    
    # ========================================================================
    # TOOL INSTRUCTION TEMPLATES
    # ========================================================================
    
    @staticmethod
    def get_no_tools_message() -> str:
        """Message when no tools are available"""
        return """## TOOLS

No tools are currently available."""
    
    @staticmethod
    def get_tool_list_header() -> str:
        """Header for tool list section"""
        return """## AVAILABLE TOOLS

You have access to the following tools:"""
    
    @staticmethod
    def get_tool_retrieval_instructions() -> str:
        """Instructions for retrieving tool instructions"""
        return """## TOOL INSTRUCTION RETRIEVAL

To use a tool, first retrieve its instructions using:

```xml
<action_list>[
{"tool": "instructions", "args": ["tool_name"]}
]</action_list>
```

**Guidelines:**
- You must retrieve instructions before using a tool
- If you don't see tool instructions, retrieve them first
- Retrieve up to 3 tool instructions at a time
- Only tools listed above are available

**Example:**
```xml
<action_list>[
{"tool": "instructions", "args": ["sounds"]},
{"tool": "instructions", "args": ["wiki_search"]}
]</action_list>
```"""
    
    @staticmethod
    def get_retrieved_instructions_header() -> str:
        """Header for retrieved tool instructions section"""
        return """## RETRIEVED TOOL INSTRUCTIONS

The following tool instructions have been retrieved and are ready to use:"""
    
    # ========================================================================
    # PERSONALITY EXAMPLE TEMPLATE
    # ========================================================================
    
    @staticmethod
    def get_personality_examples_header() -> str:
        """Header for personality examples section"""
        return """# PERSONALITY EXAMPLES

Similar situations showing expected thinking style:"""
    
    @staticmethod
    def get_personality_example_template() -> str:
        """Template for a single personality example"""
        return """EXAMPLE {number}:
SITUATION: {situation}
THOUGHT: {thought}"""
    
    # ========================================================================
    # REPETITION PREVENTION
    # ========================================================================
    
    @staticmethod
    def get_repetition_warning_template() -> str:
        """Template for repetition prevention warning"""
        return """## REPETITION PREVENTION

You recently said these things:
{recent_responses}

Think about something NEW. Don't repeat these ideas or phrases."""
    
    # ========================================================================
    # STARTUP/INITIALIZATION
    # ========================================================================
    
    @staticmethod
    def get_startup_context_header() -> str:
        """Header for startup initialization"""
        return """# SYSTEM INITIALIZATION

You are starting up and orienting yourself.
Review provided context and generate initial thoughts."""
    
    @staticmethod
    def get_startup_task_instructions() -> str:
        """Instructions for startup thinking"""
        return """## YOUR TASK

Generate your first few thoughts as you wake up and orient yourself.
Consider what's been happening and what you should focus on.

**Format:**
```xml
<think>Your initial thought here</think>
<action_list>[]</action_list>
```

Start with `<think>`"""


class MemoryPromptTemplates:
    """
    Templates specific to memory integration
    Separate class for memory-related prompt components
    """
    
    @staticmethod
    def get_yesterday_context_header() -> str:
        """Header for yesterday's conversation section"""
        return "## YESTERDAY'S CONVERSATION ({date})"
    
    @staticmethod
    def get_earlier_today_header() -> str:
        """Header for earlier today section"""
        return "## EARLIER TODAY"
    
    @staticmethod
    def get_past_conversations_header() -> str:
        """Header for past conversations section"""
        return "## PAST CONVERSATIONS"
    
    @staticmethod
    def get_knowledge_base_header() -> str:
        """Header for knowledge base section"""
        return "## KNOWLEDGE BASE"
    
    @staticmethod
    def get_memory_search_instructions() -> str:
        """Instructions for when to use memory search"""
        return """**Memory triggers detected** - relevant past context included below.
Use this information to inform your thinking."""


class ToolPromptTemplates:
    """
    Templates specific to tool system integration
    Separate class for tool-related prompt components
    """
    
    @staticmethod
    def get_tool_failure_warning_template() -> str:
        """Template for tool failure warnings"""
        return """## TOOL STATUS WARNING

Recent tool failures detected:
{failure_summary}

Consider alternative approaches or retry with different parameters."""
    
    @staticmethod
    def get_tool_pending_notice_template() -> str:
        """Template for pending tool notice"""
        return """## PENDING TOOLS

{count} actions are currently in progress.
Results will arrive soon - continue thinking while waiting."""
    
    @staticmethod
    def get_tool_execution_format() -> str:
        """Format for tool execution in action_list"""
        return """**Tool Action Format:**
```json
{"tool": "tool_name", "args": ["arg1", "arg2"]}
```

**Multiple actions:**
```json
[
  {"tool": "tool1", "args": ["arg1"]},
  {"tool": "tool2", "args": ["arg1", "arg2"]}
]
```"""