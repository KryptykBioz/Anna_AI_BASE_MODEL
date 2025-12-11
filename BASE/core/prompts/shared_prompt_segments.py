# Filename: BASE/core/prompts/shared_prompt_segments.py
"""
SHARED PROMPT SEGMENTS - REFACTORED
Generic utilities only - no personality or mode-specific content
"""
from dataclasses import dataclass


@dataclass
class PromptSegment:
    """Single prompt component with metadata"""
    content: str
    priority: int
    token_estimate: int
    category: str


class SharedPromptSegments:
    """Generic grounding rules and universal utilities"""
    
    @staticmethod
    def get_grounding_rules() -> PromptSegment:
        """Universal grounding rules - prevents hallucination"""
        return PromptSegment(
            content="""## GROUNDING RULES

- Only reference data explicitly provided
- NO invention of details, events, or states
- If uncertain, acknowledge limitation
- Prioritize accuracy over completeness""",
            priority=1,
            token_estimate=40,
            category='core'
        )
    
    @staticmethod
    def get_tool_state_grounding() -> str:
        """Tool status grounding rules - prevents hallucination about tool execution"""
        return """## CRITICAL TOOL STATE GROUNDING

Tool status events are FACTUAL SYSTEM STATE. You MUST NOT invent or assume.

### STATUS TYPES

1. **"Initiated X"** = Command SENT, NOT completed
2. **"FAILED: X"** = Confirmed error
3. **"TIMEOUT: X"** = No response
4. **"X result: ..."** = SUCCESSFUL completion

### STRICT RULES

- NEVER say "I searched" if you only see "Initiated search"
- NEVER describe results you don't have
- ALWAYS distinguish "started" vs "completed"
- ALWAYS acknowledge failures explicitly"""
    
    @staticmethod
    def get_vision_grounding_enhancement() -> str:
        """Enhanced grounding for vision data"""
        return """## CRITICAL VISION GROUNDING

Vision data contains FACTUAL OBSERVATIONS ONLY.

- Accept vision descriptions AS-IS
- Do NOT elaborate beyond what vision states
- Do NOT invent details not mentioned
- ACKNOWLEDGE, don't INTERPRET"""