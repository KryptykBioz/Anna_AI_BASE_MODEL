# Agentic AI System Architecture

## 💡 Overview
This is a sophisticated agentic AI system built on Ollama that implements a two-stage cognitive architecture separating internal thinking from external communication. The agent maintains continuous autonomous thought, manages multiple memory tiers, executes tools dynamically, and generates natural spoken responses.

---

## 🏗️ Core Architecture

### Two-Stage Processing Pipeline
The system fundamentally separates cognition into two independent pathways:

#### Stage 1: Thought Processing (Internal Cognition)
* **Purpose:** Generate internal thoughts, process observations, plan actions
* **Model:** Fast thinking model optimized for rapid cognitive processing
* **Output:** Structured thoughts with priority levels, strategic plans, tool actions
* **Runs:** Continuously in background, independent of user interaction

#### Stage 2: Response Generation (External Communication)
* **Purpose:** Synthesize natural spoken responses for TTS/chat output
* **Model:** Response model optimized for natural language generation
* **Output:** Conversational text designed for speech synthesis
* **Runs:** Only when agent decides to speak based on thought accumulation

> **Critical Design Principle:** Thoughts $\ne$ Responses. The agent thinks continuously but speaks selectively based on accumulated cognitive state.

---

## 🧠 Cognitive Loop System

### Continuous Thinking Architecture
The agent operates in a true continuous thinking mode where cognitive processing never pauses:

#### Cognitive Loop Manager
* Manages background autonomous thinking that runs independently
* Processes thoughts as fast as possible (50-200ms intervals when active)
* No delays after response generation - thinking continues immediately
* Only response generation is rate-limited (separately from thinking)

### Thinking Modes
The system determines thinking mode based on time since last user input:

| Mode | Trigger | Focus / Action |
| :--- | :--- | :--- |
| **Standard Mode** | `< 6 minutes since user input` | **Reactive:** Processes incoming events immediately. **Proactive:** Reflects on recent context when no events pending. Focuses on immediate tasks. |
| **Memory Reflection Mode** | `6+ minutes without input` | Retrieves and reflects on past experiences. Searches long-term memory for relevant context. Triggered by memory-related keywords in thought stream. |
| **Future Planning Mode** | `6+ minutes without input, alternates with memory` | Anticipates future needs and actions. Plans ahead based on patterns and goals. Considers what user might need next. |

### Thought Buffer
The `ThoughtBuffer` is the central cognitive state manager:

#### Two Parallel Buffers
* **Raw Events Queue:** Unprocessed incoming observations
* **Processed Thoughts:** Interpreted cognitions with priority and metadata

#### Priority System
Thoughts are tagged with string-based priorities:
* `[CRITICAL]`: Direct mentions, urgent reminders, safety issues
* `[HIGH]`: User input, direct questions, tool failures
* `[MEDIUM]`: Chat messages, tool results, observations
* `[LOW]`: Ambient events, internal reflections, response echoes

#### Decision Logic
**When to Generate Thoughts:**
* Always processes pending raw events immediately (reactive)
* Generates proactive thoughts when no reactive work pending
* Never blocks - thinking happens as fast as possible

**When to Speak:**
* Critical priority thoughts trigger immediate response
* High priority thoughts with user waiting (8+ seconds)
* Accumulated observations (5+ unspoken thoughts + 30s since last response)
* Chat engagement triggers (unengaged messages meeting thresholds)
* Natural conversation flow (context-dependent timing)

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

## ⚙️ Prompt Construction System

### Unified Prompt Architecture
All prompts follow a consistent structure via the `MasterPromptConstructor`:
1.  **Personality** (Who the agent is)
2.  **Thought Chain** (Recent internal thoughts)
3.  **Mode Instructions** (What to do now)
4.  **Current Context** (Events, data, observations)
5.  **Response Format** (How to structure output)

### Modular Prompt Components
* **Personality Injection:** Centralized definition of core identity and style. Injected consistently across all prompt types, with stage-specific variants.
* **Thought Chain Formatting:** Formats recent thoughts for context continuity. Includes timestamps and source attribution. Filters out noise (response echoes, artifacts).
* **Context Detection:** Analyzes conversation data to detect active contexts (search results, tool data, vision observations, chat activity). Adjusts prompt sections based on detected contexts to prevent irrelevant instruction bloat.

---

## 🛠️ Tool System

### Dynamic Tool Discovery
The system automatically discovers and registers tools at initialization:

#### Tool Registration Process
* Scans `BASE/tools/installed/` directory
* Reads `information.json` from each tool
* Dynamically creates control variables in `personality.controls`
* Registers metadata in config registry
* Makes tools available via `ToolManager`

#### Tool Metadata Structure
Each tool provides: name, display name, control variable name, category, description, usage examples, timeout, cooldown settings, and available commands.

### Tool Execution Flow

#### Action State Management
The `ActionStateManager` tracks all tool executions:
* Registers each tool call with a unique action ID.
* Tracks status: `PENDING` $\to$ `IN_PROGRESS` $\to$ `COMPLETED/FAILED`.
* Records timestamps, results, errors, and retry attempts.
* Provides awareness of pending actions to the thought processor.

#### Tool Manager
The `ToolManager` orchestrates all tool operations:
* Loads tool classes dynamically from the filesystem.
* Manages the tool lifecycle (initialization, startup, shutdown).
* Executes structured actions from the thought processor.
* Provides tool instructions to the prompt builder.
* Handles persistence of tool-specific instructions.

#### Instruction Persistence
* Tools can request persistent instructions via special actions.
* Instructions are stored across sessions in JSON.
* Automatically injected into prompts when the tool is enabled.
* **Instruction Types:** **Persistent** (survive across sessions) and **Session** (last only for current session).

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