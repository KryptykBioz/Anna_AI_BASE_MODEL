# Memory System Architecture

## Table of Contents
- [Overview](#overview)
- [Four-Tier Architecture](#four-tier-architecture)
- [Memory Flow](#memory-flow)
- [Memory Search System](#memory-search-system)
- [Enhanced Memory Retrieval](#enhanced-memory-retrieval)
- [Memory Integration](#memory-integration)
- [Session File Management](#session-file-management)
- [Memory Maintenance](#memory-maintenance)
- [Configuration](#configuration)
- [Performance](#performance)

---

## Overview

The memory system implements a **four-tier hierarchical architecture** that balances immediate context with long-term knowledge retention. This design optimizes for both recency (recent conversations) and relevance (semantic similarity to current context).

### Core Philosophy

1. **Hierarchical Storage**: Different tiers for different time horizons
2. **Semantic Retrieval**: Vector embeddings enable intelligent search
3. **Automatic Overflow**: Recent memories migrate to deeper tiers over time
4. **Combined Context**: User input + agent thoughts create richer queries
5. **Persistent Knowledge**: Static reference materials available always

### Key Components

```
MemoryManager       â†' Manages storage, overflow, and persistence
MemorySearch        â†' Semantic search across all tiers
MemoryIntegration   â†' Intelligent memory injection into prompts
SessionFileManager  â†' Temporary document context for sessions
Summarizer          â†' Compresses conversations into summaries
```

---

## Four-Tier Architecture

### Tier 1: Short-Term Memory

**Purpose**: Immediate conversation continuity

**Characteristics**:
- **Storage**: `personality/memory/short_memory.json`
- **Capacity**: Last 25 messages (configurable)
- **Embedding**: None (raw text)
- **Retrieval**: Chronological order
- **Always included**: Yes

**Data Structure**:
```json
[
  {
    "role": "user",
    "content": "What's the weather like?",
    "timestamp": "Monday, December 09, 2024 at 02:30:15 PM",
    "date": "2024-12-09"
  },
  {
    "role": "assistant",
    "content": "Let me check that for you.",
    "timestamp": "Monday, December 09, 2024 at 02:30:18 PM",
    "date": "2024-12-09"
  }
]
```

**Overflow Behavior**:
When the buffer exceeds 25 entries:
1. Oldest entry removed from Tier 1
2. Entry embedded using `nomic-embed-text`
3. Embedded entry moved to Tier 2 (Medium Memory)
4. Process repeats automatically

**Use Case**: Maintaining natural conversation flow without context loss.

---

### Tier 2: Medium-Term Memory

**Purpose**: Earlier messages from today

**Characteristics**:
- **Storage**: `personality/memory/medium_memory.json`
- **Capacity**: Unlimited (within session day)
- **Embedding**: Yes (768-dimensional vectors)
- **Retrieval**: Semantic similarity search
- **Included when**: Triggered by keywords or context

**Data Structure**:
```json
[
  {
    "role": "user",
    "content": "Can you help me with Python?",
    "timestamp": "Monday, December 09, 2024 at 10:15:32 AM",
    "date": "2024-12-09",
    "embedding": [0.123, -0.456, 0.789, ...]
  }
]
```

**Search Triggers**:
- Keywords: "earlier", "before", "you said"
- Implicit: When recent context suggests recall needed
- Manual: Direct memory queries

**Example**:
```
User Query: "What did we discuss about Python earlier?"
    â†"
Semantic Search: Generate embedding for query
    â†"
Cosine Similarity: Compare against all Tier 2 entries
    â†"
Top Results: Return 3 most relevant messages (threshold: 0.3)
    â†"
Context Injection: Format as "EARLIER TODAY" section
```

---

### Tier 3: Long-Term Memory

**Purpose**: Summaries of past days

**Characteristics**:
- **Storage**: `personality/memory/long_memory.json`
- **Capacity**: Unlimited (grows indefinitely)
- **Embedding**: Yes (on daily summaries)
- **Retrieval**: Semantic similarity search
- **Included when**: Historical context needed

**Data Structure**:
```json
[
  {
    "summary": "Discussed Python coding best practices. User learning about list comprehensions and decorators. Helped debug a function that wasn't returning expected values.",
    "date": "2024-12-08",
    "timestamp": "Monday, December 09, 2024 at 12:05:00 AM",
    "entry_count": 47,
    "embedding": [0.234, -0.567, 0.890, ...],
    "metadata": {
      "archived_from": "previous_day",
      "entry_type": "daily_summary"
    }
  }
]
```

**Search Triggers**:
- Keywords: "yesterday", "remember", "last week"
- Historical: "What did we talk about on Monday?"
- Pattern: Implicit connections to past topics

**Special Case: Yesterday's Detail**:
Yesterday's full conversation is preserved in Tier 2 (Medium Memory) until midnight rolls over. This provides full-detail access to recent past without requiring summarization.

**Summarization Process**:
1. At GUI startup, check for date rollover
2. For dates 2+ days old, generate summary via LLM
3. Embed summary using `nomic-embed-text`
4. Archive to Tier 3 with metadata
5. Remove source entries from Tier 1/2

**Summary Generation** (see `summarizer.py`):
```python
prompt = f"""Create a concise summary of this conversation from {date}.
Summarize from {agentname}'s perspective as a diary entry.
Focus on key topics, decisions, emotional context, preferences, and plans.

Conversation from {date} ({entry_count} messages):
{conversation}

Summary of {date}:"""
```

---

### Tier 4: Base Knowledge

**Purpose**: Static reference material and personality

**Characteristics**:
- **Storage**: `personality/base_memory/base_memories/*.json`
- **Capacity**: Unlimited (read-only)
- **Embedding**: Pre-computed during setup
- **Retrieval**: Semantic search with type filtering
- **Included when**: Domain-specific queries or personality needed

**Components**:

#### 1. Personality Examples
Two-stage personality system:

**Thought Examples** (`thought_examples/*.json`):
```json
{
  "source_file": "strategic_thinking_thought_examples.json",
  "processing_stage": "thought",
  "chunks": [
    {
      "text": "CONTEXT: User asks complex question\n\nRESPONSE: Break into steps. Check tools. Consider dependencies.\n\nKEYWORDS: planning, strategic, methodical",
      "metadata": {
        "type": "thought_example",
        "stage": "thought",
        "context": "User asks complex question",
        "response": "Break into steps...",
        "keywords": ["planning", "strategic"]
      },
      "embedding": [...]
    }
  ]
}
```

**Response Examples** (`response_examples/*.json`):
```json
{
  "source_file": "friendly_responses_response_examples.json",
  "processing_stage": "response",
  "chunks": [
    {
      "text": "CONTEXT: User greets agent\n\nRESPONSE: Hey there! How's it going?\n\nKEYWORDS: greeting, casual, warm",
      "metadata": {
        "type": "response_example",
        "stage": "response",
        "context": "User greets agent",
        "response": "Hey there!...",
        "keywords": ["greeting", "casual"]
      },
      "embedding": [...]
    }
  ]
}
```

**Creating Personality Files**:
```python
# personality/base_memory/base_personality/my_style.py

processing_stage = "response"  # or "thought"

system_prompt = "Description of personality aspect"

response_examples = [
    {
        "context": "Situation description",
        "response": "How agent responds",
        "keywords": ["relevant", "keywords"]
    }
]
```

**Generating Embeddings**:
```bash
cd BASE/memory
python embed_personality.py
```

#### 2. Reference Documents
Static guides, instructions, documentation:

**Document Structure**:
```json
{
  "source_file": "python_guide.txt",
  "total_chunks": 15,
  "chunks": [
    {
      "text": "Python list comprehensions provide concise syntax...",
      "embedding": [...],
      "metadata": {
        "type": "document",
        "source_file": "python_guide.txt",
        "chunk_id": 3
      }
    }
  ]
}
```

**Adding Documents**:
```bash
# 1. Place document in personality/base_memory/base_files/
cp my_guide.txt personality/base_memory/base_files/

# 2. Generate embeddings
cd BASE/memory
python embed_document.py

# 3. Embeddings saved to personality/base_memory/base_memories/
```

**Supported Formats**:
- Text: `.txt`, `.md`, `.log`
- Code: `.py`, `.js`, `.java`, `.cpp`, etc.
- Data: `.json`, `.xml`, `.yaml`, `.csv`

**Search Triggers**:
- Keywords: "how to", "guide", "explain", "what is"
- Domain: Technical terms or topics in query
- Personality: During response generation stage

---

## Memory Flow

### Lifecycle of a Message

```
1. USER INPUT
   "Can you help me with Python decorators?"
   â†"
2. SAVE TO TIER 1 (Short Memory)
   {role: "user", content: "...", timestamp: "..."}
   â†"
3. COGNITIVE PROCESSING
   Agent thinks about request
   â†"
4. AGENT RESPONSE
   "Sure! Decorators are functions that modify other functions..."
   â†"
5. SAVE TO TIER 1 (Short Memory)
   {role: "assistant", content: "...", timestamp: "..."}
   â†"
6. OVERFLOW CHECK
   If Tier 1 > 25 entries:
     - Embed oldest entry
     - Move to Tier 2
   â†"
7. DATE ROLLOVER (Next Day)
   If date changes:
     - Keep yesterday's entries in Tier 2
     - Previous days: Generate summary
     - Archive summary to Tier 3
   â†"
8. LONG-TERM STORAGE
   Daily summaries persist indefinitely in Tier 3
```

### Memory Retrieval Flow

```
1. USER QUERY
   "What did we discuss about Python earlier?"
   â†"
2. DETECT MEMORY NEED
   - Keywords: "earlier" detected
   - Context: Historical reference
   â†"
3. SEARCH TIER 1 (Short Memory)
   - Check last 25 messages
   - Result: Not found (too old)
   â†"
4. SEARCH TIER 2 (Medium Memory)
   - Generate query embedding
   - Cosine similarity search
   - Top 3 results (relevance > 0.3)
   â†"
5. FORMAT RESULTS
   ## EARLIER TODAY
   [10:15 AM] User: Can you help me with Python?
   (relevance: 0.87)
   â†"
6. INJECT INTO CONTEXT
   Prompt includes retrieved memories
   â†"
7. AGENT RESPONDS
   "Earlier we talked about decorators..."
```

---

## Memory Search System

### MemorySearch Class

Located in `BASE/memory/memory_search.py`, this class handles all semantic retrieval.

#### Core Methods

**1. Basic Search** (Backward Compatible):
```python
memory_search.search_base_knowledge(
    query="how to use decorators",
    k=5,
    min_similarity=0.3
)
```

**2. Enhanced Search** (Combined Context):
```python
memory_search.search_base_knowledge_combined(
    user_input="how to use decorators",
    recent_thoughts=[
        "User asked about Python",
        "I should explain decorators clearly",
        "Need to provide code examples"
    ],
    k=5,
    min_similarity=0.3,
    use_embedding_combination=True
)
```

#### Search Algorithm

**Embedding Generation**:
```python
# Single query
query_embedding = ollama.embed("how to use decorators")

# Combined query (user + thoughts)
combined_embedding = (
    0.6 * ollama.embed(user_input) +
    0.4 * avg(ollama.embed(thought) for thought in thoughts)
)
```

**Similarity Calculation**:
```python
# Vectorized cosine similarity
similarities = (embeddings @ query.T) / (norms * query_norm)

# Filter by threshold
valid = similarities >= min_similarity

# Return top-k
top_k = argpartition(similarities, k)[:k]
```

**Performance Optimizations**:
- **Pre-computed norms**: Document norms cached
- **Query cache**: LRU cache (1000 entries) for repeated queries
- **Vectorized ops**: NumPy for fast matrix operations
- **Argpartition**: O(n) vs O(n log n) for top-k selection

---

## Enhanced Memory Retrieval

### Combined Query Construction

The system creates richer semantic queries by combining user input with recent agent thoughts:

**Why This Works**:
```
User Input Only:
"What was that?"
â†' Vague, hard to match

User Input + Thoughts:
"What was that?" + 
["We discussed Python decorators",
 "User seemed confused about syntax",
 "I explained the @ symbol usage"]
â†' Rich context, better matches
```

**Implementation**:
```python
def build_combined_query(
    user_input: str,
    recent_thoughts: List[str],
    weight_user: float = 0.6,
    weight_thoughts: float = 0.4
) -> str:
    """Combines user input and thoughts with weighting"""
    
    query_parts = []
    
    # User input (higher weight - explicit)
    if user_input:
        repetitions = int(weight_user * 10)
        query_parts.extend([user_input] * repetitions)
    
    # Recent thoughts (lower weight - implicit)
    if recent_thoughts:
        repetitions = int(weight_thoughts * 10)
        for thought in recent_thoughts[-5:]:
            if len(thought) > 10:  # Skip trivial
                query_parts.extend([thought] * repetitions)
    
    # Combine and truncate
    combined = " ".join(query_parts)
    return combined[:500]  # Limit length
```

**Embedding Combination**:
```python
def build_combined_embedding(
    user_input: str,
    recent_thoughts: List[str]
) -> np.ndarray:
    """Creates weighted embedding from multiple sources"""
    
    embeddings = []
    weights = []
    
    # User input embedding
    if user_input:
        embeddings.append(embed(user_input))
        weights.append(0.6)
    
    # Average thought embeddings
    if recent_thoughts:
        thought_embeds = [embed(t) for t in recent_thoughts[-5:]]
        avg_thought = np.mean(thought_embeds, axis=0)
        embeddings.append(avg_thought)
        weights.append(0.4)
    
    # Weighted combination
    combined = sum(e * w for e, w in zip(embeddings, weights))
    
    # Normalize
    return combined / np.linalg.norm(combined)
```

### Personality Example Retrieval

**Stage-Specific Search**:
```python
# During thought processing
thought_examples = memory_search.search_personality_examples(
    query="User asked complex question",
    stage="thought",
    k=2,
    min_similarity=0.35
)

# During response generation
response_examples = memory_search.search_personality_examples(
    query="User greeted me",
    stage="response",
    k=2,
    min_similarity=0.35
)
```

**Formatted Output**:
```
## THOUGHT PROCESSING EXAMPLES

SITUATION: User asked complex question
THOUGHT: Break into steps. Check tools. Consider dependencies.

SITUATION: Multiple events need processing
THOUGHT: Prioritize by urgency. Address highest priority first.
```

---

## Memory Integration

### MemoryAwarePromptBuilder

Located in `BASE/memory/memory_integration.py`, this class intelligently injects memory into prompts.

#### Memory Relevance Detection

**Triggers Memory Search**:
```python
def detect_memory_needs(
    thoughts: List[str],
    context_parts: List[str],
    urgency_level: int
) -> MemoryRelevanceScore:
    """Analyzes if memory retrieval is needed"""
    
    score = MemoryRelevanceScore()
    
    # Always include recent context
    score.needs_short_memory = True
    
    # High urgency = skip memory for speed
    if urgency_level >= 9:
        return score
    
    # Check for memory triggers
    recent_text = " ".join(thoughts[-3:]).lower()
    
    if "remember" in recent_text or "recall" in recent_text:
        score.needs_medium_memory = True
        score.needs_long_memory = True
        score.query_hint = recent_text[-100:]
    
    if "yesterday" in recent_text:
        score.needs_yesterday = True
        score.query_hint = recent_text[-100:]
    
    if "how to" in recent_text or "guide" in recent_text:
        score.needs_base_knowledge = True
        score.query_hint = extract_reference_query(recent_text)
    
    return score
```

**MemoryRelevanceScore**:
```python
@dataclass
class MemoryRelevanceScore:
    needs_short_memory: bool = True
    needs_medium_memory: bool = False
    needs_long_memory: bool = False
    needs_base_knowledge: bool = False
    needs_yesterday: bool = False
    query_hint: str = ""
```

#### Context Building

**Conditional Memory Injection**:
```python
def build_memory_context(
    relevance: MemoryRelevanceScore
) -> str:
    """Builds memory context based on detected needs"""
    
    context_parts = []
    
    # Tier 1: Always included
    if relevance.needs_short_memory:
        short_mem = memory_search.get_short_memory()
        context_parts.append("## RECENT CONVERSATION")
        context_parts.append(short_mem)
    
    # Tier 1.5: Yesterday's detail
    if relevance.needs_yesterday:
        yesterday = memory_search.get_yesterday_context(max_entries=10)
        if yesterday:
            context_parts.append(f"\n## YESTERDAY ({date})")
            context_parts.append(yesterday)
    
    # Tier 2: Earlier today
    if relevance.needs_medium_memory and relevance.query_hint:
        medium_results = memory_search.search_medium_memory(
            relevance.query_hint, k=3
        )
        if medium_results:
            context_parts.append("\n## EARLIER TODAY")
            for r in medium_results:
                context_parts.append(
                    f"[{r['timestamp']}] {r['role']}: {r['content']}"
                )
    
    # Tier 3: Past days
    if relevance.needs_long_memory and relevance.query_hint:
        long_results = memory_search.search_long_memory(
            relevance.query_hint, k=2
        )
        if long_results:
            context_parts.append("\n## PAST DAYS")
            for r in long_results:
                context_parts.append(f"[{r['date']}] {r['summary']}")
    
    # Tier 4: Base knowledge
    if relevance.needs_base_knowledge and relevance.query_hint:
        base_results = memory_search.search_base_knowledge(
            relevance.query_hint, k=3, min_similarity=0.4
        )
        
        # Separate personality from documents
        personality = [r for r in base_results 
                      if r['metadata']['type'] in 
                      ['conversation_example', 'system_prompt']]
        documents = [r for r in base_results if r not in personality]
        
        if personality:
            context_parts.append("\n## PERSONALITY KNOWLEDGE")
            for r in personality:
                context_parts.append(r['text'])
        
        if documents:
            context_parts.append("\n## REFERENCE GUIDES")
            for r in documents:
                context_parts.append(f"From {r['source']}:")
                context_parts.append(r['text'])
    
    return "\n".join(context_parts)
```

**Example Output**:
```
## RECENT CONVERSATION
User: Can you help me with Python decorators?
Assistant: Sure! Decorators are functions that modify other functions.

## EARLIER TODAY
[10:15 AM] User: Can you help me with Python?
(relevance: 0.87)

## REFERENCE GUIDES
From python_guide.txt:
Python decorators use the @ syntax. Example:
@decorator
def function():
    pass
```

---

## Session File Management

### SessionFileManager

Located in `BASE/memory/session_file_manager.py`, handles temporary document context.

#### File Loading

**Supported File Types**:
```python
SUPPORTED_EXTENSIONS = {
    '.txt', '.md', '.rst',           # Documents
    '.py', '.js', '.java', '.cpp',   # Code
    '.json', '.xml', '.yaml',        # Data
    '.log', '.csv'                   # Logs
}
```

**File Processing**:
```python
def add_file(filepath: str, content: str) -> Dict:
    """Add document to session memory"""
    
    # Auto-detect file type
    file_type = detect_file_type(filepath, content)
    
    # Extract sections based on type
    if file_type == 'code':
        sections = extract_code_sections(content)
    elif file_type == 'markdown':
        sections = extract_markdown_sections(content)
    else:
        sections = extract_generic_sections(content)
    
    # Extract keywords from each section
    for section in sections:
        section['keywords'] = extract_keywords(section['content'])
    
    # Store in memory (no persistence)
    file_data = {
        'filepath': filepath,
        'file_type': file_type,
        'content': content,
        'sections': sections,
        'keywords': list(set(all_keywords)),
        'added_at': datetime.now().isoformat()
    }
    
    session_files[file_id] = file_data
    return file_data
```

#### Code Section Extraction

**Python Example**:
```python
def extract_code_sections(content: str) -> List[Dict]:
    """Extract functions and classes from Python code"""
    
    sections = []
    
    for i, line in enumerate(content.split('\n')):
        # Detect function/class definition
        if re.match(r'^(def |class |async def )', line.lstrip()):
            match = re.match(r'^(def |class )(\w+)', line.lstrip())
            section_type = 'class' if 'class' in match.group(1) else 'function'
            
            # Track indentation to find section end
            indent_level = len(line) - len(line.lstrip())
            section_lines = [line]
            
            # Continue until indentation decreases
            for j in range(i+1, len(lines)):
                next_line = lines[j]
                if next_line.strip():
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent_level:
                        break
                section_lines.append(next_line)
            
            sections.append({
                'type': section_type,
                'name': match.group(2),
                'content': '\n'.join(section_lines),
                'line_start': i + 1,
                'line_end': j
            })
    
    return sections
```

#### Keyword Search

**Fast Retrieval Without Embeddings**:
```python
def search(query: str, file_id: Optional[str] = None, top_k: int = 5):
    """Search for relevant sections using keyword matching"""
    
    query_keywords = extract_keywords(query.lower())
    results = []
    
    for fid, file_data in session_files.items():
        if file_id and fid != file_id:
            continue
        
        for section in file_data['sections']:
            # Keyword overlap score
            section_keywords = set(section['keywords'])
            keyword_overlap = len(query_keywords & section_keywords)
            
            # Direct text match bonus
            text_match = sum(
                1 for kw in query_keywords 
                if kw in section['content'].lower()
            )
            
            score = keyword_overlap * 2 + text_match
            
            if score > 0:
                results.append({
                    'file_id': fid,
                    'filename': file_data['filename'],
                    'section_name': section['name'],
                    'content': section['content'],
                    'score': score
                })
    
    # Sort by score, return top-k
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]
```

#### Context Generation

**For AI Queries**:
```python
def get_context_for_query(query: str, max_lines: int = 200) -> str:
    """Generate formatted context for AI consumption"""
    
    if not query:
        # No query = list available files
        return format_file_summaries()
    
    # Search for relevant sections
    results = search(query, top_k=10)
    
    if not results:
        # No matches = list available files
        return format_file_summaries()
    
    # Format relevant results
    context_lines = ["## RELEVANT CODE/DOCUMENTATION"]
    total_lines = 0
    
    for result in results:
        context_lines.append(
            f"\n### {result['filename']} - {result['section_name']}"
        )
        context_lines.append(
            f"*Lines {result['line_start']}-{result['line_end']} "
            f"(relevance: {result['score']})*"
        )
        context_lines.append("```")
        
        # Add content (respecting line limit)
        section_lines = result['content'].split('\n')
        lines_to_add = min(len(section_lines), max_lines - total_lines)
        context_lines.extend(section_lines[:lines_to_add])
        context_lines.append("```")
        
        total_lines += lines_to_add
        if total_lines >= max_lines:
            context_lines.append("\n*[Additional content truncated]*")
            break
    
    return "\n".join(context_lines)
```

---

## Memory Maintenance

### Daily Summarization

**Process** (see `BASE/memory/summarizer.py`):

1. **Trigger**: GUI startup detects date rollover
2. **Collection**: Gather all entries from previous date
3. **Generation**: LLM creates diary-style summary
4. **Embedding**: Generate vector for summary
5. **Archive**: Store in Tier 3 with metadata
6. **Cleanup**: Remove source entries from Tier 1/2

**Summarization Prompt**:
```
Create a concise summary of this full day's conversation between 
{username} and {agentname} that took place on {date}.

Summarize in first person from {agentname}'s perspective, creating 
a diary entry reflecting on that day.

Focus on:
- Key topics discussed
- Important information shared
- Decisions made
- Emotional context
- Personal preferences revealed
- Ongoing plans or commitments

Write in complete sentences with a reflective tone.

Conversation from {date} ({entry_count} messages):
{conversation}

Summary of {date}:
```

**Example Summary**:
```
Today I helped User learn about Python decorators. We started with 
basic @ syntax and moved into practical examples. User seemed to 
grasp the concept well after seeing the logging decorator example. 
Later, we discussed their upcoming project deadline and agreed to 
focus on code review tomorrow. The conversation had a productive 
tone, and User appreciated the step-by-step explanations.
```

### Memory Operations

**Clear Today's Memory** (GUI button):
```python
memory_manager.clear_today_memory()
# Removes all Tier 1 and Tier 2 entries
# Preserves Tier 3 (long-term) and Tier 4 (base)
```

**Clear All Personal Memory**:
```python
memory_manager.clear_memory()
# Removes Tier 1, 2, 3
# Preserves Tier 4 (base knowledge)
```

**Reload Base Knowledge** (GUI button):
```python
memory_manager.reload_base_knowledge()
# Re-scans personality/base_memory/base_memories/
# Loads new personality files or documents
```

### Statistics

**Memory Stats**:
```python
stats = memory_manager.get_stats()
# {
#   'short_memory_entries': 18,
#   'medium_memory_entries': 42,
#   'long_memory_summaries': 7,
#   'base_knowledge_chunks': 156,
#   'base_personality_chunks': 89,
#   'base_document_chunks': 67,
#   'total_interactions': 65,
#   'current_date': '2024-12-09'
# }
```

**Base Knowledge Breakdown**:
```python
breakdown = memory_manager.get_base_knowledge_breakdown()
# {
#   'total_chunks': 156,
#   'by_source': {
#     'friendly_responses_response_examples.json': 34,
#     'strategic_thinking_thought_examples.json': 28,
#     'python_guide_embeddings.json': 67
#   },
#   'by_type': {
#     'personality': 89,
#     'document': 67
#   }
# }
```

---

## Configuration

### Memory Controls

**In `personality/controls.py`**:
```python
# Memory System
SAVE_MEMORY = True                  # Enable memory persistence
USE_SHORT_MEMORY = True             # Tier 1 (always keep True)
USE_MEDIUM_MEMORY = True            # Tier 2 (today's earlier)
USE_LONG_MEMORY = True              # Tier 3 (past days)
USE_BASE_MEMORY = True              # Tier 4 (static knowledge)

# Memory Limits
SHORT_MEMORY_LIMIT = 25             # Max Tier 1 entries before overflow
MAX_CONTEXT_ENTRIES = 50            # Max entries in any context section
```

### Embedding Model

**In `personality/agent_info.py`**:
```python
embed_model = "nomic-embed-text"    # Ollama embedding model
```

**Model Requirements**:
```bash
# Install embedding model
ollama pull nomic-embed-text

# Verify installation
ollama list | grep nomic-embed-text

# Test embedding generation
curl http://localhost:11434/api/embeddings \
  -d '{"model":"nomic-embed-text","prompt":"test"}'
```
