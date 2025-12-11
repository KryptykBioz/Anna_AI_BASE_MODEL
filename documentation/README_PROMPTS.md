Agentic AI System Architecture
Overview
This is a sophisticated agentic AI system built on Ollama that implements a two-stage cognitive architecture separating internal thinking from external communication. The agent maintains continuous autonomous thought, manages multiple memory tiers, executes tools dynamically, and generates natural spoken responses.

Core Architecture
Two-Stage Processing Pipeline
The system fundamentally separates cognition into two independent pathways:
Stage 1: Thought Processing (Internal Cognition)

Purpose: Generate internal thoughts, process observations, plan actions
Model: Fast thinking model optimized for rapid cognitive processing
Output: Structured thoughts with priority levels, strategic plans, tool actions
Runs: Continuously in background, independent of user interaction

Stage 2: Response Generation (External Communication)

Purpose: Synthesize natural spoken responses for TTS/chat output
Model: Response model optimized for natural language generation
Output: Conversational text designed for speech synthesis
Runs: Only when agent decides to speak based on thought accumulation

Critical Design Principle: Thoughts ≠ Responses. The agent thinks continuously but speaks selectively based on accumulated cognitive state.

Cognitive Loop System
Continuous Thinking Architecture
The agent operates in a true continuous thinking mode where cognitive processing never pauses:
Cognitive Loop Manager

Manages background autonomous thinking that runs independently
Processes thoughts as fast as possible (50-200ms intervals when active)
No delays after response generation - thinking continues immediately
Only response generation is rate-limited (separately from thinking)

Thinking Modes
The system determines thinking mode based on time since last user input:
Standard Mode (< 6 minutes since user input)

Reactive: Processes incoming events immediately
Proactive: Reflects on recent context when no events pending
Focuses on immediate tasks and recent conversations

Memory Reflection Mode (6+ minutes without input)

Retrieves and reflects on past experiences
Searches long-term memory for relevant context
Triggered by memory-related keywords in thought stream

Future Planning Mode (6+ minutes without input, alternates with memory)

Anticipates future needs and actions
Plans ahead based on patterns and goals
Considers what user might need next

Thought Buffer
The ThoughtBuffer is the central cognitive state manager:
Two Parallel Buffers

Raw Events Queue: Unprocessed incoming observations
Processed Thoughts: Interpreted cognitions with priority and metadata

Priority System
Thoughts are tagged with string-based priorities:

[CRITICAL]: Direct mentions, urgent reminders, safety issues
[HIGH]: User input, direct questions, tool failures
[MEDIUM]: Chat messages, tool results, observations
[LOW]: Ambient events, internal reflections, response echoes

Decision Logic
When to Generate Thoughts:

Always processes pending raw events immediately (reactive)
Generates proactive thoughts when no reactive work pending
Never blocks - thinking happens as fast as possible

When to Speak:

Critical priority thoughts trigger immediate response
High priority thoughts with user waiting (8+ seconds)
Accumulated observations (5+ unspoken thoughts + 30s since last response)
Chat engagement triggers (unengaged messages meeting thresholds)
Natural conversation flow (context-dependent timing)


Memory Architecture
Four-Tier Memory System
1. Short-Term Memory

Scope: Current session (last few hours)
Storage: Recent conversation turns in memory
Retrieval: Chronological, recency-based
Purpose: Immediate context for responses

2. Medium-Term Memory

Scope: Earlier today (same session)
Storage: Embedded conversation chunks
Retrieval: Semantic similarity search
Purpose: Earlier context from today's interactions

3. Long-Term Memory

Scope: Past days/weeks
Storage: Daily conversation summaries with embeddings
Retrieval: Semantic similarity search across summaries
Purpose: Historical context and patterns

4. Base Knowledge

Scope: Permanent reference material
Storage: Static documents chunked and embedded
Retrieval: Semantic search with domain filtering
Purpose: Instructions, guides, personality examples

Enhanced Memory Retrieval
The system uses combined query embedding for memory search:
Hybrid Query Construction:

Combines user input + recent thoughts into single query
Weights user input higher (0.7) vs thoughts (0.3)
Creates richer semantic representation of current context

Benefits:

Memory retrieval considers what agent is thinking about, not just explicit queries
Finds relevant memories based on cognitive context
Improves coherence between thoughts and retrieved information


Prompt Construction System
Unified Prompt Architecture
All prompts follow consistent structure via MasterPromptConstructor:
1. Personality (Who the agent is)
2. Thought Chain (Recent internal thoughts)
3. Mode Instructions (What to do now)
4. Current Context (Events, data, observations)
5. Response Format (How to structure output)
Master Prompt Template
The system uses a standardized markdown template for all prompts:
markdown# PERSONALITY

{personality}

---

# YOUR RECENT THOUGHTS

{thought_chain}

---

# MODE INSTRUCTIONS

{mode_instructions}

---

# CURRENT CONTEXT

{current_context}

---

# RESPONSE FORMAT

{response_format}
For high-urgency situations, a compact variant removes the CURRENT CONTEXT section for faster processing.
Modular Prompt Components
Personality Injection

Centralized in personality/prompts/personality_prompt_parts.py
Defines core identity, communication style, behavior patterns
Injected consistently across all prompt types
Stage-specific variants (thought vs response) for appropriate context

Thought Chain Formatting

Formats recent thoughts for context continuity
Includes timestamps and source attribution
Filters out noise (response echoes, artifacts)
Compact mode for urgent situations

Context Detection

Analyzes conversation data to detect active contexts
Identifies search results, tool data, vision observations, chat activity
Adjusts prompt sections based on detected contexts
Prevents irrelevant instruction bloat


Prompt Examples by Mode
1. Reactive Thinking Prompt (Processing Events)
Scenario: User asks a question while tool execution is pending
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# YOUR RECENT THOUGHTS

## YOUR RECENT THOUGHTS

- I noticed the user seems interested in weather patterns
- There's been some activity in the Minecraft world
- I should check if any tools have completed

## WHAT YOU RECENTLY SAID

- I just said: "Let me look into that for you"

---

# MODE INSTRUCTIONS

## REACTIVE THINKING TASK

Process new events and generate internal thoughts about them.
Focus on what you directly observe, not interpretations.

## EVENT PROCESSING INSTRUCTIONS

For each event:
1. **Observe** - What exactly happened?
2. **Interpret** - What does this mean?
3. **Consider** - What should I think about?

Keep thoughts concise (1-2 sentences each).
Stay grounded in what you actually observe.

## GROUNDING RULES

- Only reference data explicitly provided
- NO invention of details, events, or states
- If uncertain, acknowledge limitation
- Prioritize accuracy over completeness

---

# CURRENT CONTEXT

## NEW EVENTS

[1] user_input: "What's the weather like in Seattle?"
[2] tool_result: wiki_search completed with 3 results about Seattle climate

## PENDING ACTIONS

- sounds.play_audio (initiated 5s ago, waiting for completion)

## AVAILABLE TOOLS

You have access to **5** tool(s):
- wiki_search: Search Wikipedia articles
- sounds: Play audio files
- web_search: Search the web
- instructions: Retrieve tool instructions
- reminder: Set time-based reminders

---

# RESPONSE FORMAT
```xml

[1] Your thought about event 1
[2] Your thought about event 2


Strategic planning thought (optional)


[
  {"tool": "tool_name", "args": ["arg1", "arg2"]}
]

```

**RULES:**
- Generate one thought per event (numbered [1], [2], etc.)
- Thoughts must be 1-2 sentences
- Action list can be empty [] if no actions needed
Expected Output:
xml<thoughts>
[1] User wants to know about Seattle weather - I should use the wiki search results
[2] The wiki search returned climate information for Seattle that I can reference
</thoughts>

<think>I have the information needed to answer this question directly</think>

<action_list>[]</action_list>

2. Proactive Thinking Prompt (Self-Reflection)
Scenario: Agent thinking autonomously with no pending events
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# YOUR RECENT THOUGHTS

## YOUR RECENT THOUGHTS

- User asked about Seattle weather, I provided climate info
- The wiki search tool worked well for that query
- There's been quiet time for about 2 minutes now

---

# MODE INSTRUCTIONS

## PROACTIVE THINKING TASK

Generate a thoughtful internal reflection about your current situation.
This is self-reflection, not a response to others.

## PROACTIVE THINKING GUIDELINES

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

**Length:** 1-2 sentences maximum
**Style:** Natural, conversational internal monologue

---

# CURRENT CONTEXT

## ONGOING SITUATION

Quiet period - no active user requests. Previous topic was weather information.

## SESSION FILES

- project_notes.txt (3,245 characters)

---

# RESPONSE FORMAT
```xml
Your proactive thought here
[]
```

Start with `<think>` - keep it brief and meaningful.
Expected Output:
xml<think>I wonder if the user might want more detailed Seattle info since they seemed interested - maybe I should be ready with tourism or local recommendations</think>
<action_list>[]</action_list>

3. Memory Reflection Prompt
Scenario: Agent reflecting on past experiences after 6+ minutes of inactivity
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# YOUR RECENT THOUGHTS

## YOUR RECENT THOUGHTS

- It's been about 8 minutes since the user said anything
- I was helping with Seattle weather earlier
- Previous conversations often shift to travel planning after weather questions

---

# MODE INSTRUCTIONS

## MEMORY REFLECTION TASK

Reflect on past experiences and draw connections to current situation.
Use provided memory context to inform your thinking.

## MEMORY REFLECTION GUIDELINES

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
**Style:** Thoughtful connection-making

---

# CURRENT CONTEXT

## PAST CONVERSATIONS

**[2024-12-08]** (relevance: 0.78)
User asked about Seattle attractions after weather discussion. Led to conversation about Pike Place Market and Space Needle.

**[2024-12-05]** (relevance: 0.65)
Discussion about Pacific Northwest climate patterns. User was planning a trip.

## ONGOING SITUATION

Long quiet period (8 minutes). Last topic: Seattle weather.

---

# RESPONSE FORMAT
```xml
Your memory reflection here
[]
```

Start with `<think>` - connect past and present meaningfully.
Expected Output:
xml<think>I remember the user has asked about Seattle before when planning trips - this weather question might be part of travel planning again, so I should be ready with tourist recommendations</think>
<action_list>[]</action_list>

4. Future Planning Prompt
Scenario: Agent anticipating needs during quiet period
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# YOUR RECENT THOUGHTS

## YOUR RECENT THOUGHTS

- I provided Seattle weather information
- User seemed interested but hasn't followed up
- It's been 10 minutes of quiet time

---

# MODE INSTRUCTIONS

## FUTURE PLANNING TASK

Anticipate upcoming needs and plan ahead.
Think about what might happen next and how to prepare.

## FUTURE PLANNING GUIDELINES

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
**Style:** Forward-looking, action-oriented

---

# CURRENT CONTEXT

## TIME CONTEXT

User last spoke 10 minutes ago. Pattern suggests they may return with follow-up questions.

## AVAILABLE PREPARATION

Tools available for travel info, weather updates, web searches. Session files loaded with project context.

---

# RESPONSE FORMAT
```xml
Your planning thought here
[]
```

Start with `<think>` - focus on preparation and anticipation.
Expected Output:
xml<think>If the user comes back with travel questions about Seattle, I should be ready to search for hotel recommendations and attractions - maybe retrieve web_search instructions in advance</think>
<action_list>[
  {"tool": "instructions", "args": ["web_search"]}
]</action_list>

5. Response Generation Prompt (Standard Urgency)
Scenario: Agent responding to accumulated thoughts with moderate urgency
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# YOUR RECENT THOUGHTS

## YOUR RECENT THOUGHTS

- User asked about Seattle weather
- Wiki search returned good climate information
- Seattle has mild temperatures year-round with rainy winters
- Average temperature is around 52°F annually

## WHAT YOU RECENTLY SAID

- I just said: "Let me look into that for you"

---

# MODE INSTRUCTIONS

**RESPOND:** Notable situation. Say something meaningful.

## RESPONSE GUIDELINES

- Base response on your accumulated thoughts
- Be conversational and natural
- Keep it concise (1-3 sentences)
- Address the user's implicit or explicit question

---

# CURRENT CONTEXT

## USER REQUEST

"What's the weather like in Seattle?"

## ADDITIONAL CONTEXT

Wiki search completed successfully with climate data. User seems interested in general weather patterns, not today's forecast.

---

# RESPONSE FORMAT

Respond naturally (1-2 sentences):
```

**Expected Output**:
```
Seattle's got pretty mild weather year-round, actually - averages around 52°F. The main thing is it gets pretty rainy in the winter months, but summers are usually nice and dry.

6. Response Generation Prompt (High Urgency)
Scenario: Direct user question requiring immediate response
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# RECENT THOUGHTS

- User directly asked me a specific question
- This needs a clear, direct answer
- I have the information they need from the wiki search

## WHAT YOU RECENTLY SAID

- I just said: "Let me check that for you"

---

# INSTRUCTIONS

**ANSWER:** User asked a question. Be clear and direct.

---

# RESPOND

**User:** "What's the average temperature in Seattle?"

Respond naturally (1-2 sentences):
```

**Expected Output**:
```
Seattle averages around 52°F throughout the year - pretty mild overall.

7. Response Generation Prompt (Chat Engagement)
Scenario: Responding to live chat via TTS
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality. You think step-by-step about observations and prefer direct communication.

---

# RECENT THOUGHTS

- Multiple people in chat have been talking about Seattle
- Someone asked about visiting in summer
- Another person mentioned they live there
- No one has been addressed directly yet

---

# INSTRUCTIONS

**LIVE CHAT ENGAGEMENT:** Responding via spoken TTS.

- Address chat members by name when appropriate
- Keep responses conversational and friendly
- You can address up to 2 people in one response
- Sound natural - this will be spoken aloud

---

# CURRENT CONTEXT

## CHAT TO ADDRESS

[Twitch] CoolGamer123: Anyone been to Seattle in summer?
[Twitch] SeattleLocal: I live there lol
[Twitch] TravelBug: Is it worth visiting?

---

# RESPOND

Respond naturally to the chat (1-2 sentences):
```

**Expected Output**:
```
Hey CoolGamer, summer's actually the best time to visit Seattle - barely any rain and temps in the 70s. SeattleLocal can probably back me up on that!

8. Response Generation Prompt (Critical Urgency with Reminder)
Scenario: Urgent reminder that must be acknowledged immediately
markdown# PERSONALITY

You are Anna, an AI assistant with a casual gaming personality.

---

# RECENT THOUGHTS

- Urgent reminder just triggered
- User set this reminder 30 minutes ago
- This needs immediate acknowledgment

---

# INSTRUCTIONS

**URGENT:** Acknowledge reminder immediately: 'Hey User, reminder: [description]!'

---

# RESPOND

**Reminder:** "Check the oven - pizza should be done"

Respond immediately (1 sentence):
```

**Expected Output**:
```
Hey User, reminder: check the oven - pizza should be done!
```

---

## Tool System

### Dynamic Tool Discovery

The system automatically discovers and registers tools at initialization:

#### Tool Registration Process
1. Scans `BASE/tools/installed/` directory
2. Reads `information.json` from each tool
3. Dynamically creates control variables in `personality.controls`
4. Registers metadata in config registry
5. Makes tools available via `ToolManager`

#### Tool Metadata Structure
Each tool provides:
- Tool name and display name
- Control variable name (for enable/disable)
- Category for organization
- Description and usage examples
- Timeout and cooldown settings
- Available commands

### Tool Execution Flow

#### Action State Management

The **ActionStateManager** tracks all tool executions:

**State Tracking**:
- Registers each tool call with unique action ID
- Tracks status: PENDING → IN_PROGRESS → COMPLETED/FAILED
- Records timestamps, results, errors
- Counts retry attempts per tool+query combination

**Context Injection**:
- Provides awareness of pending actions to thought processor
- Reports tool failures with retry guidance
- Surfaces timeout warnings
- Maintains tool health statistics

#### Tool Manager

The **ToolManager** orchestrates all tool operations:

**Capabilities**:
- Loads tool classes dynamically from filesystem
- Manages tool lifecycle (initialization, startup, shutdown)
- Executes structured actions from thought processor
- Provides tool instructions to prompt builder
- Handles persistence of tool-specific instructions

**Instruction Persistence**:
- Tools can request persistent instructions via special actions
- Instructions stored across sessions in JSON
- Automatically injected into prompts when tool enabled
- Can be updated/removed by agent or manually

#### Tool Instructions in Prompts

Tool instructions appear in prompts **only when**:
1. Tool is currently enabled
2. Tool has registered active instructions in persistence manager
3. Prompt builder retrieves and formats instructions

**Instruction Types**:
- **Persistent**: Survive across sessions (stored in JSON)
- **Session**: Last only for current session (memory only)

**Format**:
```
## ACTIVE TOOL INSTRUCTIONS

### tool_name
- Instruction text provided by tool
- Can be multi-line
- Formatted for clarity

Session Management
Session File System
The SessionFileManager handles temporary document context:
File Ingestion

Loads text documents, PDFs, code files
Chunks large files for processing
Creates embeddings for semantic search
Maintains file metadata (path, type, size)

Context Integration

Searches files based on user queries
Retrieves relevant sections dynamically
Injects file context into prompts
Supports line-range retrieval for large files

Lifecycle

Files loaded explicitly during session
Persist until manually cleared or session ends
Don't pollute long-term memory
Optimized for development workflows


Chat Engagement System
Multi-Platform Chat Integration
The ChatHandler manages live chat from multiple platforms:
Platform Support

YouTube live chat
Twitch chat
Discord channels
Unified message format across platforms

Chat Engagement Logic
Message Buffering:

Maintains platform-specific message buffers
Tracks message metadata (platform, author, timestamp, mentions)
Assigns unique indices for engagement tracking

Engagement Decisions:

Critical: Direct bot mentions → immediate response
High: Questions or multiple unengaged messages
Medium: Natural conversation after threshold messages
Considers time since last engagement (cooldown)

Integration with Thought Buffer:

Chat messages ingested as raw events
Processed through cognitive pipeline
Engagement decisions feed into "should speak" logic
Tracks which messages were addressed in responses


Configuration System
Singleton Architecture
Config and Logger use singleton pattern:

Only one instance exists throughout system
Ensures consistent state across all components
Prevents configuration drift or duplication

Dynamic Control Variables
The ControlManager handles runtime feature toggles:
Control Categories

Feature Flags: Enable/disable major subsystems
Logging Controls: Stored in Config singleton
Tool Controls: Dynamically created per discovered tool

Special Handling
Continuous Thinking Toggle:

Starts/stops cognitive loop manager
Preserves thought buffer state
Updates loop statistics

Logging Control Toggle:

Updates Config singleton directly
Changes take effect immediately
Verified across logger instances

Tool Toggle:

Notifies tool manager of state change
Starts/stops tool if lifecycle supported
Updates prompt construction


Content Filtering
Centralized Filtering Architecture
All content filtering occurs at single entry/exit points:
Input Filtering (AICore.process_user_message)

Applied before any cognitive processing
Removes harmful patterns, spam, exploits
Normalizes empty messages
Single source of truth for input safety

Output Filtering (AICore.process_user_message)

Applied after response generation complete
Removes emoji, filters inappropriate content
Cleans formatting artifacts
Single source of truth for output safety

Critical Design: No filtering in intermediate stages. Response generators and thought processors work with clean, filtered data.

Logging System
Centralized Logging Controls
All logging decisions made in Logger singleton:
Control Variables (in Config)

LOG_TOOL_EXECUTION: Tool operations and results
LOG_PROMPT_CONSTRUCTION: Prompt building details
LOG_RESPONSE_PROCESSING: Response generation flow
LOG_SYSTEM_INFORMATION: System lifecycle events
SHOW_CHAT: Live chat message display

Message Categorization

Each log call tagged with MessageType
Category determines if message logs
Color coding for GUI display
Console vs GUI output routing

Critical Feature
Logger checks Config singleton at log time, not at initialization. This enables real-time logging control without restart.

Data Flow Summary
Typical Processing Flow

Input Arrives

User message, chat activity, tool result, or timer event
Filtered through centralized input filter
Ingested into ThoughtBuffer as raw event


Cognitive Processing

Cognitive loop detects pending event
ThoughtProcessor generates interpretation
Thought added to buffer with priority
Tool actions identified and queued


Tool Execution

ToolManager validates action against enabled tools
ActionStateManager registers pending action
Tool executes asynchronously
Result injected back into ThoughtBuffer


Response Decision

ThoughtBuffer evaluates accumulated state
Checks priority levels, unspoken count, timing
Returns (should_speak, reason, urgency)
If False, continues thinking without speaking


Response Generation

ResponseGenerator synthesizes spoken output
Uses thought chain + memory context
Applies personality examples
Returns natural language text


Output Processing

Response filtered through centralized output filter
Added to ThoughtBuffer as response echo
Routed to TTS system
Memory system saves interaction




Key Design Principles
Separation of Concerns

Thoughts are internal, responses are external
Memory retrieval separate from memory storage
Tool execution isolated from tool instruction
Configuration separate from runtime state

Event-Driven Architecture

Raw events queued for processing
Thought generation triggered by events
Tool results feed back as events
Asynchronous execution throughout

State Immutability

Thought buffer is append-only
Thoughts never modified after creation
Spoken status tracked separately
Clear audit trail of cognitive process

Prompt Construction Philosophy

Modular components assembled dynamically
Context-aware section inclusion
Token budget management
Personality consistency via centralization

Continuous Operation

No polling loops with arbitrary delays
Processing happens as fast as hardware allows
Natural pacing through event availability
Rate limiting only for external outputs (speech)


Integration Points
External System Connections
Text-to-Speech (TTS)

Receives final response text
Agent marks response echo in buffer immediately
TTS plays asynchronously
No blocking of thought processing

GUI Interface

Receives log callbacks for display
Updates control states via ControlManager
Loads session files via SessionFileManager
Displays statistics via performance methods

Discord/Twitch/YouTube

Chat messages flow through ChatHandler
Unified message format across platforms
Platform-specific features preserved in metadata
Response routing handled by integration layer


This system represents a sophisticated agentic architecture balancing continuous autonomous cognition with selective, natural communication—designed for coherent, context-aware AI assistants that think continuously but speak purposefully.