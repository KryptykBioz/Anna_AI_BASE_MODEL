# Filename: BASE/core/utils/thought_chain_formatter.py
"""
Unified Thought Chain Formatter
Centralizes thought chain formatting for all prompt types
"""
from typing import List, Optional
from personality.bot_info import username, agentname


class ThoughtChainFormatter:
    """
    Formats thought chains consistently across all modes
    Single source of truth for thought chain presentation
    """
    
    @staticmethod
    def format_thought_chain(
        thoughts: List[str],
        max_thoughts: int = 10,
        include_responses: bool = True
    ) -> str:
        """
        Format thought chain with separation of internal thoughts and spoken responses
        
        Args:
            thoughts: List of thought strings (may include response echoes)
            max_thoughts: Maximum number of thoughts to include
            include_responses: Whether to include response echoes
        
        Returns:
            Formatted markdown string
        """
        if not thoughts:
            return "## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
        
        # Separate internal thoughts from response echoes
        internal_thoughts = []
        response_echoes = []
        
        for thought in thoughts[-max_thoughts:]:
            if not thought or not isinstance(thought, str):
                continue
            
            # Clean artifacts
            if (thought.startswith('<thought about') or 
                thought.startswith('<think>') or
                thought.strip().startswith('{"tool":')):
                continue
            
            # Identify response echoes
            if any(phrase in thought for phrase in [
                "I just said", "I just asked", "I just acknowledged",
                "I just shared", "I just responded", "I just told"
            ]):
                response_echoes.append(thought)
            else:
                internal_thoughts.append(thought)
        
        # Build formatted output
        sections = []
        
        if internal_thoughts:
            sections.append("## YOUR RECENT THOUGHTS\n")
            for thought in internal_thoughts:
                sections.append(f"- {thought}")
        
        if response_echoes and include_responses:
            sections.append("\n## WHAT YOU RECENTLY SAID\n")
            for echo in response_echoes[-3:]:  # Last 3 responses only
                sections.append(f"- {echo}")
        
        return "\n".join(sections) if sections else "## YOUR RECENT THOUGHTS\n\nNo recent thoughts."
    
    @staticmethod
    def format_compact_chain(thoughts: List[str], max_thoughts: int = 5) -> str:
        """
        Compact thought chain for high-urgency prompts
        
        Args:
            thoughts: List of thought strings
            max_thoughts: Maximum thoughts to include
        
        Returns:
            Compact formatted string
        """
        if not thoughts:
            return "## RECENT THOUGHTS\n\nNone"
        
        # Filter clean thoughts only
        clean_thoughts = []
        for thought in thoughts[-max_thoughts:]:
            if not thought or not isinstance(thought, str):
                continue
            if thought.startswith('<') or thought.strip().startswith('{'):
                continue
            clean_thoughts.append(thought)
        
        if not clean_thoughts:
            return "## RECENT THOUGHTS\n\nNone"
        
        return "## RECENT THOUGHTS\n\n" + "\n".join([f"- {t}" for t in clean_thoughts])
    
    @staticmethod
    def extract_last_user_input(thoughts: List[str]) -> Optional[str]:
        """
        Extract last user input from thought chain
        
        Args:
            thoughts: List of thought strings
        
        Returns:
            Last user input or None
        """
        for thought in reversed(thoughts):
            if not isinstance(thought, str):
                continue
            
            if f"{username} said:" in thought:
                # Extract message after "said:"
                parts = thought.split(f"{username} said:", 1)
                if len(parts) == 2:
                    return parts[1].strip()
        
        return None
    
    @staticmethod
    def create_response_echo(spoken_text: str) -> str:
        """
        Create response echo for thought chain
        
        Args:
            spoken_text: What the agent just said
        
        Returns:
            Echo thought string
        """
        # Truncate if too long
        if len(spoken_text) > 150:
            spoken_text = spoken_text[:147] + "..."
        
        return f"I just said: \"{spoken_text}\""