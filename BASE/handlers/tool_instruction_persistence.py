# Filename: BASE/handlers/tool_instruction_persistence.py
"""
Tool Instruction Persistence Manager
Tracks which tools have active instruction retrievals with 6-minute timers
Provides flags for prompt builders to include instructions dynamically
"""
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class InstructionPersistence:
    """Tracks instruction persistence for a single tool"""
    tool_name: str
    retrieval_timestamp: float
    timeout_duration: float = 360.0  # 6 minutes
    
    def is_valid(self) -> bool:
        """Check if instruction retrieval is still valid"""
        elapsed = time.time() - self.retrieval_timestamp
        return elapsed < self.timeout_duration
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds"""
        elapsed = time.time() - self.retrieval_timestamp
        remaining = self.timeout_duration - elapsed
        return max(0.0, remaining)
    
    def reset_timer(self):
        """Reset the timer (when instructions re-requested)"""
        self.retrieval_timestamp = time.time()


class ToolInstructionPersistenceManager:
    """
    Manages instruction persistence flags for all tools
    Automatically creates flags for enabled tools
    Tracks 6-minute timers for instruction validity
    """
    
    def __init__(self, logger=None):
        """
        Initialize persistence manager
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        
        # Active instruction persistence by tool name
        self._active_instructions: Dict[str, InstructionPersistence] = {}
        
        # Instruction timeout: 6 minutes
        self._timeout_duration = 360.0
    
    # ========================================================================
    # CORE PERSISTENCE OPERATIONS
    # ========================================================================
    
    def mark_instructions_retrieved(self, tool_name: str) -> bool:
        """
        Mark that instructions were retrieved for a tool
        If already exists, resets the 6-minute timer
        
        Args:
            tool_name: Name of tool
            
        Returns:
            True if this was a refresh (timer reset), False if new
        """
        was_refresh = tool_name in self._active_instructions
        
        if was_refresh:
            # Reset existing timer
            self._active_instructions[tool_name].reset_timer()
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Timer reset: {tool_name} "
                    f"(6 minutes from now)"
                )
        else:
            # Create new persistence entry
            self._active_instructions[tool_name] = InstructionPersistence(
                tool_name=tool_name,
                retrieval_timestamp=time.time(),
                timeout_duration=self._timeout_duration
            )
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Instructions activated: {tool_name} "
                    f"(valid for 6 minutes)"
                )
        
        return was_refresh
    
    def has_active_instructions(self, tool_name: str) -> bool:
        """
        Check if tool has active (non-expired) instructions
        Automatically cleans up expired entries
        
        Args:
            tool_name: Name of tool
            
        Returns:
            True if instructions are active and valid
        """
        if tool_name not in self._active_instructions:
            return False
        
        persistence = self._active_instructions[tool_name]
        
        if not persistence.is_valid():
            # Expired - remove from tracking
            del self._active_instructions[tool_name]
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Instructions expired: {tool_name}"
                )
            
            return False
        
        return True
    
    def get_active_tool_names(self) -> List[str]:
        """
        Get list of all tools with active instructions
        Automatically cleans up expired entries
        
        Returns:
            List of tool names with valid instructions
        """
        # Clean up expired entries first
        expired = [
            name for name, persistence in self._active_instructions.items()
            if not persistence.is_valid()
        ]
        
        for name in expired:
            del self._active_instructions[name]
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Auto-expired: {name}"
                )
        
        return list(self._active_instructions.keys())
    
    def clear_instructions(self, tool_name: str):
        """
        Manually clear instruction persistence for a tool
        (Optional - normally instructions expire naturally)
        
        Args:
            tool_name: Name of tool
        """
        if tool_name in self._active_instructions:
            del self._active_instructions[tool_name]
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Manually cleared: {tool_name}"
                )
    
    def clear_all_instructions(self):
        """Clear all instruction persistence (e.g., on system reset)"""
        count = len(self._active_instructions)
        self._active_instructions.clear()
        
        if self.logger and count > 0:
            self.logger.system(
                f"[Instruction Persistence] Cleared {count} active instruction(s)"
            )
    
    # ========================================================================
    # STATUS AND MONITORING
    # ========================================================================
    
    def get_time_remaining(self, tool_name: str) -> Optional[float]:
        """
        Get time remaining before instructions expire
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Seconds remaining, or None if no active instructions
        """
        if tool_name not in self._active_instructions:
            return None
        
        persistence = self._active_instructions[tool_name]
        return persistence.time_remaining()
    
    def get_all_status(self) -> Dict[str, Dict]:
        """
        Get status of all active instructions
        Useful for debugging and monitoring
        
        Returns:
            Dict mapping tool_name to status info
        """
        status = {}
        
        for tool_name, persistence in self._active_instructions.items():
            remaining = persistence.time_remaining()
            elapsed = time.time() - persistence.retrieval_timestamp
            
            status[tool_name] = {
                'retrieved_at': persistence.retrieval_timestamp,
                'elapsed_seconds': elapsed,
                'remaining_seconds': remaining,
                'remaining_minutes': remaining / 60.0,
                'is_valid': persistence.is_valid()
            }
        
        return status
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of active instructions
        
        Returns:
            Summary string
        """
        active = self.get_active_tool_names()
        
        if not active:
            return "No active instruction retrievals"
        
        lines = [f"{len(active)} tool(s) with active instructions:"]
        
        for tool_name in sorted(active):
            remaining = self.get_time_remaining(tool_name)
            if remaining:
                minutes = remaining / 60.0
                lines.append(f"  - {tool_name}: {minutes:.1f} minutes remaining")
        
        return "\n".join(lines)
    
    # ========================================================================
    # INTEGRATION HELPERS
    # ========================================================================
    
    def should_include_in_prompt(self, tool_name: str) -> bool:
        """
        Check if tool instructions should be included in next prompt
        This is the main method prompt builders should use
        
        Args:
            tool_name: Name of tool
            
        Returns:
            True if instructions should be included
        """
        return self.has_active_instructions(tool_name)
    
    def get_tools_for_prompt(self, available_tools: List[str]) -> List[str]:
        """
        Filter available tools to only those with active instructions
        Used by prompt builders to determine which tools to include
        
        Args:
            available_tools: List of all available tool names
            
        Returns:
            Filtered list of tools that should be in prompt
        """
        active = self.get_active_tool_names()
        
        # Return intersection of available and active
        return [tool for tool in available_tools if tool in active]
    
    def update_from_retrieval_request(
        self, 
        requested_tools: List[str],
        available_tools: List[str]
    ) -> tuple[List[str], List[str]]:
        """
        Process instruction retrieval requests and update persistence
        
        Args:
            requested_tools: List of tool names user requested instructions for
            available_tools: List of currently available tool names
            
        Returns:
            Tuple of (valid_requests, invalid_requests)
        """
        valid = []
        invalid = []
        
        for tool_name in requested_tools:
            if tool_name in available_tools:
                # Valid request - mark instructions as retrieved
                self.mark_instructions_retrieved(tool_name)
                valid.append(tool_name)
            else:
                # Invalid request - tool not available
                invalid.append(tool_name)
        
        return valid, invalid
    
    # ========================================================================
    # CLEANUP AND MAINTENANCE
    # ========================================================================
    
    def cleanup_expired(self) -> int:
        """
        Manually cleanup expired instructions
        (Usually called automatically, but can be called explicitly)
        
        Returns:
            Number of expired entries removed
        """
        expired = [
            name for name, persistence in self._active_instructions.items()
            if not persistence.is_valid()
        ]
        
        for name in expired:
            del self._active_instructions[name]
        
        if expired and self.logger:
            self.logger.system(
                f"[Instruction Persistence] Cleaned up {len(expired)} expired entries"
            )
        
        return len(expired)
    
    
    def clear_instructions_for_disabled_tools(self, enabled_tools: List[str]):
        """
        Clear instruction persistence for tools that are no longer enabled
        Called by tool manager when tools are disabled
        
        Args:
            enabled_tools: List of currently enabled tool names
        """
        active_tools = list(self._active_instructions.keys())
        
        disabled_active = [
            tool for tool in active_tools
            if tool not in enabled_tools
        ]
        
        if disabled_active:
            for tool_name in disabled_active:
                del self._active_instructions[tool_name]
                
                if self.logger:
                    self.logger.system(
                        f"[Instruction Persistence] Auto-cleared instructions for disabled tool: {tool_name}"
                    )
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Persistence] Cleared {len(disabled_active)} disabled tool(s) "
                    f"from active instructions"
                )
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about instruction persistence
        
        Returns:
            Dict with statistics
        """
        active = self.get_active_tool_names()
        all_status = self.get_all_status()
        
        avg_remaining = 0.0
        if active:
            avg_remaining = sum(
                status['remaining_seconds'] for status in all_status.values()
            ) / len(active)
        
        return {
            'active_count': len(active),
            'active_tools': sorted(active),
            'avg_time_remaining_seconds': avg_remaining,
            'avg_time_remaining_minutes': avg_remaining / 60.0,
            'timeout_duration_minutes': self._timeout_duration / 60.0
        }