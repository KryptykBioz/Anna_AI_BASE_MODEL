# Filename: BASE/handlers/tool_lifecycle.py
"""
Tool Lifecycle Manager
Handles tool discovery, loading, starting, and stopping
"""
from typing import Dict, Optional, Any
from pathlib import Path
import importlib.util
import sys
import json


class ToolLifecycleManager:
    """
    Manages tool discovery and lifecycle operations
    Separated from ToolManager to reduce file complexity
    """
    
    def __init__(self, project_root: Path, logger=None):
        """
        Initialize lifecycle manager
        
        Args:
            project_root: Project root path
            logger: Optional logger instance
        """
        self.project_root = project_root
        self.logger = logger
        
        # Tool metadata cache
        self._tool_metadata: Dict[str, Dict] = {}
        
        # Active tool instances (shared with ToolManager)
        self._active_tools: Dict[str, Any] = {}
        
        # Event loop and thought buffer (set by ToolManager)
        self._event_loop = None
        self._thought_buffer = None
    
    # ========================================================================
    # TOOL DISCOVERY
    # ========================================================================
    
    def discover_tools(self) -> Dict[str, Dict]:
        """
        Discover all available tools from filesystem
        
        Returns:
            Dict mapping tool_name to metadata
        """
        tools_dir = self.project_root / 'BASE' / 'tools' / 'installed'
        
        if not tools_dir.exists():
            if self.logger:
                self.logger.warning(f"Tools directory not found: {tools_dir}")
            return {}
        
        discovered = {}
        
        for tool_dir in tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue
            
            info_file = tool_dir / 'information.json'
            if not info_file.exists():
                continue
            
            tool_file = tool_dir / 'tool.py'
            if not tool_file.exists():
                continue
            
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                
                tool_name = info.get('tool_name')
                control_var = info.get('control_variable_name')
                
                if not tool_name or not control_var:
                    if self.logger:
                        self.logger.warning(
                            f"Invalid tool metadata in {tool_dir.name}"
                        )
                    continue
                
                discovered[tool_name] = {
                    'tool_name': tool_name,
                    'control_variable': control_var,
                    'description': info.get('tool_description', ''),
                    'commands': info.get('available_commands', []),
                    'timeout': info.get('timeout_seconds', 30),
                    'cooldown': info.get('cooldown_seconds', 0),
                    'tool_dir': tool_dir,
                    'tool_file': tool_file,
                    'metadata': info
                }
                
                if self.logger:
                    self.logger.system(
                        f"[Tool Discovery] Found {tool_name} "
                        f"(control: {control_var})"
                    )
            
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Failed to load tool from {tool_dir.name}: {e}"
                    )
        
        self._tool_metadata = discovered
        return discovered
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict]:
        """
        Get complete metadata for a specific tool
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Dict with tool metadata or None
        """
        metadata = self._tool_metadata.get(tool_name)
        if not metadata:
            return None
        
        # Check if tool is active
        is_active = tool_name in self._active_tools
        
        return {
            'name': tool_name,
            'enabled': is_active,
            'description': metadata.get('description', 'No description'),
            'control_variable': metadata.get('control_variable', 'UNKNOWN'),
            'commands': metadata.get('commands', []),
            'cooldown': metadata.get('cooldown', 0),
            'timeout': metadata.get('timeout', 30)
        }
    
    def get_all_metadata(self) -> Dict[str, Dict]:
        """Get all tool metadata"""
        return self._tool_metadata.copy()
    
    # ========================================================================
    # TOOL LOADING
    # ========================================================================
    
    def load_tool_class(self, tool_file: Path, tool_name: str):
        """
        Dynamically load tool class from tool.py
        
        Args:
            tool_file: Path to tool.py file
            tool_name: Name of tool (for module naming)
        
        Returns:
            Tool class or None if not found
        """
        try:
            module_name = f"tool_{tool_name}"
            
            spec = importlib.util.spec_from_file_location(
                module_name, str(tool_file)
            )
            
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find class ending in 'Tool' (but not BaseTool)
            for attr_name in dir(module):
                if attr_name.endswith('Tool') and not attr_name.startswith('Base'):
                    tool_class = getattr(module, attr_name)
                    if isinstance(tool_class, type):
                        return tool_class
            
            return None
        
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"[Tool Lifecycle] Failed to load {tool_file}: {e}"
                )
            return None
    
    # ========================================================================
    # TOOL LIFECYCLE
    # ========================================================================
    
    def set_event_loop(self, event_loop):
        """Set event loop for async operations"""
        self._event_loop = event_loop
    
    def set_thought_buffer(self, thought_buffer):
        """Set thought buffer for tool context injection"""
        self._thought_buffer = thought_buffer
    
    def set_active_tools(self, active_tools: Dict[str, Any]):
        """Set reference to active tools dict (shared with ToolManager)"""
        self._active_tools = active_tools
    
    async def start_tool(self, tool_name: str, config, controls) -> bool:
        """
        Start a tool by loading and initializing it
        
        Args:
            tool_name: Name of tool to start
            config: Configuration object
            controls: Controls module
            
        Returns:
            True if started successfully
        """
        if tool_name in self._active_tools:
            if self.logger:
                self.logger.warning(
                    f"[Tool Lifecycle] {tool_name} already running"
                )
            return False
        
        metadata = self._tool_metadata.get(tool_name)
        if not metadata:
            if self.logger:
                self.logger.error(
                    f"[Tool Lifecycle] Unknown tool: {tool_name}"
                )
            return False
        
        try:
            # Load tool class dynamically
            tool_class = self.load_tool_class(
                metadata['tool_file'], 
                tool_name
            )
            
            if not tool_class:
                if self.logger:
                    self.logger.error(
                        f"[Tool Lifecycle] Could not load class for {tool_name}"
                    )
                return False
            
            # Instantiate tool
            tool_instance = tool_class(
                config=config,
                controls=controls,
                logger=self.logger
            )
            
            # Call tool's start() method (which calls initialize())
            await tool_instance.start(
                thought_buffer=self._thought_buffer,
                event_loop=self._event_loop
            )
            
            # Store instance
            self._active_tools[tool_name] = tool_instance
            
            if self.logger:
                self.logger.success(
                    f"[Tool Lifecycle] Started {tool_name}"
                )
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"[Tool Lifecycle] Failed to start {tool_name}: {e}"
                )
            import traceback
            traceback.print_exc()
            return False
    
    async def stop_tool(self, tool_name: str) -> bool:
        """
        Stop a tool by calling its end() method
        
        Args:
            tool_name: Name of tool to stop
            
        Returns:
            True if stopped successfully
        """
        tool_instance = self._active_tools.get(tool_name)
        
        if not tool_instance:
            if self.logger:
                self.logger.system(
                    f"[Tool Lifecycle] {tool_name} not running"
                )
            return False
        
        try:
            # Call tool's end() method (which calls cleanup())
            await tool_instance.end()
            
            # Remove from active tools
            del self._active_tools[tool_name]
            
            if self.logger:
                self.logger.system(
                    f"[Tool Lifecycle] Stopped {tool_name}"
                )
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"[Tool Lifecycle] Error stopping {tool_name}: {e}"
                )
            return False
    
    async def cleanup_all_tools(self):
        """Cleanup all active tools"""
        tool_names = list(self._active_tools.keys())
        
        if not tool_names:
            return
        
        if self.logger:
            self.logger.system(
                f"[Tool Lifecycle] Cleaning up {len(tool_names)} tool(s)"
            )
        
        for tool_name in tool_names:
            await self.stop_tool(tool_name)
        
        if self.logger:
            self.logger.system("[Tool Lifecycle] Cleanup complete")