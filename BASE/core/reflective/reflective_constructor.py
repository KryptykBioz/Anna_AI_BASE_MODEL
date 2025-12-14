# Filename: BASE/core/reflective/reflective_constructor.py
"""
Reflective Thinking Prompt Constructor - FIXED
===============================================
Constructs prompts for memory-based reflection and self-awareness.

FIX: Now properly retrieves and includes tool instructions from persistence manager

Prompt Components:
1. Personality (core identity + reflective style)
2. Thought chain (recent thoughts for continuity)
3. Memory context (retrieved memories to reflect on)
4. Tool list OR retrieved tool instructions (based on persistence)
5. Response guidance (how to reflect)

Focus: Looking backward, connecting past to present
"""

from typing import List, Optional
from datetime import datetime, timedelta
from BASE.core.reflective.reflective_parts import ReflectivePromptParts
from personality.prompts.personality_prompt_parts import PersonalityPromptParts


class ReflectiveConstructor:
    """Constructs prompts for reflective thinking"""
    
    STARTUP_THOUGHT_THRESHOLD = 3  # First 3 thoughts use startup context
    
    def __init__(self, memory_search=None, tool_manager=None, logger=None):
        """
        Initialize reflective constructor
        
        Args:
            memory_search: MemorySearch instance for memory retrieval
            tool_manager: ToolManager instance for tool instructions
            logger: Optional logger instance
        """
        self.memory_search = memory_search
        self.tool_manager = tool_manager
        self.logger = logger
        
        # Initialize prompt parts
        self.parts = ReflectivePromptParts()
        self.personality = PersonalityPromptParts()
    
    def build_reflective_prompt(
        self,
        thought_chain: List[str],
        ongoing_context: str,
        query: Optional[str] = None,
        is_startup: bool = False
    ) -> str:
        """
        Build complete reflective thinking prompt
        
        AUTOMATIC STARTUP: Detects thought_count < 3 and loads startup context
        
        Args:
            thought_chain: Recent thoughts (for continuity)
            ongoing_context: Current situation description
            query: Optional query for memory search
            is_startup: Whether this is startup mode (manual override)
        
        Returns:
            Complete reflective thinking prompt
        """
        # Detect startup based on thought count
        thought_count = len(thought_chain)
        is_actually_startup = is_startup or thought_count < self.STARTUP_THOUGHT_THRESHOLD
        
        if is_actually_startup and self.logger:
            self.logger.system(
                f"[Reflective Prompt] STARTUP MODE "
                f"(thought {thought_count + 1}/{self.STARTUP_THOUGHT_THRESHOLD})"
            )
        
        sections = []
        
        # 1. Personality injection
        sections.append(self.personality.get_personality_injection('thought'))
        
        # 2. Recent thoughts (if any)
        if thought_chain:
            sections.append(self._format_thought_chain(thought_chain))
        
        # 3. Mode instructions
        if is_actually_startup:
            sections.append(self.parts.get_startup_instructions())
        else:
            sections.append(self.parts.get_mode_instructions())
        
        # 4. Tool instructions (FIXED: Check persistence and include detailed instructions)
        if self.tool_manager:
            tool_section = self._get_tool_instructions_section()
            if tool_section:
                sections.append(tool_section)
        
        # 5. Context (startup or standard)
        if is_actually_startup:
            sections.append(self._build_startup_context())
        else:
            sections.append(self._build_standard_context(ongoing_context, query))
        
        # 6. Output format
        sections.append(self.parts.get_output_format(is_startup=is_actually_startup))
        
        prompt = "\n".join(sections)
        
        if self.logger:
            mode = "Startup" if is_actually_startup else "Standard"
            self.logger.prompt(f"[Reflective Thinking Prompt - {mode}]\n{prompt}")
        
        return prompt
    
    def _format_thought_chain(self, thoughts: List[str]) -> str:
        """Format recent thoughts"""
        recent = thoughts[-5:]
        formatted = "\n".join([f"- {t}" for t in recent])
        return f"\n## YOUR RECENT THOUGHTS\n\n{formatted}"
    
    def _get_tool_instructions_section(self) -> str:
        """
        Get tool instructions section - FIXED
        Checks instruction persistence and includes detailed instructions when available
        
        Returns:
            Tool section (either minimal list or detailed instructions)
        """
        if not self.tool_manager:
            return ""
        
        # Check if instruction persistence manager exists
        if not hasattr(self.tool_manager, 'instruction_persistence_manager'):
            # Fallback to minimal list
            return self.tool_manager._build_tool_list()
        
        persistence_manager = self.tool_manager.instruction_persistence_manager
        
        # Get tools with active instructions
        tools_with_instructions = persistence_manager.get_active_tool_names()
        
        if not tools_with_instructions:
            # No active instructions - return minimal tool list
            return self.tool_manager._build_tool_list()
        
        # Build detailed instructions for tools with active retrievals
        return self._build_detailed_tool_instructions(tools_with_instructions)
    
    def _build_detailed_tool_instructions(self, tool_names: List[str]) -> str:
        """
        Build detailed instructions for tools with active retrievals
        
        Args:
            tool_names: List of tools with active instruction persistence
        
        Returns:
            Formatted detailed tool instructions
        """
        # Import the instruction builder
        from BASE.handlers.tool_instruction_builder import ToolInstructionBuilder
        
        # Create builder instance
        builder = ToolInstructionBuilder(
            tool_manager=self.tool_manager,
            logger=self.logger
        )
        
        # Build detailed instructions
        detailed_instructions = builder.build_retrieved_tool_instructions(tool_names)
        
        if self.logger:
            self.logger.system(
                f"[Reflective Constructor] Including detailed instructions for "
                f"{len(tool_names)} tools: {', '.join(tool_names)}"
            )
        
        return detailed_instructions
    
    def _build_startup_context(self) -> str:
        """
        Build comprehensive startup context
        
        Loads:
        1. Core identity knowledge
        2. Personality examples
        3. Long-term memory summaries
        4. Yesterday's context
        5. Recent conversation history
        """
        if not self.memory_search:
            return "\n## STARTUP\n\nNo memory context available."
        
        sections = []
        
        # 1. Core identity
        identity = self._load_identity_knowledge()
        if identity:
            sections.append("## CORE IDENTITY")
            sections.append(identity)
        
        # 2. Personality examples
        personality = self._load_startup_personality()
        if personality:
            sections.append("\n## PERSONALITY & IDENTITY")
            sections.append(personality)
        
        # 3. Long-term summaries
        summaries = self._load_startup_long_memories()
        if summaries:
            sections.append("\n## RECENT PAST")
            sections.append(summaries)
        
        # 4. Yesterday's context
        yesterday = self.memory_search.get_yesterday_context(max_entries=5)
        if yesterday:
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            sections.append(f"\n## YESTERDAY ({yesterday_date})")
            sections.append(yesterday)
        
        # 5. Recent conversation
        recent = self._load_recent_short_memory()
        if recent:
            sections.append("\n## RECENT CONVERSATION HISTORY")
            sections.append(recent)
        
        return "\n".join(sections) if sections else "\n## STARTUP\n\nNo context available."
    
    def _build_standard_context(self, ongoing_context: str, query: Optional[str]) -> str:
        """Build standard reflective context with memory search"""
        sections = []
        
        sections.append("## CURRENT SITUATION\n")
        sections.append(ongoing_context if ongoing_context else "Open time for reflection")
        
        if self.memory_search and query:
            memory_ctx = self._retrieve_memory_context(query)
            if memory_ctx:
                sections.append("\n## RELEVANT MEMORIES\n")
                sections.append(memory_ctx)
        
        return "\n".join(sections)
    
    def _load_identity_knowledge(self) -> str:
        """Load core identity knowledge"""
        if not self.memory_search:
            return ""
        
        identity_query = "agent identity personality role purpose vtuber"
        results = self.memory_search.search_base_knowledge(
            identity_query, k=2, min_similarity=0.4
        )
        
        if not results:
            return ""
        
        lines = []
        for result in results:
            text = result['text']
            if len(text) > 300:
                text = text[:300] + "..."
            lines.append(text)
        
        return "\n".join(lines)
    
    def _load_startup_personality(self) -> str:
        """Load personality examples"""
        if not self.memory_search:
            return ""
        
        personality_query = "personality traits communication style behavior"
        examples = self.memory_search.search_personality_examples(
            query=personality_query, stage='thought', k=3, min_similarity=0.3
        )
        
        if not examples:
            return ""
        
        lines = ["You are an AI with a distinct personality. Here are examples of your behavior:", ""]
        
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
    
    def _load_startup_long_memories(self, max_summaries: int = 3) -> str:
        """Load recent long-term memory summaries"""
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
    
    def _load_recent_short_memory(self, max_entries: int = 15) -> str:
        """Load most recent short-term memory"""
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
    
    def _retrieve_memory_context(self, query: str) -> str:
        """Retrieve relevant memories for reflection"""
        if not self.memory_search:
            return ""
        
        sections = []
        
        # Long-term memory
        long_results = self.memory_search.search_long_memory(query, k=2)
        if long_results:
            sections.append("### Past Conversations")
            for r in long_results:
                date = r.get('date', 'Unknown')
                summary = r.get('summary', '')
                sections.append(f"- **[{date}]** {summary}")
        
        # Yesterday's context
        yesterday_ctx = self.memory_search.get_yesterday_context(max_entries=5)
        if yesterday_ctx:
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            sections.append(f"\n### Yesterday ({yesterday_date})")
            sections.append(yesterday_ctx)
        
        return "\n".join(sections) if sections else ""