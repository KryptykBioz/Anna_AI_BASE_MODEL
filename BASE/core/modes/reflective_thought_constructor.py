# Filename: BASE/core/modes/reflective_thought_constructor.py
"""
Reflective Thought Mode Constructor
Handles memory reflection and connecting past to present
NOW: Includes startup context loading when thought count < 10
"""
from typing import List, Optional
from datetime import datetime, timedelta


class ReflectiveThoughtConstructor:
    """
    Constructs mode-specific sections for reflective thinking
    Connects past memories to current situation
    Handles startup context when agent first initializes
    """
    
    def __init__(self, memory_search=None, logger=None):
        """
        Initialize reflective thought constructor
        
        Args:
            memory_search: MemorySearch instance (optional)
            logger: Optional logger instance
        """
        self.memory_search = memory_search
        self.logger = logger
    
    def build_mode_instructions(self, is_startup: bool = False) -> str:
        """
        Build mode-specific instructions for reflective thinking
        
        Args:
            is_startup: Whether this is startup initialization
        
        Returns:
            Markdown-formatted instructions
        """
        if is_startup:
            return """## Startup Initialization Mode

You are waking up and orienting yourself after being offline.

### Your Task:
- Review the provided context from your recent past
- Orient yourself to what's been happening
- Generate ONE initial thought (15-50 words) about your current state
- Acknowledge what you remember and what you should focus on

### Guidelines:
- Think in your own voice and personality
- Be genuine about resuming after downtime
- Connect to recent memories naturally
- Set a positive, engaged tone"""
        
        return """## Reflective Thinking Mode

You are reflecting on past experiences and connecting them to your current situation.

### Your Task:
- Review the memory context provided
- Identify relevant patterns or lessons from the past
- Generate ONE reflective thought (15-50 words)
- Connect past experiences to present naturally

### Guidelines:
- Think in your own voice and personality
- Make genuine connections, not forced ones
- Be specific about what you remember and why it matters
- Sound thoughtful, not robotic"""
    
    def build_current_context(
        self,
        ongoing_context: str,
        query: Optional[str] = None,
        is_startup: bool = False,
        thought_count: int = 0
    ) -> str:
        """
        Build current context for reflective thinking
        
        Args:
            ongoing_context: Current situation description
            query: Optional query for memory search
            is_startup: Whether this is startup initialization
            thought_count: Number of thoughts agent currently has
        
        Returns:
            Markdown-formatted context
        """
        sections = []
        
        # STARTUP MODE: Load comprehensive context
        if is_startup or thought_count < 10:
            if self.logger:
                self.logger.system(
                    f"[Reflective Mode] Startup context (thoughts: {thought_count})"
                )
            
            startup_sections = self._build_startup_context()
            sections.extend(startup_sections)
        
        # STANDARD MODE: Current situation + targeted memories
        else:
            sections.append("## CURRENT SITUATION\n")
            sections.append(ongoing_context if ongoing_context else "Open time for reflection")
            
            # Memory context (if available)
            if self.memory_search and query:
                memory_sections = self._retrieve_memory_context(query)
                if memory_sections:
                    sections.append("\n## RELEVANT MEMORIES\n")
                    sections.append(memory_sections)
        
        return "\n".join(sections)
    
    def build_response_format(self, is_startup: bool = False) -> str:
        """
        Build expected response format for reflective thinking
        
        Args:
            is_startup: Whether this is startup initialization
        
        Returns:
            Markdown-formatted response format
        """
        if is_startup:
            return """## Expected Output Format
```xml
<think>Your initial orientation thought</think>
<action_list>[]</action_list>
```

### Rules:
- ONE startup thought (15-50 words)
- Acknowledge what you remember from context
- Set a positive, engaged tone
- Use your own voice and personality"""
        
        return """## Expected Output Format
```xml
<think>Your reflective thought connecting past to present</think>
<action_list>[]</action_list>
```

### Rules:
- ONE reflective thought (15-50 words)
- Connect past memories to current situation naturally
- Use your own voice and personality
- Be specific and insightful"""
    
    # ========================================================================
    # STARTUP CONTEXT BUILDING (Consolidated from thinking_modes.py)
    # ========================================================================
    
    def _build_startup_context(self) -> List[str]:
        """
        Build comprehensive startup context with recent memory + personality
        
        This ensures the agent starts with:
        1. Core identity knowledge (role/purpose) - WHO they are
        2. Personality examples (behavior) - HOW they think/act
        3. Long-term memory summaries (historical context) - PAST experiences
        4. Yesterday's context (temporal continuity) - RECENT past
        5. Recent conversation history (immediate context) - LAST session
        
        Returns:
            List of context sections to seed initial thoughts
        """
        context_sections = []
        
        if not self.memory_search:
            if self.logger:
                self.logger.warning("[Startup] No memory_search available")
            context_sections.append("## STARTUP\n\nNo memory context available.")
            return context_sections
        
        # ========================================================================
        # 1. Core identity knowledge (role/purpose) - FOUNDATION
        # ========================================================================
        identity_knowledge = self._load_identity_knowledge()
        if identity_knowledge:
            context_sections.append("## CORE IDENTITY")
            context_sections.append(identity_knowledge)
            if self.logger:
                self.logger.system("[Startup] Loaded identity knowledge")
        
        # ========================================================================
        # 2. Personality examples (behavior) - CHARACTER
        # ========================================================================
        personality_context = self._load_startup_personality()
        if personality_context:
            context_sections.append("\n## PERSONALITY & IDENTITY")
            context_sections.append(personality_context)
            if self.logger:
                self.logger.system("[Startup] Loaded personality examples")
        
        # ========================================================================
        # 3. Long-term memory summaries (historical context) - DISTANT PAST
        # ========================================================================
        startup_memories = self._load_startup_long_memories()
        if startup_memories:
            context_sections.append("\n## RECENT PAST")
            context_sections.append(startup_memories)
            if self.logger:
                self.logger.system("[Startup] Loaded recent long-term memories")
        
        # ========================================================================
        # 4. Yesterday's context (temporal continuity) - NEAR PAST
        # ========================================================================
        yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=5)
        if yesterday_ctx:
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            context_sections.append(f"\n## YESTERDAY ({yesterday_date})")
            context_sections.append(yesterday_ctx)
            if self.logger:
                self.logger.system("[Startup] Loaded yesterday's context")
        
        # ========================================================================
        # 5. Recent conversation history (immediate context) - MOST RECENT
        # ========================================================================
        recent_short_memory = self._load_recent_short_memory()
        if recent_short_memory:
            context_sections.append("\n## RECENT CONVERSATION HISTORY")
            context_sections.append(recent_short_memory)
            if self.logger:
                entry_count = len(recent_short_memory.split('\n'))
                self.logger.system(
                    f"[Startup] Loaded recent conversation ({entry_count} entries)"
                )
        
        # Log total context loaded
        if self.logger:
            total_length = sum(len(section) for section in context_sections)
            self.logger.system(
                f"[Startup] Built context: {len(context_sections)} sections, "
                f"{total_length} chars total"
            )
        
        return context_sections
    
    def _load_recent_short_memory(self, max_entries: int = 15) -> str:
        """
        Load most recent short-term memory entries
        
        Args:
            max_entries: Maximum number of recent entries to load
        
        Returns:
            Formatted string of recent conversation
        """
        if not self.memory_search:
            return ""
        
        memory_manager = self.memory_search.memory_manager
        recent_entries = memory_manager.short_memory[-max_entries:]
        
        if not recent_entries:
            return ""
        
        lines = []
        for entry in recent_entries:
            role = (
                memory_manager.username if entry['role'] == 'user' 
                else memory_manager.agentname
            )
            content = entry['content']
            lines.append(f"{role}: {content}")
        
        entry_count = len(lines)
        time_info = ""
        if recent_entries:
            last_timestamp = recent_entries[-1].get('timestamp', '')
            if last_timestamp:
                time_info = f" (last message: {last_timestamp})"
        
        header = f"Last {entry_count} messages from previous session{time_info}:"
        return header + "\n" + "\n".join(lines)
    
    def _load_startup_personality(self) -> str:
        """
        Load personality examples to establish agent identity
        
        Returns:
            Formatted string of personality examples
        """
        if not self.memory_search:
            return ""
        
        personality_query = "personality traits communication style behavior"
        
        examples = self.memory_search.search_personality_examples(
            query=personality_query,
            stage='thought',
            k=3,
            min_similarity=0.3
        )
        
        if not examples:
            return ""
        
        lines = []
        lines.append("You are an AI with a distinct personality. Here are examples of your behavior:")
        lines.append("")
        
        for i, ex in enumerate(examples, 1):
            text = ex['text']
            
            situation = ""
            cognition = ""
            
            for line in text.split('\n'):
                if 'SITUATION:' in line:
                    situation = line.split('SITUATION:', 1)[1].strip()
                elif 'INTERNAL COGNITION:' in line or 'THOUGHT:' in line:
                    delimiter = 'INTERNAL COGNITION:' if 'INTERNAL COGNITION:' in line else 'THOUGHT:'
                    cognition = line.split(delimiter, 1)[1].strip()
            
            if situation and cognition:
                lines.append(f"Example {i}:")
                lines.append(f"  Situation: {situation}")
                lines.append(f"  Your thought: {cognition}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _load_identity_knowledge(self) -> str:
        """
        Load base knowledge about agent identity and role
        
        Returns:
            Formatted string of identity knowledge
        """
        if not self.memory_search:
            return ""
        
        identity_query = "agent identity personality role purpose vtuber"
        
        base_results = self.memory_search.search_base_knowledge(
            identity_query,
            k=2,
            min_similarity=0.4
        )
        
        if not base_results:
            return ""
        
        lines = []
        for result in base_results:
            text = result['text']
            if len(text) > 300:
                text = text[:300] + "..."
            lines.append(text)
        
        return "\n".join(lines)
    
    def _load_startup_long_memories(self, max_summaries: int = 3) -> str:
        """
        Load recent long-term memory summaries
        
        Args:
            max_summaries: Maximum number of summaries to load
        
        Returns:
            Formatted string of memory summaries
        """
        if not self.memory_search:
            return ""
        
        memory_manager = self.memory_search.memory_manager
        recent_summaries = memory_manager.long_memory[-max_summaries:]
        
        if not recent_summaries:
            return ""
        
        lines = []
        for summary in recent_summaries:
            date = summary.get('date', 'Unknown date')
            summary_text = summary.get('summary', '')
            entry_count = summary.get('entry_count', 0)
            
            if summary_text:
                lines.append(f"[{date}] ({entry_count} messages): {summary_text}")
        
        return "\n".join(lines) if lines else ""
    
    # ========================================================================
    # STANDARD MEMORY RETRIEVAL (Non-startup)
    # ========================================================================
    
    def _retrieve_memory_context(self, query: str) -> str:
        """
        Retrieve relevant memories for reflection
        
        Args:
            query: Query string for memory search
        
        Returns:
            Formatted memory context
        """
        if not self.memory_search:
            return ""
        
        sections = []
        
        # Search long-term memory
        long_results = self.memory_search.search_long_memory(query, k=2)
        if long_results:
            sections.append("### Past Conversations")
            for r in long_results:
                date = r.get('date', 'Unknown')
                summary = r.get('summary', '')
                sections.append(f"- **[{date}]** {summary}")
        
        # Get yesterday's context
        yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=5)
        if yesterday_ctx:
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            sections.append(f"\n### Yesterday ({yesterday_date})")
            sections.append(yesterday_ctx)
        
        return "\n".join(sections) if sections else ""