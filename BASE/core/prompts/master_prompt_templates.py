# Filename: BASE/core/prompts/master_prompt_templates.py
"""
Master Prompt Templates
Defines the general format structure for ALL prompts
"""


class MasterPromptTemplates:
    """
    Master templates defining the general structure
    All prompts follow this format hierarchy
    """
    
    @staticmethod
    def get_general_structure() -> str:
        """
        General prompt structure (markdown format)
        Used by all prompt types
        """
        return """# PERSONALITY

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

{response_format}"""
    
    @staticmethod
    def assemble_prompt(
        personality: str,
        thought_chain: str,
        mode_instructions: str,
        current_context: str,
        response_format: str
    ) -> str:
        """
        Assemble complete prompt from components
        
        Args:
            personality: Complete personality description
            thought_chain: Formatted thought chain
            mode_instructions: Mode-specific instructions
            current_context: Current situational context
            response_format: Expected response format
        
        Returns:
            Complete assembled prompt
        """
        template = MasterPromptTemplates.get_general_structure()
        
        return template.format(
            personality=personality,
            thought_chain=thought_chain,
            mode_instructions=mode_instructions,
            current_context=current_context,
            response_format=response_format
        )
    
    @staticmethod
    def get_compact_structure() -> str:
        """
        Compact structure for high-urgency prompts
        Minimal sections for speed
        """
        return """# PERSONALITY

{personality}

---

# RECENT THOUGHTS

{thought_chain}

---

# INSTRUCTIONS

{mode_instructions}

---

# RESPOND

{response_format}"""
    
    @staticmethod
    def assemble_compact_prompt(
        personality: str,
        thought_chain: str,
        mode_instructions: str,
        response_format: str
    ) -> str:
        """
        Assemble compact prompt (no context section)
        
        Args:
            personality: Complete personality description
            thought_chain: Formatted thought chain (compact)
            mode_instructions: Mode-specific instructions
            response_format: Expected response format
        
        Returns:
            Complete compact prompt
        """
        template = MasterPromptTemplates.get_compact_structure()
        
        return template.format(
            personality=personality,
            thought_chain=thought_chain,
            mode_instructions=mode_instructions,
            response_format=response_format
        )