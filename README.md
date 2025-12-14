# Agentic AI System Architecture

## 💡 Overview
This is a sophisticated agentic AI system built on Ollama that implements a two-stage cognitive architecture separating internal thinking from external communication. The agent maintains continuous autonomous thought, manages multiple memory tiers, executes tools dynamically, and generates natural spoken responses.

**This system was created by @KryptykBioz**
**Anna_AI was created as an open-source, free-to-use agentic system for personal use only.**
**Other projects and information can be found here:**
Github: [KryptykBioz](https://github.com/KryptykBioz)
YouTube : [@KryptykBioz](https://www.youtube.com/@KryptykBioz)
Twitch: [Kryptykbioz](https://www.twitch.tv/kryptykbioz)

**This framework was created in my free time without formal training. As I am self-taught, self-funded, and created this for the public, any contribution to my work is greatly appreciated (and much needed!). Consider making a small donation, subscribing to my channels, or liking some of my videos to keep me going as I continue creating these kinds of agents for others to use. Thank you!**

---

## 📑 Table of Contents

### Core Systems
1. [Core Processing Architecture](#core-processing-architecture)
   - [Overview](#overview)
   - [Key Design Principles](#key-design-principles)
   - [Processing Flow](#processing-flow)
   - [Component Responsibilities](#component-responsibilities)
   - [Adaptive Behavior](#adaptive-behavior)
   - [Performance Characteristics](#performance-characteristics)

2. [Modular Prompting System](#modular-prompting-system)
   - [Overview](#overview-1)
   - [Design Philosophy](#design-philosophy)
   - [Prompt Construction Flow](#prompt-construction-flow)
   - [Constructor Responsibilities](#constructor-responsibilities)
   - [Tool Instruction Persistence](#tool-instruction-persistence)
   - [Personality Injection System](#personality-injection-system)
   - [Grounding and Hallucination Prevention](#grounding-and-hallucination-prevention)
   - [Output Format Specifications](#output-format-specifications)
   - [Adaptive Prompt Complexity](#adaptive-prompt-complexity)
   - [Memory-Augmented Example Retrieval](#memory-augmented-example-retrieval)
   - [Performance Optimization](#performance-optimization)
   - [Extension and Customization](#extension-and-customization)

3. [Memory System](#memory-system)
   - [Overview](#overview-2)
   - [Architecture](#architecture)
   - [Memory Tiers](#memory-tiers)
   - [Summarization System](#summarization-system)
   - [Memory Search](#memory-search)
   - [Context Building](#context-building)
   - [Date Rollover](#date-rollover)
   - [Memory Integrity](#memory-integrity)

4. [Tool Handler System](#tool-handler-system)
   - [Overview](#overview-3)
   - [Core Design Principles](#core-design-principles-1)
   - [Tool System Architecture](#tool-system-architecture)
   - [BaseTool Architecture](#basetool-architecture)
   - [Tool Discovery and Lifecycle](#tool-discovery-and-lifecycle)
   - [Instruction Persistence System](#instruction-persistence-system)
   - [Action State Management](#action-state-management)
   - [Tool Integration Patterns](#tool-integration-patterns)
   - [Tool Instruction Documentation](#tool-instruction-documentation)
   - [Error Handling and Guidance](#error-handling-and-guidance)
   - [Performance Optimization](#performance-optimization-1)
   - [Extension and Customization](#extension-and-customization-1)

5. [Graphical User Interface System](#graphical-user-interface-system)
   - [Overview](#overview-4)
   - [Design Philosophy](#design-philosophy-1)
   - [GUI Architecture](#gui-architecture)
   - [View Components](#view-components)
   - [Theme System](#theme-system)
   - [Message Processing](#message-processing)
   - [Voice Manager](#voice-manager)
   - [Control Panel Manager](#control-panel-manager)
   - [Dynamic Tool Panel System](#dynamic-tool-panel-system)
   - [Session Files Panel](#session-files-panel)
   - [Configuration Management](#configuration-management)
   - [Error Handling](#error-handling)
   - [Performance Optimizations](#performance-optimizations)
   - [Extensibility](#extensibility)
   - [Keyboard Shortcuts](#keyboard-shortcuts)
   - [Accessibility Features](#accessibility-features)

### Supporting Systems
6. [Session Management](#️-session-management)
   - [Session File System](#session-file-system)

7. [Chat Engagement System](#-chat-engagement-system)
   - [Multi-Platform Chat Integration](#multi-platform-chat-integration)
   - [Chat Engagement Logic](#chat-engagement-logic)

8. [Configuration System](#️-configuration-system)
   - [Singleton Architecture](#singleton-architecture)
   - [Dynamic Control Variables](#dynamic-control-variables)

9. [Content Filtering](#️-content-filtering)
   - [Centralized Filtering Architecture](#centralized-filtering-architecture)

10. [Logging System](#-logging-system)
    - [Centralized Logging Controls](#centralized-logging-controls)

### System Overview
11. [Data Flow Summary](#-data-flow-summary)
    - [Typical Processing Flow](#typical-processing-flow)

12. [Key Design Principles](#-key-design-principles)

13. [Integration Points](#-integration-points)

---

# Core Processing Architecture

## Overview

This agentic framework implements a continuous cognitive processing system that operates independently of user input. The agent maintains an internal stream of consciousness, accumulates observations and thoughts, and decides when to generate verbal responses based on priority signals and accumulated context.

The architecture separates **thinking** (internal cognitive processing) from **speaking** (verbal output generation), enabling the agent to continuously process information while selectively engaging in conversation when appropriate.

## Key Design Principles

**Continuous Cognition**: The agent thinks constantly through an autonomous cognitive loop, processing events and forming thoughts regardless of user activity.

**Event-Driven Processing**: Raw incoming data (user messages, tool results, observations) are queued as events and transformed into interpreted thoughts through the thinking model.

**Priority-Based Response**: Thoughts are tagged with priority levels (LOW, MEDIUM, HIGH, CRITICAL) that determine urgency and influence when the agent should speak.

**Modular Prompts**: Different cognitive modes (responsive, planning, reflective) use specialized prompt constructors optimized for their specific reasoning patterns.

**Separation of Concerns**: The system cleanly separates event capture, thought interpretation, priority assessment, prompt construction, and response generation into distinct components.

## Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CONTINUOUS COGNITIVE LOOP                        │
│                     (Runs autonomously at ~100-500ms)                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         1. RAW EVENT CAPTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│  • User input (messages, commands)                                       │
│  • Tool execution results (success, failure, timeout)                    │
│  • Chat messages (Discord, Twitch, YouTube)                              │
│  • Vision observations (screen analysis)                                 │
│  • Memory retrievals (past conversations)                                │
│  • System events (reminders, notifications)                              │
│                                                                           │
│  ➜ Events queued in ThoughtBuffer.unprocessed_events                    │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      2. THOUGHT INTERPRETATION                           │
├─────────────────────────────────────────────────────────────────────────┤
│  ThoughtProcessor processes each raw event through thinking model:       │
│                                                                           │
│  Raw Event → LLM Interpretation → Processed Thought                      │
│                                                                           │
│  • Short prompt: "What does this mean to you?"                           │
│  • Agent personality applied                                             │
│  • Recent thoughts included for context                                  │
│  • Output: 1-2 sentence internal thought                                 │
│                                                                           │
│  ➜ Thoughts stored with metadata: [TIMESTAMP][SOURCE][PRIORITY]         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        3. PRIORITY ASSIGNMENT                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Automatic priority tagging based on event source:                       │
│                                                                           │
│  [CRITICAL] → Urgent reminders, direct mentions                          │
│  [HIGH]     → User input, direct questions, tool failures                │
│  [MEDIUM]   → Chat messages, tool results, observations                  │
│  [LOW]      → Background events, ambient data                            │
│                                                                           │
│  ➜ Priority stored as metadata on each thought                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       4. MODE DETERMINATION                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ThinkingModes analyzes context to determine cognitive mode:             │
│                                                                           │
│  Priority 1: STARTUP                                                     │
│    ➜ First 3 thoughts use memory_reflection_startup                     │
│                                                                           │
│  Priority 2: SELF-REFLECTION                                             │
│    ➜ Past-related keywords OR 6+ min idle                               │
│    ➜ Uses memory_reflection mode                                        │
│                                                                           │
│  Priority 3: FUTURE PLANNING                                             │
│    ➜ Planning keywords detected                                          │
│    ➜ Uses future_planning mode                                          │
│                                                                           │
│  Priority 4: STANDARD (default)                                          │
│    ➜ Uses standard planning mode                                         │
│                                                                           │
│  ➜ Mode determines which prompt constructor to use                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      5. RESPONSE DECISION                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ResponseDecider analyzes thought buffer to determine action:            │
│                                                                           │
│  A. SHOULD SPEAK?                                                        │
│     • HIGH/CRITICAL priority detected? → YES                             │
│     • Direct mention or question? → YES                                  │
│     • Thought accumulation threshold reached? → YES                      │
│     • Otherwise → NO (continue thinking silently)                        │
│                                                                           │
│  B. WHICH PROMPT TYPE?                                                   │
│     • Incoming input → RESPONSIVE (process new data)                     │
│     • Recent input (<6 min) → PLANNING (set goals)                       │
│     • Idle (6+ min) → REFLECTIVE (review memories)                       │
│     • Need verbal output → SPOKEN (generate response)                    │
│                                                                           │
│  ➜ Returns PromptDecision with type and reasoning                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     6. PROMPT CONSTRUCTION                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Modular constructors build specialized prompts:                         │
│                                                                           │
│  ResponsiveConstructor:                                                  │
│    • Analyzes incoming data and context                                  │
│    • Detects tools, vision data, chat messages                           │
│    • Constructs focused response prompt                                  │
│    • Includes tool usage instructions if relevant                        │
│                                                                           │
│  ReflectiveConstructor:                                                  │
│    • Queries memory system for relevant past experiences                 │
│    • Builds context from memories and current thoughts                   │
│    • Constructs introspective reasoning prompt                           │
│    • Optimized for long-term pattern recognition                         │
│                                                                           │
│  PlanningConstructor:                                                    │
│    • Analyzes current state and available tools                          │
│    • Constructs goal-setting and action-planning prompt                  │
│    • Includes time context and user activity status                      │
│    • Optimized for proactive behavior                                    │
│                                                                           │
│  SpokenConstructor (when verbal output needed):                          │
│    • Synthesizes recent thought chain                                    │
│    • Applies personality and conversation style                          │
│    • Constructs natural language response prompt                         │
│    • Optimized for human-readable output                                 │
│                                                                           │
│  ➜ Each constructor outputs optimized prompt for specific reasoning      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       7. LLM GENERATION                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Constructed prompt sent to appropriate LLM:                             │
│                                                                           │
│  Thinking Model (fast, efficient):                                       │
│    • Used for internal thoughts and reasoning                            │
│    • Generates <think> tags with brief thoughts                          │
│    • May include <action_list> with tool calls                           │
│                                                                           │
│  Text Model (higher quality):                                            │
│    • Used for verbal responses to users                                  │
│    • Generates natural conversational output                             │
│    • Applied personality and style constraints                           │
│                                                                           │
│  ➜ Response parsed and validated                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      8. ACTION EXECUTION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  If LLM generated tool actions:                                          │
│                                                                           │
│  • Parse <action_list> JSON                                              │
│  • Validate against enabled tools                                        │
│  • Queue actions in ActionStateManager                                   │
│  • Execute asynchronously via ToolManager                                │
│  • Track pending/completed/failed states                                 │
│                                                                           │
│  Results queued as new raw events → back to step 1                       │
│                                                                           │
│  ➜ Tool results feed back into cognitive loop                            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       9. OUTPUT DELIVERY                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  If verbal response generated:                                           │
│                                                                           │
│  • Clean response (remove emojis, formatting)                            │
│  • Apply content filter (if enabled)                                     │
│  • Route to appropriate output channel:                                  │
│    - GUI text display                                                    │
│    - TTS speech synthesis                                                │
│    - Discord/Twitch/YouTube chat                                         │
│                                                                           │
│  • Mark thoughts as spoken                                               │
│  • Update response timing                                                │
│                                                                           │
│  Loop continues → back to step 1                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### ThoughtBuffer
Central storage for cognitive state. Maintains queues of unprocessed events and processed thoughts. Tracks priorities, spoken status, and user interaction timing. Provides formatted thought chains for prompt construction.

### ThoughtProcessor
Core orchestrator that processes raw events into thoughts, determines cognitive modes, constructs prompts, calls LLMs, and coordinates action execution. Manages the flow from input to output.

### CognitiveLoopManager
Autonomous loop runner that continuously calls ThoughtProcessor. Handles pacing (fast when active, slower when idle), manages response rate limiting, and ensures thinking continues even during response generation.

### ResponseDecider
Analyzes thought buffer and context to determine whether verbal response is needed and which prompt type to use. Scans for priority markers and applies decision rules based on timing and content.

### Prompt Constructors
Specialized modules (Responsive, Reflective, Planning, Spoken) that build optimized prompts for different reasoning modes. Each incorporates relevant context, personality, and constraints for their specific task.

### ToolManager
Manages available tools, validates action requests, and coordinates execution. Provides tool documentation to prompt constructors and tracks action states for feedback into thinking loop.

### ActionStateManager
Tracks pending, completed, and failed tool actions. Provides failure summaries to inform future decisions. Manages timeouts and retry logic.

## Adaptive Behavior

The system implements several adaptive mechanisms:

**Momentum Tracking**: Consecutive proactive thoughts build momentum, encouraging sustained reasoning on topics of interest.

**Context Decay**: Older thoughts naturally lose influence, preventing the agent from fixating on stale information.

**Priority Elevation**: Events can trigger immediate priority escalation (e.g., direct mentions force CRITICAL priority).

**Mode Switching**: The agent fluidly transitions between responsive, planning, and reflective modes based on environmental context.

**Response Pacing**: Rate limiting prevents over-communication while allowing urgent responses through. Thinking continues unrestricted regardless of speaking frequency.

## Performance Characteristics

The cognitive loop operates at high frequency (10-20 cycles per second) during active periods, ensuring rapid response to new events. When idle, it adaptively slows to conserve resources while maintaining readiness. The separation of thinking and speaking allows the agent to maintain continuous cognitive activity (processing ~500-2000 thoughts per hour) while speaking selectively (1-10 responses per hour) based on actual need rather than arbitrary timing.

This architecture enables natural, context-aware behavior that feels responsive to users while operating autonomously in the background, much like a human maintaining continuous awareness while choosing when to verbally engage.

---

## 💾 Memory Architecture

### Four-Tier Memory System

| Tier | Scope | Storage | Retrieval | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **1. Short-Term** | Current session (last few hours) | Recent conversation turns in memory | Chronological, recency-based | Immediate context for responses |
| **2. Medium-Term** | Earlier today (same session) | Embedded conversation chunks | Semantic similarity search | Earlier context from today's interactions |
| **3. Long-Term** | Past days/weeks | Daily conversation summaries with embeddings | Semantic similarity search across summaries | Historical context and patterns |
| **4. Base Knowledge** | Permanent reference material | Static documents chunked and embedded | Semantic search with domain filtering | Instructions, guides, personality examples |

### Enhanced Memory Retrieval
The system uses combined query embedding for memory search:

* **Hybrid Query Construction:** Combines user input + recent thoughts into a single query. Weights user input higher (0.7) vs thoughts (0.3) to create a richer semantic representation of current context.
* **Benefits:** Memory retrieval considers what the agent is thinking about, not just explicit queries. Finds relevant memories based on cognitive context and improves coherence between thoughts and retrieved information.

---

# Modular Prompting System

## Overview

This agentic framework employs a sophisticated modular prompting architecture that adapts to different cognitive modes and communication needs. Instead of using a single monolithic prompt, the system dynamically constructs specialized prompts optimized for specific reasoning patterns: responsive processing of new events, reflective analysis of past experiences, forward-looking planning, and natural spoken communication.

The prompting system separates **what to think about** (mode determination) from **how to think about it** (prompt construction), enabling the agent to maintain consistent personality while adapting its reasoning approach to the situation at hand.

## Design Philosophy

**Separation of Concerns**: Prompt construction is completely decoupled from decision logic. The ResponseDecider determines what type of thinking is needed, while specialized Constructors build the appropriate prompts.

**Reusable Components**: Prompt parts are modularized into reusable pieces (personality injection, grounding rules, output formats) that can be mixed and matched across different modes.

**Context-Aware Composition**: Each constructor intelligently selects and orders relevant context based on the reasoning mode, ensuring the LLM receives information in the most useful format.

**Persistent Instructions**: Tools can have their detailed instructions cached and selectively included in prompts only when relevant, avoiding prompt bloat while maintaining capability awareness.

**Personality Consistency**: A single unified personality definition is injected into all prompts, ensuring the agent maintains consistent character across different reasoning modes.

## Prompt Construction Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PROMPT CONSTRUCTION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────┘

STAGE 1: MODE DETERMINATION
┌─────────────────────────────────────────────────────────────────────────┐
│                           ResponseDecider                                │
├─────────────────────────────────────────────────────────────────────────┤
│ Analyzes:                                                                │
│  • Priority markers in thought chain ([HIGH], [CRITICAL])                │
│  • Presence of incoming events                                           │
│  • Time since last user input                                            │
│  • Memory-related keywords                                               │
│  • Planning-related keywords                                             │
│                                                                           │
│ Outputs:                                                                 │
│  • PromptType: RESPONSIVE | REFLECTIVE | PLANNING | SPOKEN              │
│  • Priority level (1-10)                                                 │
│  • Reasoning explanation                                                 │
│  • Context flags (special handling indicators)                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
STAGE 2: CONSTRUCTOR SELECTION
┌─────────────────────────────────────────────────────────────────────────┐
│                        Route to Appropriate Constructor                  │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RESPONSIVE    │    │   REFLECTIVE    │    │    PLANNING     │
│  Constructor    │    │  Constructor    │    │  Constructor    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      If needs speech    │
                    │   → SPOKEN Constructor  │
                    └─────────────────────────┘

STAGE 3: COMPONENT ASSEMBLY
┌─────────────────────────────────────────────────────────────────────────┐
│                    Each Constructor Assembles Prompt                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. PERSONALITY INJECTION                                                │
│     ├─ Core identity (who the agent is)                                  │
│     ├─ Personality traits (friendly, curious, helpful)                   │
│     ├─ Communication style (casual gamer language)                       │
│     └─ Voice guidelines (natural expressions)                            │
│                                                                           │
│  2. RECENT THOUGHT CHAIN                                                 │
│     ├─ Last 5-10 thoughts with metadata                                  │
│     ├─ Formatted: [TIMESTAMP] [SOURCE] [PRIORITY] content                │
│     └─ Provides continuity between reasoning cycles                      │
│                                                                           │
│  3. MODE-SPECIFIC INSTRUCTIONS                                           │
│     ├─ What kind of thinking to do                                       │
│     ├─ Expected output format                                            │
│     └─ Constraints and guidelines                                        │
│                                                                           │
│  4. CONTEXT INJECTION                                                    │
│     ├─ Retrieved memories (if relevant)                                  │
│     ├─ Tool instructions (if actions likely)                             │
│     ├─ Session files (if referenced)                                     │
│     ├─ Vision data (if present)                                          │
│     ├─ Chat messages (if engagement mode)                                │
│     └─ Pending actions (if awaiting results)                             │
│                                                                           │
│  5. PRIMARY CONTENT                                                      │
│     ├─ Responsive: Raw events to interpret                               │
│     ├─ Reflective: Memories to analyze                                   │
│     ├─ Planning: Current situation assessment                            │
│     └─ Spoken: User message or chat to address                           │
│                                                                           │
│  6. GROUNDING RULES                                                      │
│     ├─ Hallucination prevention                                          │
│     ├─ Data verification requirements                                    │
│     └─ Uncertainty acknowledgment                                        │
│                                                                           │
│  7. OUTPUT FORMAT SPECIFICATION                                          │
│     ├─ XML tag structure                                                 │
│     ├─ Length constraints                                                │
│     └─ Action list format                                                │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

STAGE 4: SPECIALIZED ENHANCEMENTS
┌─────────────────────────────────────────────────────────────────────────┐
│                  Constructor-Specific Optimizations                      │
└─────────────────────────────────────────────────────────────────────────┘

ResponsiveConstructor:
  • Checks tool instruction persistence
  • Includes detailed tool docs if recently used
  • Adds vision grounding for visual observations
  • Formats incoming events for interpretation

ReflectiveConstructor:
  • Detects startup mode (first 3 thoughts)
  • Loads comprehensive context for startup
  • Queries memory system for relevant past
  • Builds temporal context (yesterday, earlier today)

PlanningConstructor:
  • Formats time context (minutes since user input)
  • Includes current trajectory assessment
  • Adds anticipatory planning guidelines
  • Optimizes for goal-setting behavior

SpokenConstructor:
  • Retrieves personality-matched examples from memory
  • Combines thought context + user input for example search
  • Adjusts guidance based on priority level
  • Optimizes for natural spoken output
```

## Constructor Responsibilities

### ResponsiveConstructor
**Purpose**: Process incoming events and generate interpretive thoughts

**Input Processing**:
- Raw event queue (user messages, tool results, observations)
- Recent thought chain for continuity
- Last user message for context
- Pending actions summary
- Additional context parts

**Prompt Strategy**:
- Leads with personality to maintain character
- Includes recent thoughts to preserve narrative flow
- Lists incoming events clearly with source tags
- Adds tool instructions if relevant (checks persistence)
- Emphasizes grounding rules to prevent hallucination
- Requests one thought per event (numbered list format)
- Allows optional action planning

**Output Format**:
```xml
<thoughts>
[1] Thought about event 1
[2] Thought about event 2
</thoughts>
<think>Optional strategic thought</think>
<action_list>[{tool actions}]</action_list>
```

### ReflectiveConstructor
**Purpose**: Connect past experiences to present situation

**Modes**:
- **Startup Mode**: First 3 thoughts use comprehensive initialization
- **Standard Mode**: Memory-triggered reflection on relevant past

**Startup Context Loading**:
1. Core identity knowledge from base memory
2. Personality examples from past behavior
3. Long-term memory summaries (recent days)
4. Yesterday's full conversation
5. Last session's message history

**Standard Context Loading**:
1. Current situation description
2. Relevant memories from query-based search
3. Temporal context (yesterday, earlier today)

**Prompt Strategy**:
- Emphasizes memory grounding (only reference provided memories)
- Focuses on pattern recognition and insight
- Requests single reflective thought (15-50 words)
- Encourages genuine connections, not forced ones
- Maintains conversational authenticity

**Output Format**:
```xml
<think>Single reflective thought</think>
<action_list>[{optional tool actions}]</action_list>
```

### PlanningConstructor
**Purpose**: Anticipate needs and plan future actions

**Context Building**:
- Current situation assessment
- Time context (how long since user input)
- User activity status
- Available tools and capabilities

**Prompt Strategy**:
- Encourages proactive thinking
- Focuses on anticipation and preparation
- Emphasizes actionable planning
- Suggests helpful preparatory actions
- Maintains agent's helpful personality

**Output Format**:
```xml
<think>Forward-looking planning thought</think>
<action_list>[{tool actions for preparation}]</action_list>
```

### SpokenConstructor
**Purpose**: Generate natural verbal responses to users

**Context Building**:
- Recent thought chain (what agent has been thinking)
- User input or chat messages to address
- Retrieved personality-matched examples
- Memory context if relevant
- Chat context if engaging with stream

**Example Retrieval Innovation**:
Unlike other constructors, SpokenConstructor uses a **combined query approach** for retrieving personality examples:
```
Query = Recent Thoughts + User Input + Chat Context
```
This ensures examples match the full conversational situation, not just the user's words in isolation. The system searches past conversations for similar **thought states** + **user interactions**, finding responses that fit the agent's current mental context.

**Priority-Based Guidance**:
- **CRITICAL** (9-10): "Respond immediately and acknowledge urgency"
- **HIGH** (7-8): "Answer directly and clearly"
- **MEDIUM** (5-6): "Respond naturally based on thoughts"
- **CHAT ENGAGEMENT**: "Address chat members by name, keep conversational"

**Prompt Strategy**:
- Places personality examples BEFORE thoughts (prime the style)
- Includes thought chain for context
- Adds user message or chat to address
- Provides urgency-appropriate guidance
- Enforces brevity (1-2 sentences)
- Emphasizes natural conversational tone

**Output Format**:
```
Direct natural language response (no XML tags)
```

## Tool Instruction Persistence

The system implements **intelligent tool instruction caching** to balance prompt efficiency with capability awareness:

### When Tool Instructions Are Minimal
If no tools have been recently used, prompts include only a **brief tool list**:
```
## AVAILABLE TOOLS
- search: Web search
- reminder: Set reminders
- vision: Analyze screen
- [etc...]
```

### When Tool Instructions Are Detailed
If a tool has been used recently (within persistence window), the **full instruction documentation** is included:
```
## TOOL: search
Purpose: Perform web searches for current information
Usage: {"tool": "search", "args": ["query"]}
Parameters:
  - query: Search terms (string)
Examples:
  - Search for recent news: {"tool": "search", "args": ["news today"]}
  - Find information: {"tool": "search", "args": ["topic details"]}
Constraints:
  - Keep queries concise (2-5 words optimal)
  - Use natural language
  - One search per action
```

This **dynamic instruction loading** is managed by the InstructionPersistenceManager, which tracks tool usage and determines when detailed guidance is beneficial versus wasteful.

## Personality Injection System

All prompts begin with a **unified personality definition** from `PersonalityPromptParts.get_unified_personality()`:

```markdown
## Core Identity
You are [AgentName], a cheerful gaming AI assistant helping [Username].

## Personality Traits
- Friendly & Enthusiastic: Genuine warmth and excitement
- Helpful & Proactive: Anticipate needs and offer assistance
- Curious & Observant: Notice details and make connections
- Warm & Supportive: Care about user's experience

## Communication Style
- Use casual gamer language naturally
- Speak in first person
- Be enthusiastic when appropriate
- Stay conversational and genuine
- Show personality through word choice

## Voice Guidelines
- Use natural language fillers
- Be genuinely engaged, not robotic
- React authentically in your own voice
- Keep things casual like a gaming buddy
- Vary expressions - don't repeat phrases
```

This single source of truth ensures **personality consistency** across all reasoning modes while allowing constructors to emphasize different aspects (thinking voice vs. speaking voice).

## Grounding and Hallucination Prevention

Every prompt includes **strict grounding rules** to prevent the agent from inventing information:

### Universal Grounding Rules
```
CRITICAL CONSTRAINTS:
1. Base thoughts ONLY on explicitly provided data
2. Never hallucinate or invent information
3. If data is unclear, acknowledge uncertainty
4. Think step-by-step about what you observe
5. Stay factual and grounded in reality
```

### Mode-Specific Grounding

**Vision Data Grounding**:
```
Vision data contains FACTUAL OBSERVATIONS ONLY.
- Accept vision descriptions AS-IS
- Do NOT elaborate beyond what vision states
- Do NOT invent details not mentioned
- ACKNOWLEDGE, don't INTERPRET
```

**Tool Status Grounding**:
```
Tool status events are FACTUAL SYSTEM STATE.
- "Initiated X" = Command SENT, NOT completed
- "FAILED: X" = Confirmed error
- "TIMEOUT: X" = No response
- NEVER say "I searched" if you only see "Initiated search"
- ALWAYS distinguish "started" vs "completed"
```

**Memory Grounding**:
```
When reflecting on memories:
- Only reference memories explicitly provided
- Don't invent past events
- "I remember X" only if X is in memory context
- If uncertain, say "I think" or "I recall"
```

These grounding rules are **actively enforced** through prompt structure, and violations are caught during response parsing and validation.

## Output Format Specifications

Each constructor enforces specific output formats optimized for its purpose:

### Thinking Formats (Responsive, Reflective, Planning)
```xml
<think>Internal thought content</think>
<action_list>[{"tool": "name", "args": [...]}]</action_list>
```

### Spoken Format (Natural Language)
```
Direct conversational response with no XML tags
```

The system **parses** these formats using regex patterns:
- `<think>(.*?)</think>` extracts internal thoughts
- `<action_list>(.*?)</action_list>` extracts tool actions as JSON
- Actions are validated against enabled tools
- Invalid actions are rejected with helpful error messages

## Adaptive Prompt Complexity

The system adapts prompt complexity based on context:

### Minimal Complexity
- No recent tool usage → Brief tool list
- No relevant memories → Skip memory section
- No chat activity → Skip chat context
- No vision data → Skip vision grounding

### Maximum Complexity
- Recent tool usage → Full tool documentation
- Memory keywords detected → Retrieved memories + yesterday's context
- Active chat → Full chat engagement context
- Vision data present → Enhanced grounding rules
- Multiple context types → All relevant sections included

This adaptive approach ensures prompts are **information-rich when needed** but **lean when possible**, optimizing both LLM performance and response quality.

## Memory-Augmented Example Retrieval

The SpokenConstructor implements a sophisticated **personality example retrieval system**:

### Traditional Approach (Avoided)
```
User: "What game should I play?"
Query: "What game should I play?"
→ Retrieves examples of answering game questions
```

### This System's Approach
```
User: "What game should I play?"
Agent's Recent Thoughts: 
  - "User seems bored with current game"
  - "They prefer action games with good stories"
  - "Haven't played anything new in a week"

Query: "User seems bored with current game. They prefer action games 
        with good stories. What game should I play? What game should I play?"
→ Retrieves examples of thoughtful game recommendations
   considering user's context and preferences
```

This **context-aware retrieval** finds examples where the agent's **internal cognitive state** matches the current situation, not just where the user's words match. The result is responses that feel more personalized and situationally appropriate.

## Performance Optimization

The modular prompt system includes several performance optimizations:

**Component Caching**: Personality injection and grounding rules are static and could be cached (not currently implemented but architecture supports it)

**Lazy Loading**: Context components are only built when needed based on mode and flags

**Selective Inclusion**: Tool instructions, memories, and session files are included only when relevant

**Length Constraints**: Each component has maximum lengths to prevent prompt bloat

**Priority Ordering**: Most important context appears first (tool state, session files, user message)

These optimizations ensure the system scales efficiently even with large memory systems and many available tools.

## Extension and Customization

The modular architecture makes the system highly extensible:

**Adding New Modes**: Create a new Constructor class inheriting from base pattern, implement `build_prompt()` method, register in ResponseDecider

**Customizing Personality**: Edit `PersonalityPromptParts.get_unified_personality()` to change agent character across all modes simultaneously

**Adding Prompt Components**: Create new methods in `*_parts.py` modules, compose into constructor prompts as needed

**Adjusting Grounding**: Modify grounding rules in `*_parts.py` modules to enforce different constraints

**Tool Integration**: Implement `ToolInstructionBuilder` methods to format new tool types

The separation of decision logic, prompt construction, and reusable components makes the system **maintainable and adaptable** to new requirements without cascading changes.

---

## 🛠️ Tool System

# Tool Handler System

## Overview

This agentic framework implements a sophisticated tool system that enables the agent to interact with external capabilities through a unified, extensible architecture. Tools are first-class system components that can be dynamically enabled/disabled, execute actions asynchronously, inject context into the agent's thought stream, and maintain persistent instruction state to optimize prompt efficiency.

The tool system is built on the **BaseTool architecture**, where each tool is a self-contained module with standardized lifecycle management, execution patterns, and instruction documentation. This design enables seamless integration of new capabilities without modifying core agent logic.

## Core Design Principles

**Separation of Concerns**: Tool lifecycle (discovery, start, stop) is managed separately from execution (command processing, result handling). This separation enables hot-swapping of tools without disrupting the cognitive loop.

**Instruction Persistence**: Tools track whether their detailed instructions have been recently retrieved, avoiding prompt bloat by only including full documentation when relevant. Instructions persist for 6 minutes after retrieval, after which they must be requested again.

**Async-First Execution**: All tool operations are asynchronous, preventing any single tool from blocking the cognitive loop. Timeouts and cancellation are built into the execution layer.

**Event-Driven Integration**: Tool results feed back into the agent's cognitive stream as raw events, ensuring all tool outputs undergo the same interpretation process as user inputs.

**State Tracking**: The ActionStateManager maintains complete execution history (pending, in-progress, completed, failed) enabling the agent to reference past actions and learn from failures.

**Graceful Degradation**: Tool failures are non-fatal and generate informative error messages that guide the agent toward correct usage.

## Tool System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TOOL SYSTEM HIERARCHY                            │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────┐
                    │     ToolManager         │
                    │  (Main Orchestrator)    │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
    ┌──────────────────┐ ┌─────────────┐ ┌──────────────────┐
    │ ToolLifecycle    │ │ Instruction │ │ ActionState      │
    │ Manager          │ │ Persistence │ │ Manager          │
    │                  │ │ Manager     │ │                  │
    │ - Discovery      │ │             │ │ - Execution      │
    │ - Loading        │ │ - 6min      │ │   tracking       │
    │ - Start/Stop     │ │   timers    │ │ - Failure        │
    │                  │ │ - Flags     │ │   analytics      │
    └──────────────────┘ └─────────────┘ └──────────────────┘
              │                                   │
              │                                   │
              ▼                                   ▼
    ┌──────────────────┐              ┌──────────────────┐
    │  Active Tools    │              │  Execution       │
    │  Dictionary      │◄─────────────┤  Results         │
    │  {name: inst}    │              │                  │
    └──────────────────┘              └──────────────────┘
              │
              │
              ▼
    ┌──────────────────┐
    │   BaseTool       │
    │   Instances      │
    │                  │
    │   Each tool:     │
    │   - initialize() │
    │   - execute()    │
    │   - cleanup()    │
    │   - context_loop │
    └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         TOOL EXECUTION FLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

1. AGENT GENERATES ACTION
   ThoughtProcessor → LLM produces <action_list>

2. ACTION VALIDATION
   ToolManager receives parsed actions
      ├─ Check tool exists in discovered metadata
      ├─ Check tool is enabled (in active_tools)
      ├─ Check instruction persistence (if enforced)
      └─ Check tool.is_available()

3. ACTION REGISTRATION
   ActionStateManager.register_action()
      └─ Assigns unique action_id
      └─ Records tool, args, timestamp

4. ASYNC EXECUTION
   ActionStateManager.mark_in_progress()
   await tool_instance.execute(command, args)
      ├─ Wrapped in asyncio.wait_for(timeout)
      ├─ Tool performs operation
      └─ Returns standardized result dict

5. RESULT HANDLING
   Success:
      ├─ ActionStateManager.complete_action()
      ├─ Inject result into thought_buffer
      └─ Log success with instruction timing

   Timeout:
      ├─ ActionStateManager.fail_action(reason='timeout')
      ├─ Inject timeout notification
      └─ Log timeout for analytics

   Error:
      ├─ ActionStateManager.fail_action(reason='error')
      ├─ Inject error message
      └─ Log error for debugging

6. FEEDBACK LOOP
   Tool result → ThoughtBuffer.ingest_raw_data()
      └─ Result queued as RawDataEvent
      └─ ThoughtProcessor interprets result
      └─ Agent's next thought considers outcome


┌─────────────────────────────────────────────────────────────────────────┐
│                    INSTRUCTION PERSISTENCE FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

INITIAL STATE: Agent has minimal tool list
┌──────────────────────────────────────────────────────────────────────────┐
│ ## AVAILABLE TOOLS                                                       │
│ - search [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Web search           │
│ - reminder [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Set reminders      │
│ - vision [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Screen analysis      │
│                                                                          │
│ To use a tool, retrieve instructions first:                             │
│ {"tool": "instructions", "args": ["tool_name"]}                         │
└──────────────────────────────────────────────────────────────────────────┘

AGENT DECIDES: Needs search capability
   └─ Generates: {"tool": "instructions", "args": ["search"]}

INSTRUCTION RETRIEVAL:
   ToolManager.handle_instruction_retrieval()
      ├─ Validates "search" is enabled
      ├─ InstructionPersistenceManager.mark_instructions_retrieved("search")
      │    └─ Starts 6-minute timer
      ├─ ToolInstructionBuilder.build_retrieved_tool_instructions(["search"])
      │    └─ Loads information.json from filesystem
      │    └─ Formats complete documentation
      └─ Sets pending_tool_instructions = ["search"]

NEXT PROMPT: Full search instructions included
┌──────────────────────────────────────────────────────────────────────────┐
│ ## RETRIEVED TOOL INSTRUCTIONS                                           │
│                                                                          │
│ ### TOOL: search                                                         │
│ Perform web searches for current information                            │
│                                                                          │
│ **Usage Format:**                                                        │
│ {"tool": "search.query", "args": ["search terms"]}                      │
│                                                                          │
│ **Available Commands:**                                                  │
│ - query: Execute web search                                              │
│                                                                          │
│ **Parameters:**                                                          │
│ - search terms (string): Query to search for                            │
│                                                                          │
│ **Examples:**                                                            │
│ {"tool": "search.query", "args": ["Python tutorials"]}                  │
│ {"tool": "search.query", "args": ["weather Seattle"]}                   │
│                                                                          │
│ **Constraints:**                                                         │
│ - Keep queries concise (2-5 words)                                      │
│ - One search per action                                                  │
│ - Results limited to 10 items                                            │
└──────────────────────────────────────────────────────────────────────────┘

AGENT USES TOOL:
   └─ Generates: {"tool": "search.query", "args": ["latest AI news"]}

PERSISTENCE CHECK:
   ToolManager._execute_single_action()
      ├─ InstructionPersistenceManager.has_active_instructions("search")
      │    └─ Checks if timer valid (< 6 minutes elapsed)
      │    └─ Returns True
      ├─ Validation passes
      └─ Executes search

AFTER 6 MINUTES: Instructions expire
   InstructionPersistenceManager auto-cleanup
      └─ Removes "search" from active instructions

NEXT PROMPT: Back to minimal list (instructions expired)
   └─ Must retrieve again to use

AGENT ATTEMPTS USE WITHOUT RETRIEVAL:
   ToolManager enforcement kicks in:
      └─ Injects error: "Instructions for search expired. Retrieve again to use"
      └─ Agent learns to retrieve instructions first
```

## BaseTool Architecture

Every tool inherits from the `BaseTool` abstract base class, which defines the standardized interface:

### Required Properties and Methods

**name** (property): Unique tool identifier matching the control variable
```python
@property
def name(self) -> str:
    return "search"
```

**initialize()**: Setup connections, load config, verify availability
```python
async def initialize(self) -> bool:
    self.api_key = self._config.SEARCH_API_KEY
    self.connected = await self._connect_to_service()
    return self.connected
```

**cleanup()**: Teardown resources, close connections, save state
```python
async def cleanup(self):
    await self._disconnect_from_service()
    self._cache.clear()
```

**is_available()**: Runtime availability check
```python
def is_available(self) -> bool:
    return self._connected and self._api_key is not None
```

**execute()**: Command execution with standardized result format
```python
async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
    if command == 'query':
        query = args[0]
        results = await self._search(query)
        return self._success_result(results)
    return self._error_result(f'Unknown command: {command}')
```

### Optional Methods

**has_context_loop()**: Indicates need for background updates
```python
def has_context_loop(self) -> bool:
    return True  # This tool needs periodic context injection
```

**context_loop()**: Background task for autonomous behavior
```python
async def context_loop(self, thought_buffer):
    while self._running:
        status = await self._get_status()
        thought_buffer.add_processed_thought(
            content=f"[{self.name}] Status: {status}",
            source='tool_context',
            priority_override='LOW'
        )
        await asyncio.sleep(5.0)
```

### Standardized Result Format

All tool executions return a consistent dictionary structure:

**Success Result**:
```python
{
    'success': True,
    'content': 'Operation completed successfully',
    'source': 'tool_name',
    'metadata': {'key': 'value'},
    'guidance': 'Tool executed successfully'
}
```

**Error Result**:
```python
{
    'success': False,
    'content': 'Error message explaining what went wrong',
    'source': 'tool_name',
    'metadata': {'error_type': 'validation'},
    'guidance': 'Try different arguments or check tool status'
}
```

This standardization enables the ToolManager to handle all tool results uniformly, regardless of the specific tool or operation.

## Tool Discovery and Lifecycle

### Discovery Process

Tools are automatically discovered at system startup:

1. **Scan Directory**: `BASE/tools/installed/` is scanned for tool folders
2. **Validate Structure**: Each folder must contain `tool.py` and `information.json`
3. **Load Metadata**: Parse `information.json` for tool configuration
4. **Cache Information**: Store complete metadata for runtime access
5. **Log Results**: Report discovered tools with control variables

**Required File Structure**:
```
BASE/tools/installed/
├── search/
│   ├── tool.py              # Contains SearchTool class
│   └── information.json     # Metadata and documentation
├── reminder/
│   ├── tool.py              # Contains ReminderTool class
│   └── information.json     # Metadata and documentation
└── vision/
    ├── tool.py              # Contains VisionTool class
    └── information.json     # Metadata and documentation
```

**information.json Structure**:
```json
{
    "tool_name": "search",
    "control_variable_name": "USE_SEARCH",
    "tool_description": "Perform web searches for current information",
    "available_commands": [
        {
            "command": "query",
            "description": "Execute web search",
            "parameters": [
                {
                    "name": "search terms",
                    "type": "string",
                    "description": "Query to search for"
                }
            ],
            "examples": [
                {"tool": "search.query", "args": ["Python tutorials"]},
                {"tool": "search.query", "args": ["weather Seattle"]}
            ]
        }
    ],
    "timeout_seconds": 30,
    "cooldown_seconds": 0,
    "metadata": {
        "display_name": "Web Search",
        "version": "1.0",
        "author": "System"
    }
}
```

### Lifecycle Management

**Tool Startup**:
1. Control variable set to True (e.g., `USE_SEARCH = True`)
2. ToolManager.handle_control_update() triggered
3. ToolLifecycleManager.start_tool() called
4. Dynamic class loading from tool.py
5. Tool instantiation with (config, controls, logger)
6. tool.start() calls initialize()
7. Context loop started if needed
8. Tool added to active_tools dict

**Tool Shutdown**:
1. Control variable set to False
2. ToolManager.handle_control_update() triggered
3. ToolLifecycleManager.stop_tool() called
4. Context loop cancelled if running
5. tool.end() calls cleanup()
6. Tool removed from active_tools dict
7. Instruction persistence cleared

**Runtime State**:
- **Discovered**: Tool exists in metadata cache
- **Enabled**: Control variable is True
- **Active**: Tool instance running in active_tools
- **Available**: tool.is_available() returns True
- **Instructions Retrieved**: Persistence manager has valid timer

## Instruction Persistence System

The instruction persistence system implements a **6-minute rolling window** for tool instruction visibility:

### Persistence States

**No Instructions**: Default state - tool appears in minimal list only
```
- search [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Web search
```

**Instructions Retrieved**: Agent requests instructions explicitly
```
Agent: {"tool": "instructions", "args": ["search"]}
System: Starts 6-minute timer, includes full documentation in next prompt
```

**Instructions Active**: Within 6-minute window - full docs in every prompt
```
Prompt includes:
  ## RETRIEVED TOOL INSTRUCTIONS
  ### TOOL: search
  [complete documentation...]
```

**Instructions Expired**: Timer exceeds 6 minutes
```
System: Auto-removes from active instructions
Next prompt: Back to minimal list
Agent attempts use: "Instructions expired. Retrieve again to use"
```

**Instructions Refreshed**: Agent retrieves again before expiration
```
System: Resets 6-minute timer
Effect: Continues including full documentation
```

### Benefits of Persistence

**Prompt Efficiency**: Minimal tool lists keep prompts lean when tools aren't being used. Full documentation only included when relevant (within 6-minute window of active use).

**Agent Learning**: Enforced retrieval teaches the agent to explicitly request instructions before attempting tool usage, improving reliability.

**Automatic Cleanup**: Expired instructions are automatically removed, preventing stale documentation from accumulating.

**Usage Analytics**: Persistence tracking reveals which tools are actively used versus just enabled.

### Persistence Manager API

```python
# Mark instructions as retrieved (starts 6-minute timer)
manager.mark_instructions_retrieved(tool_name)

# Check if instructions are still valid
has_active = manager.has_active_instructions(tool_name)

# Get remaining time before expiration
remaining_seconds = manager.get_time_remaining(tool_name)

# Get all tools with active instructions
active_tools = manager.get_active_tool_names()

# Manual cleanup (optional - auto-cleanup happens naturally)
manager.clear_instructions(tool_name)

# Get complete status for monitoring
status = manager.get_all_status()
```

## Action State Management

The ActionStateManager tracks complete execution history for analytics and failure learning:

### State Transitions

```
REGISTERED → IN_PROGRESS → COMPLETED (success)
                         → FAILED (timeout/error)
```

### Tracked Information

**Per Action**:
- Unique action_id
- Tool name and command
- Arguments provided
- Registration timestamp
- Status (registered/in_progress/completed/failed)
- Completion timestamp
- Result data
- Error messages (if failed)
- Failure type (timeout/error)

### Failure Analytics

The system maintains failure history enabling:

**Failure Summaries**: Recent failures grouped by tool
```
## RECENT TOOL FAILURES
- search: 3 timeouts in last hour
- reminder: 1 validation error
```

**Failure Patterns**: Detect systematic issues
```
If search.query fails 3+ times:
  → Inject HIGH priority thought: "Search tool experiencing issues"
```

**Adaptive Behavior**: Agent learns from failures
```
After search timeout:
  Next prompt includes: "Previous search timed out - consider simpler query"
```

### State Manager API

```python
# Register new action
action_id = manager.register_action(
    tool_name='search',
    args=['query'],
    context={'user_request': 'find news'}
)

# Update state during execution
manager.mark_in_progress(action_id)

# Complete successfully
manager.complete_action(action_id, result_dict)

# Or record failure
manager.fail_action(action_id, error_message, failure_type)

# Get analytics
pending = manager.get_pending_actions()
failures = manager.get_recent_failures_summary(max_failures=5)
stats = manager.get_statistics()
```

## Tool Integration Patterns

### Pattern 1: Simple Query Tool

Tools that execute one-off queries without persistent state:

```python
class SearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "search"
    
    async def initialize(self) -> bool:
        self.api_key = self._config.SEARCH_API_KEY
        return self.api_key is not None
    
    async def cleanup(self):
        pass  # No persistent connections
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def execute(self, command: str, args: List[Any]) -> Dict:
        if command == 'query':
            results = await self._perform_search(args[0])
            return self._success_result(
                f"Found {len(results)} results",
                metadata={'count': len(results)}
            )
        return self._error_result('Unknown command')
```

### Pattern 2: Stateful Connection Tool

Tools that maintain persistent connections:

```python
class DatabaseTool(BaseTool):
    async def initialize(self) -> bool:
        self.connection = await self._connect_to_db()
        return self.connection is not None
    
    async def cleanup(self):
        if self.connection:
            await self.connection.close()
    
    def is_available(self) -> bool:
        return self.connection and self.connection.is_alive()
    
    async def execute(self, command: str, args: List[Any]) -> Dict:
        if command == 'query':
            result = await self.connection.execute(args[0])
            return self._success_result(result)
        return self._error_result('Unknown command')
```

### Pattern 3: Context-Injecting Tool

Tools that provide autonomous background updates:

```python
class MonitorTool(BaseTool):
    def has_context_loop(self) -> bool:
        return True
    
    async def context_loop(self, thought_buffer):
        while self._running:
            # Check system status
            cpu_usage = await self._get_cpu_usage()
            
            # Inject if noteworthy
            if cpu_usage > 80:
                thought_buffer.add_processed_thought(
                    content=f"System CPU at {cpu_usage}%",
                    source='monitor_alert',
                    priority_override='MEDIUM'
                )
            
            await asyncio.sleep(10.0)
```

## Tool Instruction Documentation

The ToolInstructionBuilder dynamically generates documentation from information.json files:

### Minimal Tool List

When no instructions are active, prompts contain a brief enumeration:

```markdown
## AVAILABLE TOOLS

You have access to **3** enabled tool(s).

**Tool List:**
- `search` [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Web search
- `reminder` [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Set reminders  
- `vision` [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: Screen analysis

## TOOL INSTRUCTION RETRIEVAL

To use a tool, first retrieve its instructions using:

{"tool": "instructions", "args": ["tool_name"]}

**Guidelines:**
- You must retrieve instructions before using any tool
- Retrieve up to 3 tool instructions at a time
```

### Full Tool Documentation

After retrieval, complete documentation is included:

```markdown
## RETRIEVED TOOL INSTRUCTIONS

### TOOL: search
Perform web searches for current information

**Usage Format:**
{"tool": "search.query", "args": ["search terms"]}

**Available Commands:**
- query: Execute web search

**Parameters:**
- search terms (string): Query to search for

**Examples:**
{"tool": "search.query", "args": ["Python tutorials"]}
{"tool": "search.query", "args": ["weather Seattle"]}

**Constraints:**
- Keep queries concise (2-5 words)
- One search per action
- Results limited to 10 items

**Timeout:** 30 seconds
**Cooldown:** None
```

This documentation is automatically generated from information.json, ensuring consistency between implementation and documentation.

## Error Handling and Guidance

The tool system implements comprehensive error handling with informative guidance:

### Validation Errors

**Unknown Tool**:
```
Tool 'unknown_tool' not found.
Available: search, reminder, vision
```

**Disabled Tool**:
```
Tool 'search' is currently DISABLED.
Cannot execute search.query.
Enable via USE_SEARCH=True
```

**Missing Instructions**:
```
Cannot use search: Instructions not retrieved.
Use: {"tool": "instructions", "args": ["search"]}
```

**Expired Instructions**:
```
Instructions for search expired.
Retrieve again to use: {"tool": "instructions", "args": ["search"]}
```

### Execution Errors

**Timeout**:
```
[search] Timeout after 30s
Consider: Simplify query or check network
```

**Tool Unavailable**:
```
[search] Tool not available
Reason: API key not configured
```

**Command Error**:
```
[search] Error: Invalid command 'unknown'
Available commands: query
```

All errors are injected as HIGH priority thoughts, ensuring the agent is aware of issues and can adapt its approach.

## Performance Optimization

The tool system includes several performance optimizations:

**Async Execution**: All tool operations are truly asynchronous, preventing any tool from blocking the cognitive loop or other tools.

**Timeout Enforcement**: Every action has a configurable timeout, preventing runaway operations from hanging the system.

**Instruction Caching**: Once retrieved, instructions persist for 6 minutes, avoiding repeated filesystem reads.

**Lazy Loading**: Tool classes are only loaded when the tool is enabled, not at discovery time.

**Result Streaming**: Large tool results can be streamed incrementally rather than batched.

**Failure Fast-Path**: Validation checks (tool exists, enabled, available) happen before expensive execution.

## Extension and Customization

The tool system is designed for easy extension:

**Adding New Tools**: Create tool folder with tool.py and information.json. Tool is automatically discovered on next startup.

**Custom Base Classes**: Create specialized base classes inheriting from BaseTool for specific tool categories (e.g., WebAPITool, DatabaseTool).

**Instruction Formats**: Modify ToolInstructionBuilder to change documentation formatting or add new metadata fields.

**Execution Hooks**: ActionStateManager supports pre/post execution hooks for logging, metrics, or custom handling.

**Persistence Windows**: Adjust instruction timeout duration globally or per-tool in information.json.

The separation of concerns (lifecycle, execution, persistence, instruction building) means new features can be added to one component without affecting others.

---

# Graphical User Interface System

## Overview

This agentic framework includes a comprehensive Tkinter-based GUI that provides real-time monitoring, configuration management, and interaction with the AI agent. The interface is built on a modular architecture with theme support, dynamic tool panels, and asynchronous message handling that ensures the GUI remains responsive even during intensive processing.

The GUI serves as both a control center for system configuration and a live window into the agent's cognitive processes, displaying internal thoughts, tool execution, memory operations, and external integrations in real-time.

## Design Philosophy

**Modular View Architecture**: Each major interface section (Chat, Controls, Tools, Config, Info) is implemented as an independent view component, enabling focused development and easy maintenance.

**Theme System**: Comprehensive theming support with Light, Dark, and Cyberpunk themes that apply consistently across all interface elements through a centralized theme manager.

**Asynchronous Message Flow**: GUI operations never block the AI core's cognitive loop. All message processing happens in background threads with results queued for GUI updates.

**Dynamic Tool Discovery**: Tool GUI components are automatically discovered and loaded from installed tools, requiring no hardcoded references in the main interface.

**Singleton Pattern**: Single Config and Logger instances are shared across all GUI components, ensuring consistency and preventing configuration drift.

**Event-Driven Updates**: A queue-based message system handles all GUI updates, ensuring thread-safe operations and smooth visual updates.

## GUI Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GUI ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────┘

                         ┌────────────────┐
                         │  OllamaGUI     │
                         │  (Main Entry)  │
                         └────────┬───────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  UIBuilder   │  │ThemeManager  │  │MessageProcessor│
        │              │  │              │  │              │
        │ - Menu       │  │ - Themes     │  │ - Async      │
        │ - Views      │  │ - Styling    │  │   Processing │
        │ - Switching  │  │ - Updates    │  │ - TTS        │
        └──────┬───────┘  └──────────────┘  └──────────────┘
               │
               │
    ┌──────────┼────────────┬──────────────┬──────────────┐
    │          │            │              │              │
    ▼          ▼            ▼              ▼              ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Config  │ │Controls│ │  Chat    │ │  Tools   │ │   Info   │
│  View  │ │  View  │ │  View    │ │  View    │ │  View    │
└────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                          MESSAGE FLOW                                    │
└─────────────────────────────────────────────────────────────────────────┘

USER TYPES MESSAGE IN GUI
         │
         ▼
ChatView.send_message()
         ├─ Content filtering
         ├─ Display in chat
         └─ Forward to handler
         │
         ▼
GUIMessageHandler.handle_user_message()
         ├─ Save to memory
         └─ Spawn processing thread
         │
         ▼
MessageProcessor.process_message()
         ├─ Call AICore.process_user_message()
         ├─ Get response
         └─ Queue for GUI display
         │
         ▼
Message Queue (thread-safe)
         │
         ▼
queue_processor() [main thread]
         ├─ Extract queued messages
         ├─ Update chat display
         ├─ Trigger TTS if enabled
         └─ Update processing indicators


┌─────────────────────────────────────────────────────────────────────────┐
│                      THEME SYSTEM FLOW                                   │
└─────────────────────────────────────────────────────────────────────────┘

User Selects Theme
         │
         ▼
ThemeManager.set_theme(theme_name)
         │
         ▼
Apply theme colors and fonts
         ├─ Update Tkinter styles (ttk)
         ├─ Configure text widgets
         ├─ Update custom widgets
         └─ Recreate menu with new styling
         │
         ▼
Update all active view elements
         ├─ ChatView color tags
         ├─ System log colors
         ├─ Button appearances
         └─ Tab styling


┌─────────────────────────────────────────────────────────────────────────┐
│                   DYNAMIC TOOL PANEL LOADING                             │
└─────────────────────────────────────────────────────────────────────────┘

ToolsView.create_tools_view()
         │
         ▼
DynamicToolPanelLoader.discover_tool_panels()
         ├─ Scan BASE/tools/installed/
         ├─ Find tools with component.py
         └─ Load information.json metadata
         │
         ▼
For each tool with component:
         │
         ▼
DynamicToolPanelLoader.load_component()
         ├─ Import component.py dynamically
         ├─ Call create_component(parent, ai_core, logger)
         └─ Return component instance
         │
         ▼
ToolsView._create_tool_tab()
         ├─ Create dedicated tab for tool
         ├─ Add scrollable container
         └─ Mount component panel
         │
         ▼
Tool Component Rendered in GUI
```

## View Components

### ConfigView

**Purpose**: System configuration management and status display

**Features**:
- Model configuration (text model, thinking model, embedding model)
- Agent identity settings (name, username)
- System information display
- Configuration validation
- Settings export functionality

**Layout**:
- Left panel: Model selection and configuration
- Right panel: Agent identity and system info
- Header: Quick access to validation and export

**Integration**:
- Reads from Config singleton
- Updates apply immediately to ai_core
- Displays current memory statistics
- Shows enabled tools count

### ControlsView

**Purpose**: Runtime control of system features and integrations

**Features**:
- Control panel with feature toggles
- Voice/TTS configuration
- External integration management (Discord, Twitch, YouTube)
- Real-time feature enable/disable
- Status indicators for active services

**Layout**:
- Left panel: Main control toggles (wider, fixed width)
- Right panel: Auxiliary controls (voice, integrations, stats)

**Control Panel Categories**:
- **Core Features**: Memory, cognitive loop, response limiting
- **Tools**: Individual tool enable/disable switches
- **Logging**: Selective logging categories
- **Integrations**: External service connections
- **Voice**: TTS settings and volume control

**Integration**:
- Direct binding to controls module
- Real-time tool lifecycle management
- Immediate effect on agent behavior

### ChatView

**Purpose**: Real-time conversation interface with the agent

**Features**:
- Conversation history display with color-coded messages
- Message type visualization (user, agent, system, tool, memory, etc.)
- Text input with multi-line support
- Send button and keyboard shortcuts
- Processing indicator
- Auto-scrolling to latest messages
- Conversation history persistence

**Message Types with Color Coding**:
- **USER**: User messages (green in dark themes)
- **AGENT**: Agent responses (purple accents)
- **SYSTEM**: System notifications (gray)
- **TOOL**: Tool execution results (yellow-green)
- **MEMORY**: Memory operations (yellow)
- **THINKING**: Internal thoughts (magenta)
- **ERROR**: Error messages (red)
- **DISCORD/TWITCH/YOUTUBE**: Chat platform messages (cyan)

**Layout**:
- Left panel: System log (all internal processing)
- Right panel: Chat display + input area
- Bottom: Input text area + send/stop buttons

**Input Features**:
- Shift+Enter: New line
- Enter: Send message
- Content filtering on input
- Empty message prevention
- Processing state indicators

### ToolsView

**Purpose**: Dynamic tool panel container with per-tool interfaces

**Features**:
- Automatic tool discovery from installed tools
- Individual tab per tool component
- Scrollable panel containers
- Tool component lifecycle management
- Refresh functionality
- Error handling for failed components

**Discovery Process**:
1. Scan `BASE/tools/installed/` directory
2. Check for `component.py` files
3. Load `information.json` metadata
4. Filter to tools with GUI components
5. Create dedicated tab for each tool

**Component Requirements**:
Tools must provide:
```python
def create_component(parent_gui, ai_core, logger):
    """
    Factory function to create GUI component
    
    Args:
        parent_gui: Main GUI instance
        ai_core: AI Core instance
        logger: Logger instance
    
    Returns:
        Component instance with create_panel() method
    """
    return ToolComponent(parent_gui, ai_core, logger)
```

**Tab Structure**:
- Icon + tool display name as tab label
- Scrollable content area
- Component panel mounted within container
- Automatic cleanup on view close

### InfoView

**Purpose**: Project documentation display

**Features**:
- README.md rendering with markdown formatting
- Syntax highlighting for code blocks
- Hyperlink styling
- Header formatting (H1, H2, H3)
- List formatting with bullets
- Refresh functionality
- Scrollable content

**Markdown Support**:
- Headers: `#`, `##`, `###`
- Bold: `**text**`
- Inline code: `` `code` ``
- Code blocks: ` ```language ```  `
- Lists: `- item` or `* item`
- Links: `[text](url)`

**Layout**:
- Header with title and refresh button
- Main text area with scrollbar
- File path display at bottom

## Theme System

The GUI supports three comprehensive themes with consistent styling across all components:

### DarkTheme (Default)

**Color Palette**:
- **Backgrounds**: Deep blacks (#141414, #1e1e1e, #2a2a2a)
- **Foregrounds**: Light grays (#d4d4d4, #9a9a9a, #6a6a6a)
- **Accents**: Purple (#8b5cf6), Green (#10b981), Blue (#3b82f6)
- **Borders**: Dark gray (#2a2a2a)

**Characteristics**:
- Modern, professional appearance
- Reduced eye strain in low light
- Purple accent for primary interactions
- Green accent for success/positive actions

### LightTheme

**Color Palette**:
- **Backgrounds**: Light grays (#f8f9fa, #e9ecef, #ffffff)
- **Foregrounds**: Dark grays (#212529, #6c757d, #adb5bd)
- **Accents**: Purple (#6f42c1), Green (#198754), Blue (#0d6efd)
- **Borders**: Light gray (#dee2e6)

**Characteristics**:
- Clean, professional appearance
- High contrast for bright environments
- Accessible color combinations
- Suitable for formal presentations

### CyberTheme

**Color Palette**:
- **Backgrounds**: Ultra-deep purples (#050008, #0a0015, #1a0a2e)
- **Foregrounds**: Neon green (#00ff88), Purple (#8a2be2)
- **Accents**: Neon green, Cyan (#00d4ff), Pink (#ff006e)
- **Borders**: Neon accents with glow effects

**Characteristics**:
- Cyberpunk/hacker aesthetic
- High-contrast neon colors
- Courier New monospace font
- Border emphasis and visual glow
- Distinctive, immersive appearance

### Theme Application

**Styled Elements**:
- Window background and borders
- All ttk widgets (buttons, frames, labels, checkboxes)
- Text widgets (chat, system log, input)
- Scrollbars (vertical and horizontal)
- Notebook tabs
- Menu/tab buttons
- LabelFrames (standard and accent variants)
- Comboboxes (theme selector)

**Dynamic Updates**:
When theme changes:
1. All ttk styles reconfigured
2. Text widget colors updated
3. Custom widgets refreshed
4. Menu recreated with new styling
5. Active tab highlighting updated
6. Color tags in text displays reconfigured

**Font Selection**:
- Light/Dark themes: Segoe UI (modern, readable)
- Cyber theme: Courier New (monospace, tech aesthetic)

## Message Processing

### Asynchronous Flow

All message processing happens asynchronously to keep the GUI responsive:

**User Input Path**:
1. User types in input text widget
2. ChatView validates and filters input
3. Message displayed immediately in chat
4. Background thread spawned for processing
5. AICore processes message
6. Response queued to message_queue
7. Main thread extracts from queue
8. Response displayed in chat
9. TTS triggered if enabled

**Autonomous Response Path**:
1. Cognitive loop generates autonomous response
2. Response sent via callback to GUI
3. Message queued to message_queue
4. Main thread extracts and displays
5. TTS triggered if enabled

**Processing Indicators**:
- "Processing..." label shown during message handling
- Send button disabled during processing
- Cleared on completion
- Error messages displayed for failures

### Thread Safety

**Queue-Based Updates**:
All GUI updates go through thread-safe queues:
- `message_queue`: Chat messages and system notifications
- `input_queue`: Voice input (if voice features enabled)

**Queue Processor**:
Runs in main thread at 100ms intervals:
```python
while not message_queue.empty():
    msg_type, sender, content = message_queue.get()
    if msg_type == "user":
        display_user_message(sender, content)
    elif msg_type == "agent":
        display_agent_message(sender, content)
    elif msg_type == "system":
        display_system_message(content)
    # ... handle other types
```

**TTS Management**:
- Speech played in background thread
- Stop event for interruption
- New speech cancels previous
- No blocking of GUI or message processing

## Voice Manager

Handles voice input and TTS configuration:

**Features**:
- TTS backend selection (XTTS, pyttsx3, etc.)
- Volume control with live updates
- Voice model selection (XTTS only)
- Microphone input support (when implemented)
- Real-time availability status

**TTS Integration**:
- Direct connection to ai_core.tts_tool
- Volume applied before speech
- Stop functionality for interruption
- Error handling with user feedback

**Panel Elements**:
- Backend selection dropdown
- Voice model selector (conditional)
- Volume slider (0-100%)
- Device display (XTTS)
- Status indicators

## Control Panel Manager

Manages feature toggles and configuration:

**Toggle Categories**:

**Core Features**:
- Memory System
- Cognitive Loop
- Chat Engagement
- Response Rate Limiting

**Tools**:
- Dynamically generated from discovered tools
- Individual enable/disable per tool
- Real-time lifecycle management
- Status indicators

**Logging**:
- System Information
- Tool Execution
- Response Processing
- Prompt Construction
- Chat Messages

**Integration Patterns**:
- Checkbox bound to config attribute
- OnChange callback updates config
- Config change triggers system update
- Status reflected immediately

## Dynamic Tool Panel System

Enables tools to provide custom GUI interfaces:

### Discovery Process

**Scan Phase**:
1. Check `BASE/tools/installed/` directory
2. For each tool directory:
   - Look for `component.py` file
   - Load `information.json` metadata
   - Extract display name, icon, category

**Loading Phase**:
1. Import component.py dynamically
2. Find `create_component()` factory function
3. Call factory with (parent_gui, ai_core, logger)
4. Store component instance

**Mounting Phase**:
1. Create dedicated tab for tool
2. Add scrollable container
3. Call `component.create_panel(parent)`
4. Mount returned frame in tab

### Component Interface

**Required Factory Function**:
```python
def create_component(parent_gui, ai_core, logger):
    """
    Create tool GUI component
    
    Args:
        parent_gui: Main GUI instance (OllamaGUI)
        ai_core: AI Core instance (for tool access)
        logger: Logger instance (for debugging)
    
    Returns:
        Component instance with:
        - create_panel(parent) method
        - Optional cleanup() method
    """
    return MyToolComponent(parent_gui, ai_core, logger)
```

**Required Component Method**:
```python
class MyToolComponent:
    def create_panel(self, parent):
        """
        Create GUI panel for this tool
        
        Args:
            parent: Tkinter parent frame
        
        Returns:
            Frame containing tool interface
        """
        frame = ttk.Frame(parent)
        # Build interface...
        return frame
    
    def cleanup(self):
        """Optional: Called when component unloaded"""
        pass
```

### Example Tool Component

```python
# BASE/tools/installed/my_tool/component.py

def create_component(parent_gui, ai_core, logger):
    return MyToolPanel(parent_gui, ai_core, logger)

class MyToolPanel:
    def __init__(self, parent_gui, ai_core, logger):
        self.parent_gui = parent_gui
        self.ai_core = ai_core
        self.logger = logger
        self.active = False
    
    def create_panel(self, parent):
        """Build the tool's GUI interface"""
        from tkinter import ttk
        
        frame = ttk.LabelFrame(
            parent,
            text="My Tool Controls",
            style="Dark.TLabelframe"
        )
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add controls...
        ttk.Button(
            frame,
            text="Execute Tool",
            command=self.execute_tool
        ).pack(pady=10)
        
        return frame
    
    def execute_tool(self):
        """Handle tool execution"""
        self.logger.tool("Executing my_tool via GUI")
        # Access tool through ai_core
        tool = self.ai_core.tool_manager._active_tools.get('my_tool')
        if tool:
            # Execute tool action...
            pass
    
    def cleanup(self):
        """Cleanup when panel closed"""
        self.logger.system("MyToolPanel cleanup")
```

## Session Files Panel

Manages temporary reference files for the agent:

**Features**:
- File upload with type filtering
- Display uploaded files with metadata
- Preview file contents
- Remove individual files
- Clear all files
- Automatic file parsing and indexing

**Supported File Types**:
- Python (.py)
- JavaScript/TypeScript (.js, .ts)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- C# (.cs)
- Go (.go)
- Rust (.rs)
- Markdown (.md)
- Text (.txt)
- JSON (.json)
- XML (.xml)

**File Display**:
- Type emoji icon
- Filename with extension
- File metadata (type, lines, sections, size)
- Remove button per file
- Color-coded by type

**Integration**:
- Files loaded into SessionFileManager
- Parsed into sections/functions
- Available to agent for reference
- Cleared when session ends

## Configuration Management

### Config Singleton

Single Config instance shared across entire GUI:

**Initialization**:
```python
self.config = Config()  # Create singleton
self.logger = Logger(config=self.config)  # Pass to logger
self.ai_core = AICore(config=self.config)  # Pass to ai_core
```

**Verification**:
All components verified to share same instance:
```python
assert id(gui.config) == id(gui.logger.config)
assert id(gui.config) == id(gui.ai_core.config)
```

**Benefits**:
- No configuration drift
- Immediate propagation of changes
- Single source of truth
- Thread-safe updates

### Settings Persistence

**Auto-save**:
- Config changes saved immediately
- Control toggles update config
- Theme selection persisted
- Window geometry saved

**Export**:
- JSON export of all settings
- Timestamped filename
- Human-readable format
- Import functionality (future)

## Error Handling

### User-Facing Errors

**Message Processing Errors**:
- Displayed in chat as ERROR type
- Red color coding
- Clear error description
- Logged to system log

**Tool Loading Errors**:
- Error panel in tool tab
- Description of failure
- Traceback in system log
- Graceful degradation

**File Upload Errors**:
- Dialog box with error details
- Validation before upload
- Size warnings for large files
- Type checking

### Internal Errors

**Exception Handling**:
- Try-catch around all async operations
- Traceback printed to console
- Error logged to system log
- GUI remains responsive

**Recovery Strategies**:
- Failed tool loads don't crash GUI
- Message processing errors isolated
- Theme errors revert to default
- Component failures show error panels

## Performance Optimizations

**Lazy Loading**:
- Tool components loaded on-demand
- View content created only when shown
- Large text operations batched

**Update Throttling**:
- Queue processor runs at 100ms intervals
- Text widget updates batched
- Scroll position maintained

**Memory Management**:
- Chat display limited to recent messages
- System log auto-trimmed at length limit
- Tool components cleaned up when unloaded
- Old message queue items discarded

**Thread Efficiency**:
- Single processing thread per message
- Queue-based inter-thread communication
- Background tasks properly cancelled
- No thread proliferation

## Extensibility

The GUI is designed for easy extension:

**Adding New Views**:
1. Create view class in `gui_*_view.py`
2. Add view frame to `create_main_frames()`
3. Add tab button to menu
4. Implement view creation method
5. Add to view switching logic

**Adding New Themes**:
1. Define theme class in `gui_themes.py`
2. Add to THEMES registry
3. Define all required color constants
4. Test with all views and components

**Adding Tool Panels**:
1. Create `component.py` in tool directory
2. Implement `create_component()` factory
3. Build panel interface
4. Tool auto-discovered on startup

**Custom Widgets**:
- Inherit from ttk or tk widgets
- Apply theme colors in constructor
- Support theme updates via config
- Register with theme manager if needed

## Keyboard Shortcuts

**Chat View**:
- **Enter**: Send message
- **Shift+Enter**: New line in input
- **Ctrl+L**: Clear chat display (future)

**Global**:
- **Tab Navigation**: Switch between views
- **Mousewheel**: Scroll in focused area

**Future Enhancements**:
- Configurable keyboard shortcuts
- Command palette (Ctrl+P style)
- Quick tool access shortcuts
- Search functionality

## Accessibility Features

**Color Accessibility**:
- High contrast ratios in all themes
- Color-blind friendly palettes
- Redundant visual indicators (not just color)

**Text Readability**:
- Adjustable font sizes (via theme)
- Clear font choices (Segoe UI, Courier New)
- Proper line spacing
- Word wrap in all text areas

**Keyboard Navigation**:
- Tab order for all controls
- Enter key for primary actions
- Escape for cancel operations
- Focus indicators on all interactive elements

The GUI system provides a professional, responsive, and extensible interface for interacting with the agentic framework, balancing sophistication with usability while maintaining clean separation from core agent logic.

---

## 🗄️ Session Management

### Session File System
The `SessionFileManager` handles temporary document context:
* **File Ingestion:** Loads text, PDFs, code files. Chunks large files for processing. Creates embeddings for semantic search.
* **Context Integration:** Searches files based on user queries, retrieves relevant sections dynamically, and injects file context into prompts. Supports line-range retrieval.
* **Lifecycle:** Files are loaded explicitly during the session, persist until manually cleared or the session ends, and do not pollute long-term memory. Optimized for development workflows.

---

## 💬 Chat Engagement System

### Multi-Platform Chat Integration
The `ChatHandler` manages live chat from multiple platforms:
* **Platform Support:** YouTube live chat, Twitch chat, Discord channels.
* **Unified message format** across platforms.

### Chat Engagement Logic
* **Message Buffering:** Maintains platform-specific message buffers and tracks metadata.
* **Engagement Decisions:**
    * **Critical:** Direct bot mentions $\to$ immediate response
    * **High:** Questions or multiple unengaged messages
    * **Medium:** Natural conversation after threshold messages
* Considers time since last engagement (cooldown).
* Chat messages are ingested as raw events and processed through the cognitive pipeline.

---

## ⚙️ Configuration System

### Singleton Architecture
`Config` and `Logger` use a singleton pattern to ensure consistent state and prevent configuration drift.

### Dynamic Control Variables
The `ControlManager` handles runtime feature toggles:
* **Control Categories:** Feature Flags, Logging Controls, Tool Controls.
* **Special Handling:**
    * **Continuous Thinking Toggle:** Starts/stops cognitive loop manager, preserves thought buffer state.
    * **Logging Control Toggle:** Updates `Config` singleton directly, changes take effect immediately.
    * **Tool Toggle:** Notifies tool manager of state change, starts/stops tool if supported.

---

## 🛡️ Content Filtering

### Centralized Filtering Architecture
All content filtering occurs at single entry/exit points:

* **Input Filtering (`AICore.process_user_message`):** Applied before any cognitive processing. Removes harmful patterns, spam, exploits, and normalizes empty messages.
* **Output Filtering (`AICore.process_user_message`):** Applied after response generation is complete. Removes emoji, filters inappropriate content, and cleans formatting artifacts.

> **Critical Design:** No filtering in intermediate stages. Response generators and thought processors work with clean, filtered data.

---

## 📝 Logging System

### Centralized Logging Controls
All logging decisions are made in the `Logger` singleton based on control variables in `Config`:
* `LOG_TOOL_EXECUTION`
* `LOG_PROMPT_CONSTRUCTION`
* `LOG_RESPONSE_PROCESSING`
* `LOG_SYSTEM_INFORMATION`
* `SHOW_CHAT`
* **Message Categorization:** Each log call is tagged with a `MessageType` which determines if the message logs.
* **Critical Feature:** Logger checks the `Config` singleton at log time, enabling real-time logging control without restart.

---

## 🔄 Data Flow Summary

### Typical Processing Flow
1.  **Input Arrives:** User message, chat activity, tool result, or timer event. Filtered through input filter and ingested into `ThoughtBuffer` as a raw event.
2.  **Cognitive Processing:** Cognitive loop detects pending event. `ThoughtProcessor` generates interpretation, which is added to the buffer with priority. Tool actions are identified and queued.
3.  **Tool Execution:** `ToolManager` validates and `ActionStateManager` registers. Tool executes asynchronously. Result is injected back into `ThoughtBuffer`.
4.  **Response Decision:** `ThoughtBuffer` evaluates accumulated state (priority, unspoken count, timing). If `should_speak` is `True`, proceeds to generation.
5.  **Response Generation:** `ResponseGenerator` synthesizes spoken output using the thought chain and memory context.
6.  **Output Processing:** Response is filtered through the output filter, added to `ThoughtBuffer` as a response echo, and routed to the TTS system.

---

## ✨ Key Design Principles
* **Separation of Concerns:** Thoughts are internal, responses are external. Memory retrieval/storage and tool execution/instruction are isolated.
* **Event-Driven Architecture:** Raw events trigger thought generation. Tool results feed back as events. Asynchronous execution.
* **State Immutability:** Thought buffer is append-only. Thoughts are never modified after creation, ensuring a clear audit trail.
* **Prompt Construction Philosophy:** Modular, context-aware, token budget management, and personality consistency.
* **Continuous Operation:** Processing happens as fast as hardware allows with natural pacing; rate limiting only for external outputs (speech).

---

## 🌐 Integration Points

| External System | Agent Interaction |
| :--- | :--- |
| **Text-to-Speech (TTS)** | Receives final response text. Agent marks response echo in buffer immediately. TTS plays asynchronously, non-blocking. |
| **GUI Interface** | Receives log callbacks. Updates control states via `ControlManager`. Loads session files via `SessionFileManager`. Displays statistics. |
| **Discord/Twitch/YouTube** | Chat messages flow through `ChatHandler` with a unified message format. Response routing handled by the integration layer. |

This system represents a sophisticated agentic architecture balancing continuous autonomous cognition with selective, natural communication—designed for coherent, context-aware AI assistants that think continuously but speak purposefully.