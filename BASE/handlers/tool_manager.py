# Filename: BASE/handlers/tool_manager.py
"""
Tool Manager - Main Coordination and Execution
Handles tool instruction persistence and action execution
Works with ToolLifecycleManager for discovery and lifecycle operations
"""
from typing import List, Dict, Any, Optional
import asyncio
import time
from pathlib import Path

from BASE.handlers.tool_lifecycle import ToolLifecycleManager


class ToolManager:
    """
    Main tool manager coordinating instruction persistence and execution
    Uses ToolLifecycleManager for discovery and lifecycle operations
    """
    
    def __init__(self, config, controls_module, action_state_manager, project_root, logger=None):
        """Initialize tool manager with instruction tracking"""
        self.config = config
        self.controls = controls_module
        self.action_state_manager = action_state_manager
        self.project_root = project_root
        self.logger = logger
        
        # Active tool instances (shared with lifecycle manager)
        self._active_tools: Dict[str, Any] = {}
        
        # Lifecycle manager handles discovery and lifecycle
        self.lifecycle_manager = ToolLifecycleManager(
            project_root=project_root,
            logger=logger
        )
        self.lifecycle_manager.set_active_tools(self._active_tools)
        
        # Tool metadata cache (populated by lifecycle manager)
        self._tool_metadata: Dict[str, Dict] = {}
        
        # Event loop and thought buffer
        self._event_loop = None
        self._thought_buffer = None
        
        # Instruction persistence tracking
        self._retrieved_instructions: Dict[str, float] = {}  # tool_name -> timestamp
        self._instruction_timeout: float = 360.0  # 6 minutes
        
        # Pending tool instructions for next prompt
        self.pending_tool_instructions = None
        
        # Persistence manager (injected by core_initializer)
        self.instruction_persistence_manager = None
        
        # Discover available tools
        self._tool_metadata = self.lifecycle_manager.discover_tools()
        
        if self.logger:
            self.logger.system(
                f"[Tool Manager] Initialized with {len(self._tool_metadata)} tools"
            )
    
    # ========================================================================
    # SETUP AND CONFIGURATION
    # ========================================================================
    
    def set_event_loop(self, event_loop):
        """Set event loop for async operations"""
        self._event_loop = event_loop
        self.lifecycle_manager.set_event_loop(event_loop)
        
        if self.logger:
            self.logger.system("[Tool Manager] Event loop set")
    
    def set_thought_buffer(self, thought_buffer):
        """Set thought buffer for tool context injection"""
        self._thought_buffer = thought_buffer
        self.lifecycle_manager.set_thought_buffer(thought_buffer)
        
        if self.logger:
            self.logger.system("[Tool Manager] Thought buffer set")
    
    # ========================================================================
    # TOOL METADATA ACCESS
    # ========================================================================
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict]:
        """Get complete metadata for a specific tool"""
        return self.lifecycle_manager.get_tool_metadata(tool_name)
    
    def get_enabled_tool_names(self) -> List[str]:
        """Get list of currently enabled tool names"""
        return list(self._active_tools.keys())
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if tool is currently enabled (running)"""
        return tool_name in self._active_tools
    
    def get_tool_count(self) -> Dict[str, int]:
        """Get count of enabled vs total tools"""
        return {
            'enabled': len(self._active_tools),
            'total': len(self._tool_metadata)
        }
    
    def get_all_tool_info(self) -> List[Dict]:
        """Get info for all discovered tools (for GUI generation)"""
        return list(self._tool_metadata.values())
    
    # ========================================================================
    # TOOL LIFECYCLE CONTROL
    # ========================================================================
    
    def handle_control_update(self, control_name: str, value: bool):
        """
        Handle control variable changes from GUI
        Starts or stops tools based on control variable changes
        
        Args:
            control_name: Name of control variable (e.g., 'USE_WARUDO_ANIMATION')
            value: New value (True = enable, False = disable)
        """
        # Find which tool this control belongs to
        tool_name = None
        for name, metadata in self._tool_metadata.items():
            if metadata['control_variable'] == control_name:
                tool_name = name
                break
        
        if not tool_name:
            # Not a tool control - ignore
            return
        
        # Log the change
        if self.logger:
            action = "ENABLING" if value else "DISABLING"
            self.logger.system(
                f"[Tool Manager] {action} tool: {tool_name} "
                f"(control: {control_name})"
            )
        
        if value:
            # Tool being ENABLED - start it
            if self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.lifecycle_manager.start_tool(
                        tool_name, 
                        self.config, 
                        self.controls
                    ),
                    self._event_loop
                )
            else:
                if self.logger:
                    self.logger.warning(
                        f"[Tool Manager] Cannot start {tool_name} - no event loop"
                    )
        else:
            # Tool being DISABLED - stop it
            if self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.lifecycle_manager.stop_tool(tool_name),
                    self._event_loop
                )
            else:
                # Fallback: at least remove from active tools
                if tool_name in self._active_tools:
                    del self._active_tools[tool_name]
                    if self.logger:
                        self.logger.system(
                            f"[Tool Manager] Removed {tool_name} from active tools"
                        )
            
            # Clear instruction persistence when tool disabled
            if self.instruction_persistence_manager:
                self.instruction_persistence_manager.clear_instructions(tool_name)
                if self.logger:
                    self.logger.system(
                        f"[Tool Manager] Cleared instructions for {tool_name}"
                    )
    
    def cleanup_all(self):
        """Cleanup all active tools with proper async handling"""
        if not self._active_tools:
            return
        
        if self._event_loop:
            asyncio.run_coroutine_threadsafe(
                self.lifecycle_manager.cleanup_all_tools(),
                self._event_loop
            )
        else:
            # Fallback without event loop
            self._active_tools.clear()
        
        if self.logger:
            self.logger.system("[Tool Manager] Cleanup complete")
    
    # ========================================================================
    # INSTRUCTION RETRIEVAL TRACKING
    # ========================================================================
    
    def _mark_instructions_retrieved(self, tool_name: str):
        """Mark that instructions were retrieved for a tool (resets timer)"""
        current_time = time.time()
        was_refresh = tool_name in self._retrieved_instructions
        self._retrieved_instructions[tool_name] = current_time
        
        if self.logger:
            if was_refresh:
                self.logger.system(
                    f"[Tool Manager] Instructions refreshed: {tool_name} "
                    f"(timer reset to {self._instruction_timeout / 60:.0f} minutes)"
                )
            else:
                self.logger.system(
                    f"[Tool Manager] Instructions retrieved: {tool_name} "
                    f"(valid for {self._instruction_timeout / 60:.0f} minutes)"
                )
    
    def _has_retrieved_instructions(self, tool_name: str) -> bool:
        """Check if instructions were recently retrieved (auto-expires)"""
        if tool_name not in self._retrieved_instructions:
            return False
        
        retrieval_time = self._retrieved_instructions[tool_name]
        current_time = time.time()
        elapsed = current_time - retrieval_time
        
        if elapsed > self._instruction_timeout:
            # Expired - remove from tracking
            del self._retrieved_instructions[tool_name]
            
            if self.logger:
                self.logger.system(
                    f"[Tool Manager] Instructions expired for {tool_name} "
                    f"(elapsed: {elapsed / 60:.1f} minutes)"
                )
            
            return False
        
        return True
    
    def _get_instruction_time_remaining(self, tool_name: str) -> Optional[float]:
        """Get time remaining before instructions expire"""
        if tool_name not in self._retrieved_instructions:
            return None
        
        retrieval_time = self._retrieved_instructions[tool_name]
        current_time = time.time()
        elapsed = current_time - retrieval_time
        remaining = self._instruction_timeout - elapsed
        
        return max(0.0, remaining)
    
    def get_active_instruction_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active instruction retrievals"""
        current_time = time.time()
        status = {}
        
        for tool_name, retrieval_time in self._retrieved_instructions.items():
            elapsed = current_time - retrieval_time
            remaining = self._instruction_timeout - elapsed
            
            status[tool_name] = {
                'retrieved_at': retrieval_time,
                'elapsed_seconds': elapsed,
                'remaining_seconds': remaining,
                'is_valid': remaining > 0,
                'expires_in_minutes': remaining / 60.0
            }
        
        return status
    
    # ========================================================================
    # ACTION EXECUTION
    # ========================================================================
    
    async def execute_structured_actions(
        self,
        actions: List[Dict[str, Any]],
        thought_buffer
    ):
        """
        Execute structured actions with instruction persistence
        
        Args:
            actions: List of action dicts with 'tool' and 'args'
            thought_buffer: ThoughtBuffer for result injection
        """
        instruction_requests = []
        regular_actions = []
        
        for action in actions:
            tool_call = action.get('tool', '')
            
            if tool_call == 'instructions':
                instruction_requests.append(action)
            else:
                regular_actions.append(action)
        
        # Handle instruction retrieval (includes timer resets)
        if instruction_requests:
            await self._handle_instruction_retrieval(instruction_requests, thought_buffer)
        
        # Execute regular actions (with persistence check)
        for action in regular_actions:
            await self._execute_single_action(action, thought_buffer)
    
    async def _handle_instruction_retrieval(
        self,
        requests: List[Dict[str, Any]],
        thought_buffer
    ):
        """Handle instruction retrieval requests"""
        requested_tools = []
        
        for request in requests[:3]:
            args = request.get('args', [])
            if args:
                tool_name = args[0]
                requested_tools.append(tool_name)
        
        if not requested_tools:
            return
        
        # Validate requested tools exist and are active
        valid_requests = [
            name for name in requested_tools
            if name in self._active_tools
        ]
        
        if not valid_requests:
            thought_buffer.add_processed_thought(
                content=f"Instruction retrieval failed: Requested tools not active",
                source='tool_instructions',
                priority_override="MEDIUM"
            )
            return
        
        # Use persistence manager to mark instructions retrieved
        if self.instruction_persistence_manager:
            for tool_name in valid_requests:
                was_refresh = self.instruction_persistence_manager.mark_instructions_retrieved(tool_name)
                
                if self.logger:
                    if was_refresh:
                        self.logger.system(
                            f"[Tool Manager] Instructions refreshed: {tool_name} "
                            f"(timer reset to 6 minutes)"
                        )
                    else:
                        self.logger.system(
                            f"[Tool Manager] Instructions retrieved: {tool_name} "
                            f"(valid for 6 minutes)"
                        )
        
        # Set pending instructions for next prompt
        self.pending_tool_instructions = valid_requests
        
        tool_list = ", ".join(valid_requests)
        thought_buffer.add_processed_thought(
            content=f"Retrieved instructions for: {tool_list}",
            source='tool_instructions',
            priority_override="MEDIUM"
        )
        
        if self.logger:
            self.logger.tool(
                f"[Instructions] Retrieved for {len(valid_requests)} tools: {tool_list}"
            )
        
        # Handle invalid requests
        invalid = [name for name in requested_tools if name not in valid_requests]
        if invalid:
            invalid_list = ", ".join(invalid)
            thought_buffer.add_processed_thought(
                content=f"Note: Could not retrieve instructions for: {invalid_list} (not active)",
                source='tool_instructions',
                priority_override="LOW"
            )
    
    async def _execute_single_action(
        self,
        action: Dict[str, Any],
        thought_buffer
    ):
        """Execute a single tool action with instruction persistence check"""
        tool_call = action.get('tool', '')
        args = action.get('args', [])
        
        if not tool_call:
            return
        
        # Parse tool name and command
        parts = tool_call.split('.', 1)
        tool_name = parts[0]
        command = parts[1] if len(parts) > 1 else ''
        
        # Check if tool exists in metadata
        if tool_name not in self._tool_metadata:
            if self.logger:
                available = list(self._tool_metadata.keys())
                self.logger.warning(
                    f"[Tool Manager] Unknown tool '{tool_name}'. "
                    f"Available tools: {available}"
                )
            
            thought_buffer.add_processed_thought(
                content=(
                    f"Tool '{tool_name}' not found. "
                    f"Available: {', '.join(list(self._tool_metadata.keys())[:5])}"
                ),
                source='tool_error',
                priority_override="HIGH"
            )
            return
        
        # Check if tool is active (enabled)
        tool_instance = self._active_tools.get(tool_name)
        
        if not tool_instance:
            metadata = self._tool_metadata[tool_name]
            control_var = metadata.get('control_variable', 'UNKNOWN')
            
            if self.logger:
                self.logger.warning(
                    f"[Tool Manager] Tool '{tool_name}' is DISABLED. "
                    f"Enable via {control_var}=True"
                )
            
            thought_buffer.add_processed_thought(
                content=(
                    f"Tool '{tool_name}' is currently DISABLED. "
                    f"Cannot execute {tool_call}. "
                ),
                source='tool_disabled',
                priority_override="HIGH"
            )
            return
        
        # Enforce instruction persistence check
        if self.instruction_persistence_manager:
            if not self.instruction_persistence_manager.has_active_instructions(tool_name):
                remaining = self.instruction_persistence_manager.get_time_remaining(tool_name)
                
                if remaining is not None and remaining <= 0:
                    error_msg = (
                        f"Instructions for {tool_name} expired. "
                        f"Retrieve again to use: "
                        f'{{\"tool\": \"instructions\", \"args\": [\"{tool_name}\"]}}'
                    )
                else:
                    error_msg = (
                        f"Cannot use {tool_name}: Instructions not retrieved. "
                        f'Use: {{\"tool\": \"instructions\", \"args\": [\"{tool_name}\"]}}'
                    )
                
                if self.logger:
                    self.logger.warning(
                        f"[Tool Manager] '{tool_name}' used without valid instructions"
                    )
                
                thought_buffer.add_processed_thought(
                    content=error_msg,
                    source='tool_enforcement',
                    priority_override="HIGH"
                )
                
                return
        
        # Check if tool is available
        if not tool_instance.is_available():
            if self.logger:
                self.logger.warning(
                    f"[Tool Manager] Tool '{tool_name}' not available"
                )
            
            thought_buffer.add_processed_thought(
                content=f"[{tool_name}] Tool not available",
                source='tool_failed',
                priority_override="HIGH"
            )
            return
        
        # Register action
        action_id = self.action_state_manager.register_action(
            tool_name=tool_name,
            args=args,
            context={'command': command}
        )
        
        # Execute with timeout
        metadata = self._tool_metadata.get(tool_name, {})
        timeout = metadata.get('timeout', 30)
        
        try:
            self.action_state_manager.mark_in_progress(action_id)
            
            result = await asyncio.wait_for(
                tool_instance.execute(command, args),
                timeout=timeout
            )
            
            self.action_state_manager.complete_action(action_id, result)
            
            self._inject_result(result, thought_buffer, tool_name, success=True)
            
            if self.logger and self.instruction_persistence_manager:
                remaining = self.instruction_persistence_manager.get_time_remaining(tool_name)
                remaining_str = f" (instructions valid for {remaining / 60:.1f} more minutes)" if remaining else ""
                self.logger.tool(
                    f"[{tool_name}] Success: {result.get('content', '')[:100]}{remaining_str}"
                )
        
        except asyncio.TimeoutError:
            error_msg = f"Timeout after {timeout}s"
            self.action_state_manager.fail_action(action_id, error_msg, 'timeout')
            
            self._inject_result(
                {'content': error_msg, 'source': tool_name},
                thought_buffer,
                tool_name,
                success=False,
                is_timeout=True
            )
            
            if self.logger:
                self.logger.tool(f"[{tool_name}] Timeout")
        
        except Exception as e:
            error_msg = str(e)
            self.action_state_manager.fail_action(action_id, error_msg, 'error')
            
            self._inject_result(
                {'content': error_msg, 'source': tool_name},
                thought_buffer,
                tool_name,
                success=False
            )
            
            if self.logger:
                self.logger.error(f"[{tool_name}] Error: {error_msg}")
    
    def _inject_result(
        self,
        result: Dict[str, Any],
        thought_buffer,
        tool_name: str,
        success: bool,
        is_timeout: bool = False
    ):
        """Inject tool result into thought buffer"""
        from BASE.core.thought_buffer import Priority
        
        content = result.get('content', '')
        
        if success:
            thought_content = f"[{tool_name}] SUCCESS: {content}"
            source = 'tool_result'
            priority = Priority.MEDIUM
        elif is_timeout:
            thought_content = f"[{tool_name}] TIMEOUT: {content}"
            source = 'tool_timeout'
            priority = Priority.HIGH
        else:
            thought_content = f"[{tool_name}] FAILED: {content}"
            source = 'tool_failed'
            priority = Priority.HIGH
        
        thought_buffer.add_processed_thought(
            content=thought_content,
            source=source,
            original_ref=str(result),
            priority_override=priority
        )
    
    # ========================================================================
    # PROMPT GENERATION
    # ========================================================================
    
    def get_tool_instructions_for_prompt(self) -> str:
        """
        Get tool instructions for prompts
        Returns tool list or retrieved instructions based on persistence
        """
        if not self.instruction_persistence_manager:
            return self._build_tool_list()
        
        # Get tools with valid instructions
        valid_instruction_tools = self.instruction_persistence_manager.get_active_tool_names()
        
        # Check if specific tools were newly requested
        if self.pending_tool_instructions:
            all_tools_to_include = list(set(
                self.pending_tool_instructions + valid_instruction_tools
            ))
            
            self.pending_tool_instructions = None
            
            if all_tools_to_include:
                from BASE.handlers.tool_instruction_builder import ToolInstructionBuilder
                # This would need the tool registry - simplified for now
                return self._build_tool_list()
        
        # Default: Return minimal tool list
        return self._build_tool_list()
    
    def _build_tool_list(self) -> str:
        """Build minimal tool list with retrieval instructions"""
        lines = [
            "## AVAILABLE TOOLS",
            "",
            f"You have access to {len(self._active_tools)} tool(s).",
            "",
            "**Tool List:**"
        ]
        
        for tool_name in self._active_tools.keys():
            metadata = self._tool_metadata.get(tool_name)
            if metadata:
                description = metadata.get('description', 'No description')
                lines.append(f"- `{tool_name}`: {description}")
        
        lines.extend([
            "",
            "## TOOL INSTRUCTION RETRIEVAL",
            "",
            "To use a tool, first retrieve its instructions using:",
            "",
            "```xml",
            "<action_list>[",
            '{"tool": "instructions", "args": ["tool_name"]}',
            "]</action_list>",
            "```",
            "",
            "**Guidelines:**",
            "- Instructions remain valid for 6 minutes after retrieval",
            "- Requesting instructions again resets the 6-minute timer",
            "- You can use the tool multiple times within the 6-minute window",
            "- Retrieve up to 3 tool instructions per prompt"
        ])
        
        return "\n".join(lines)