# Anna AI: Visual System Architecture

## System Overview

Anna AI is a sophisticated agentic AI system with continuous cognitive processing, four-tier memory, and autonomous goal management.

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   GUI    │  │  Voice   │  │   Chat   │  │  Games   │       │
│  │ (Tkinter)│  │  (STT)   │  │Platforms │  │Integration│       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
        ┌─────────────▼──────────────┐
        │      THOUGHT BUFFER        │
        │   (Event Aggregation)      │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   CONTINUOUS COGNITIVE     │
        │         LOOP               │
        │                            │
        │  ┌──────────────────────┐  │
        │  │ Should Process?      │  │
        │  │ • Critical → Yes     │  │
        │  │ • High → Evaluate    │  │
        │  │ • Medium → Accumulate│  │
        │  └──────────┬───────────┘  │
        └─────────────┼──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   STAGE 1: THINKING        │
        │   (NO Chat Context)        │
        │                            │
        │  • Process observations    │
        │  • Plan strategically      │
        │  • Execute tools           │
        │  • Update goals            │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   Should Speak?            │
        │   • Urgency threshold?     │
        │   • Goal achieved?         │
        │   • Chat engagement?       │
        │   • Time threshold?        │
        └─────────────┬──────────────┘
                      │
                 YES  │  NO
        ┌─────────────┼──────────────┐
        │             │              │
        ▼             ▼              │
┌───────────┐  ┌──────────┐         │
│  STAGE 2  │  │ Continue │         │
│ RESPONSE  │  │ Thinking │◄────────┘
│           │  └──────────┘
│ (WITH     │
│  Chat)    │
│           │
│ • Natural │
│   language│
│ • Personality
│ • Animation│
└─────┬─────┘
      │
      ▼
┌─────────────┐
│   OUTPUT    │
│ • TTS       │
│ • Chat      │
│ • Animation │
└─────────────┘
```

---

## Two-Stage Processing Pipeline

### Stage 1: Internal Thinking (Strategic)

```
INPUT EVENTS
├── User messages
├── Chat activity
├── Tool results
├── Game state
└── Reminders
     │
     ▼
CONTEXT ASSEMBLY (NO CHAT)
├── Tool state summary
├── Session files
├── Game context
├── Memory (Tiers 1-4)
├── Current goal
└── Pending actions
     │
     ▼
THINKING MODEL
├── Interpret events → thoughts
├── Update cognitive state
├── Generate/update goal
├── Plan tool actions
└── Execute tools (parallel)
     │
     ▼
OUTPUT: Internal State
├── Structured thoughts
├── Active goal
├── Tool action queue
└── Pending operations
```

### Stage 2: External Response (Communication)

```
INPUT FROM STAGE 1
├── Internal thoughts
├── Active goal
├── Tool results
└── Cognitive state
     │
     ▼
CONTEXT ASSEMBLY (WITH CHAT)
├── Stage 1 thoughts
├── Chat messages (NOW ADDED)
├── Memory context
├── Personality examples
└── Session context
     │
     ▼
RESPONSE MODEL
├── Synthesize natural language
├── Integrate personality
├── Reference chat naturally
├── Embed animations
└── Generate speech text
     │
     ▼
OUTPUT: Spoken Response
├── Natural language text
├── Animation commands
├── TTS audio
└── Chat platform replies
```

---

## Continuous Cognitive Loop

```
┌─────────────────────────────────────────────────────────┐
│               CONTINUOUS OPERATION CYCLE                │
└─────────────────────────────────────────────────────────┘

    START
      │
      ▼
┌──────────────────┐
│ 1. Check Events  │
│   • Queue empty? │
│   • New events?  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Events? │
    └────┬────┘
         │
    YES  │  NO (Proactive Mode)
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│ Process │ │ Generate         │
│ Event   │ │ Proactive        │
│         │ │ Thought          │
│ • User  │ │                  │
│   input │ │ Time since input:│
│ • Chat  │ │ < 6min → Reflect │
│ • Tools │ │ > 6min → Memory  │
│ • Game  │ │        → Planning│
└────┬────┘ └────┬─────────────┘
     │           │
     └─────┬─────┘
           │
           ▼
    ┌──────────────┐
    │ 2. Priority  │
    │   Assignment │
    │              │
    │ CRITICAL [!] │
    │ HIGH     [↑] │
    │ MEDIUM   [→] │
    │ LOW      [·] │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ 3. Should    │
    │    Process?  │
    │              │
    │ Critical → Y │
    │ High+wait→ Y │
    │ Accum → Y/N  │
    └──────┬───────┘
           │
       NO  │  YES
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌──────────────┐
│ Accumu-│  │ 4. STAGE 1   │
│  late  │  │    THINKING  │
│ Buffer │  │              │
└────┬───┘  │ • Interpret  │
     │      │ • Plan       │
     │      │ • Execute    │
     │      └──────┬───────┘
     │             │
     │             ▼
     │      ┌──────────────┐
     │      │ 5. Tool      │
     │      │    Execution │
     │      │              │
     │      │ Sync → Wait  │
     │      │ Async → BG   │
     │      └──────┬───────┘
     │             │
     │             ▼
     │      ┌──────────────┐
     │      │ 6. Should    │
     │      │    Speak?    │
     │      │              │
     │      │ Check:       │
     │      │ • Urgency    │
     │      │ • Threshold  │
     │      │ • Timing     │
     │      └──────┬───────┘
     │             │
     │         NO  │  YES
     │      ┌──────┴──────┐
     │      │             │
     └──────┼─────►       ▼
            │       ┌──────────────┐
            │       │ 7. STAGE 2   │
            │       │    RESPONSE  │
            │       │              │
            │       │ • Synthesize │
            │       │ • Personality│
            │       │ • Animation  │
            │       └──────┬───────┘
            │              │
            │              ▼
            │       ┌──────────────┐
            │       │ 8. Output    │
            │       │    & Memory  │
            │       │              │
            │       │ • Speak/Chat │
            │       │ • Save state │
            │       │ • Update mem │
            │       └──────┬───────┘
            │              │
            └──────────────┘
                   │
                   ▼
            ┌──────────────┐
            │ 9. Adaptive  │
            │    Pacing    │
            │              │
            │ High → 0.3s  │
            │ Med  → 0.5s  │
            │ Low  → 1.0s  │
            └──────┬───────┘
                   │
                   │
                   └──────► Back to Step 1
```

---

## Four-Tier Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY HIERARCHY                         │
└─────────────────────────────────────────────────────────────┘

TIER 1: SHORT-TERM MEMORY
┌─────────────────────────────────────────────────────────────┐
│ Last 25 Messages (Chronological Buffer)                     │
│                                                              │
│ Storage: short_memory.json                                  │
│ Access: Always included in context                          │
│ Format: Raw text (no embeddings)                            │
│                                                              │
│ [Recent] User: "Help with Python?"                          │
│ [Recent] Anna: "Sure! What do you need?"                    │
│ [Recent] User: "Decorators confuse me"                      │
│                                                              │
│ ─────────────── OVERFLOW (>25) ───────────────►            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
TIER 2: MEDIUM-TERM MEMORY
┌─────────────────────────────────────────────────────────────┐
│ Earlier Today (Semantic Search)                             │
│                                                              │
│ Storage: medium_memory.json                                 │
│ Access: Triggered by keywords/context                       │
│ Format: Text + 768-dim embeddings                           │
│                                                              │
│ Triggers: "earlier", "before", "you said"                   │
│                                                              │
│ [10:15 AM] User: "Can you help with Python?"                │
│            Embedding: [0.123, -0.456, ...]                  │
│            Similarity: 0.87 to current query                │
│                                                              │
│ ──────────── DATE ROLLOVER (Midnight) ─────────►           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
TIER 3: LONG-TERM MEMORY
┌─────────────────────────────────────────────────────────────┐
│ Past Days (Compressed Summaries)                            │
│                                                              │
│ Storage: long_memory.json                                   │
│ Access: Semantic search on summaries                        │
│ Format: Daily summaries + embeddings                        │
│                                                              │
│ Triggers: "yesterday", "remember", "last week"              │
│                                                              │
│ [2024-12-08] "Discussed Python decorators and list          │
│               comprehensions. User learning syntax.         │
│               Helped debug function issues."                │
│            Embedding: [0.234, -0.567, ...]                  │
│                                                              │
│ ──────────── PERMANENT STORAGE ─────────────►              │
└─────────────────────────────────────────────────────────────┘

TIER 4: BASE KNOWLEDGE
┌─────────────────────────────────────────────────────────────┐
│ Static Reference Material                                    │
│                                                              │
│ Storage: personality/base_memory/base_memories/*.json       │
│ Access: Semantic search with type filtering                 │
│ Format: Chunked documents + pre-computed embeddings         │
│                                                              │
│ Components:                                                  │
│                                                              │
│ ┌────────────────────────┐  ┌───────────────────────┐      │
│ │  PERSONALITY EXAMPLES  │  │   REFERENCE DOCS      │      │
│ ├────────────────────────┤  ├───────────────────────┤      │
│ │ • Thought patterns     │  │ • Technical guides    │      │
│ │ • Response styles      │  │ • API documentation   │      │
│ │ • Behavioral examples  │  │ • Code examples       │      │
│ │ • Tone & voice         │  │ • How-to instructions │      │
│ └────────────────────────┘  └───────────────────────┘      │
│                                                              │
│ Triggers: Stage-appropriate queries, "how to", "explain"    │
└─────────────────────────────────────────────────────────────┘
```

### Memory Search Flow

```
USER QUERY: "What did we discuss about Python earlier?"
     │
     ▼
┌────────────────────────────────────┐
│ Step 1: Search Tier 1 (Short)     │
│ Check last 25 messages             │
│ Result: Not found (too old)        │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Step 2: Search Tier 2 (Medium)    │
│                                    │
│ 1. Generate query embedding        │
│    [0.456, -0.234, 0.789, ...]    │
│                                    │
│ 2. Calculate cosine similarity     │
│    with all embeddings             │
│                                    │
│ 3. Filter by threshold (>0.3)      │
│                                    │
│ 4. Return top 3 matches            │
│    • Relevance: 0.87               │
│    • Relevance: 0.82               │
│    • Relevance: 0.76               │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Step 3: Format Results             │
│                                    │
│ ## EARLIER TODAY                   │
│                                    │
│ [10:15 AM] User: Can you help      │
│            with Python?             │
│ (relevance: 0.87)                  │
│                                    │
│ [10:20 AM] Anna: Of course!        │
│            What do you need?        │
│ (relevance: 0.82)                  │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Step 4: Inject into Prompt         │
│ Context includes retrieved memories│
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Step 5: Agent Response             │
│ "Earlier we talked about           │
│  decorators..."                    │
└────────────────────────────────────┘
```

---

## Tool System Architecture

### Tool Execution Flow

```
AI DECISION
"I need to search Wikipedia and show excitement"
     │
     ▼
┌────────────────────────────────────────────┐
│ TOOL SELECTOR                              │
│ Parse intent → structured actions          │
│                                            │
│ actions = [                                │
│   {tool: "wiki_search", args: ["Python"]},│
│   {tool: "animation", args: ["thinking"]} │
│ ]                                          │
└────────────┬───────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────┐
│ ACTION STATE MANAGER                       │
│ Register pending actions                   │
│                                            │
│ search_001: PENDING                        │
│ animation_002: PENDING                     │
└────────────┬───────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────┐
│ TOOL EXECUTOR (Route by Type)             │
└────────────┬───────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────────┐
│   SYNC   │  │    ASYNC     │
│  TOOLS   │  │    TOOLS     │
│          │  │              │
│Animation │  │Wiki Search   │
│Local Ops │  │Web Search    │
│          │  │Vision        │
│          │  │API Calls     │
└────┬─────┘  └──────┬───────┘
     │               │
     │ Execute       │ Launch
     │ immediately   │ background
     │               │ task
     ▼               │
┌──────────┐         │
│ Wait for │         │
│complete  │         │
└────┬─────┘         │
     │               │
     ▼               ▼
┌──────────┐  ┌──────────────┐
│ Result:  │  │ Status:      │
│ SUCCESS  │  │ IN_PROGRESS  │
└────┬─────┘  └──────┬───────┘
     │               │
     │               │ (5s later)
     │               │
     │               ▼
     │        ┌──────────────┐
     │        │ Result:      │
     │        │ SUCCESS      │
     │        │ (10 results) │
     │        └──────┬───────┘
     │               │
     └───────┬───────┘
             │
             ▼
┌────────────────────────────────────────────┐
│ RESULT INTEGRATION                         │
│                                            │
│ Inject back into thought stream:           │
│                                            │
│ "[SUCCESS] animation executed"             │
│ "[SUCCESS] wiki_search returned 10 results"│
│                                            │
│ Update action states → COMPLETED           │
└────────────┬───────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────┐
│ NEXT COGNITIVE CYCLE                       │
│ AI reads results and continues processing  │
└────────────────────────────────────────────┘
```

### Tool State Tracking

```
ACTION LIFECYCLE

PENDING
   │
   │ Tool executor starts execution
   ▼
IN_PROGRESS
   │
   ├─────► SUCCESS ──────► Results available
   │
   ├─────► FAILED ───────► Error message + retry guidance
   │
   ├─────► TIMEOUT ──────► Exceeded time limit
   │
   └─────► CANCELLED ────► Manually stopped

Each action tracked with:
{
  action_id: "search_abc123",
  tool_name: "wiki_search",
  args: ["Python decorators"],
  status: "IN_PROGRESS",
  initiated_at: 1234567890.123,
  attempt_number: 1,
  timeout: 15.0
}
```

---

## Chat Engagement System

```
MULTI-PLATFORM CHAT FLOW

┌──────────┐  ┌──────────┐  ┌──────────┐
│ Discord  │  │  Twitch  │  │ YouTube  │
│  Chat    │  │   Chat   │  │Live Chat │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ CHAT HANDLER    │
         │ (Normalization) │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ MESSAGE BUFFER          │
         │                         │
         │ Track per platform:     │
         │ • Author                │
         │ • Content               │
         │ • Timestamp             │
         │ • Mentions              │
         │ • Engagement status     │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ ENGAGEMENT ANALYZER     │
         │                         │
         │ Detect:                 │
         │ • Direct mentions       │
         │ • Questions             │
         │ • Conversation flow     │
         │ • Unengaged threshold   │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ PRIORITY ASSIGNMENT     │
         │                         │
         │ CRITICAL: @Anna mention │
         │ HIGH: "?" questions     │
         │ MEDIUM: Normal chat     │
         │ LOW: Background chatter │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ INJECT INTO             │
         │ THOUGHT BUFFER          │
         │                         │
         │ Becomes event for       │
         │ cognitive processing    │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ COGNITIVE PIPELINE      │
         │ Stage 1: Think about it │
         │ Stage 2: Respond        │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────────────┐
         │ RESPONSE ROUTING        │
         │                         │
         │ Send reply to:          │
         │ • Origin platform       │
         │ • TTS (if speaking)     │
         │ • Animation (if active) │
         └─────────────────────────┘

ENGAGEMENT DECISION LOGIC

Message arrives
     │
     ▼
Is direct mention? ──YES──► RESPOND IMMEDIATELY (urgency: 9)
     │
     NO
     ▼
Contains "?"  ──YES──► HIGH PRIORITY (urgency: 7)
     │
     NO
     ▼
Unengaged count > threshold? ──YES──► MEDIUM (urgency: 5)
     │
     NO
     ▼
Time since last > cooldown? ──YES──► MEDIUM (urgency: 4)
     │
     NO
     ▼
ACCUMULATE (urgency: 3)
```

---

## Goal Management System

```
GOAL LIFECYCLE

USER REQUEST
"Let me know when you find diamonds in Minecraft"
     │
     ▼
┌──────────────────────────────────────┐
│ STAGE 1: THINKING                    │
│ Parse request → Generate goal        │
│                                      │
│ Goal: "Monitor for diamond_ore"      │
│ Success criteria: Block detected     │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ GOAL STORAGE                         │
│                                      │
│ {                                    │
│   id: "goal_001",                    │
│   description: "Find diamonds",      │
│   status: "ACTIVE",                  │
│   created: timestamp,                │
│   success_criteria: [...]            │
│ }                                    │
└────────────┬─────────────────────────┘
             │
             │ (Continuous monitoring)
             ▼
┌──────────────────────────────────────┐
│ AUTONOMOUS MONITORING                │
│                                      │
│ Each cognitive cycle:                │
│ • Check game state                   │
│ • Compare vs goal criteria           │
│ • Track progress                     │
│                                      │
│ [Cycle 1] No diamonds yet            │
│ [Cycle 2] Still searching            │
│ [Cycle 3] Diamond detected!          │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ GOAL ACHIEVEMENT                     │
│                                      │
│ Criteria met → Mark COMPLETED        │
│ Generate high-priority thought       │
│                                      │
│ Thought: "Found diamonds at (45,12)!"│
│ Urgency: 8 (HIGH)                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ STAGE 2: RESPONSE                    │
│                                      │
│ Generate excited notification:       │
│ "Hey! [excited] I found diamonds at  │
│  coordinates (45, 12, -89)!"         │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ OUTPUT                               │
│ • TTS speaks notification            │
│ • Animation shows excitement         │
│ • Goal archived as completed         │
└──────────────────────────────────────┘
```

---

## Session File Management

```
FILE LOADING FLOW

User loads file: project_code.py
     │
     ▼
┌────────────────────────────────────┐
│ SESSION FILE MANAGER               │
│                                    │
│ 1. Detect file type                │
│    Extension: .py → Code file      │
│                                    │
│ 2. Extract sections                │
│    • Functions                     │
│    • Classes                       │
│    • Imports                       │
│                                    │
│ 3. Extract keywords                │
│    • Function names                │
│    • Class names                   │
│    • Key terms                     │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ SESSION STORAGE (Memory Only)      │
│                                    │
│ {                                  │
│   file_id: "file_001",             │
│   filepath: "project_code.py",     │
│   sections: [                      │
│     {                              │
│       type: "function",            │
│       name: "calculate_score",     │
│       content: "def calc...",      │
│       keywords: ["score", "calc"]  │
│     },                             │
│     ...                            │
│   ]                                │
│ }                                  │
└────────────┬───────────────────────┘
             │
             │
USER QUERY: "How does the scoring work?"
             │
             ▼
┌────────────────────────────────────┐
│ KEYWORD SEARCH                     │
│                                    │
│ Query keywords: ["scoring", "work"]│
│                                    │
│ Match against sections:            │
│ • "calculate_score" → 5 points     │
│ • Contains "score" → 3 points      │
│                                    │
│ Top result:                        │
│ def calculate_score(player):       │
│     return player.points * 10      │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ INJECT INTO PROMPT                 │
│                                    │
│ ## RELEVANT CODE                   │
│                                    │
│ From project_code.py:              │
│ ```python                          │
│ def calculate_score(player):       │
│     return player.points * 10      │
│ ```                                │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ AI RESPONSE                        │
│ "The scoring multiplies player     │
│  points by 10..."                  │
└────────────────────────────────────┘
```

---
