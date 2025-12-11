# Filename: BASE/handlers/tool_registry.py
"""
Tool Registry - Central Tool Management
FIXED: Proper metadata extraction from tool_info.metadata dict
"""
from typing import Dict, Optional, Type, Any, List
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import sys


@dataclass
class ToolMetadata:
    """Metadata for a registered tool"""
    tool_name: str
    control_variable: str
    description: str
    commands: List[Dict[str, Any]]
    examples: List[str]
    timeout_seconds: int
    tool_directory: Path
    
    # Dynamically loaded classes
    decider_class: Optional[Type] = None
    handler_class: Optional[Type] = None
    executor_class: Optional[Type] = None
    interface_class: Optional[Type] = None
    
    # Instances (created on demand)
    decider_instance: Optional[Any] = None
    handler_instance: Optional[Any] = None
    executor_instance: Optional[Any] = None
    interface_instance: Optional[Any] = None
    
    is_enabled: bool = True


class ToolRegistry:
    """
    Central registry for all discovered and loaded tools
    Provides access to tool components and metadata
    """
    
    def __init__(self, logger=None):
        """
        Initialize tool registry
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self._tools: Dict[str, ToolMetadata] = {}
    
    def register_tool(self, tool_info, controls_module) -> bool:
        """
        Register a tool and dynamically load its components
        
        Args:
            tool_info: ToolInfo object from tool_identifier
            controls_module: Controls module for checking enabled state
            
        Returns:
            True if registration successful, False otherwise
        """
        tool_name = tool_info.tool_name
        
        # Check if already registered
        if tool_name in self._tools:
            if self.logger:
                self.logger.system(f"[Tool Registry] {tool_name} already registered")
            return True
        
        try:
            # Get tool directory as Path
            tool_dir = self._get_tool_directory_path(tool_info)
            
            if not tool_dir.exists():
                if self.logger:
                    self.logger.error(
                        f"[Tool Registry] {tool_name} directory not found: {tool_dir}"
                    )
                return False
            
            # Validate 5-file structure
            required_files = ['decider.py', 'handler.py', 'executor.py', 'interface.py', 'information.json']
            missing_files = [f for f in required_files if not (tool_dir / f).exists()]
            
            if missing_files:
                if self.logger:
                    self.logger.error(
                        f"[Tool Registry] {tool_name} missing files: {', '.join(missing_files)}"
                    )
                return False
            
            # Load tool classes dynamically
            decider = self._load_module(tool_dir / "decider.py", f"{tool_name}_decider")
            handler = self._load_module(tool_dir / "handler.py", f"{tool_name}_handler")
            executor = self._load_module(tool_dir / "executor.py", f"{tool_name}_executor")
            interface = self._load_module(tool_dir / "interface.py", f"{tool_name}_interface")
            
            # Find the main classes
            decider_class = self._find_class(decider, 'Decider')
            handler_class = self._find_class(handler, 'Handler')
            executor_class = self._find_class(executor, 'Executor')
            interface_class = self._find_class(interface, 'Interface')
            
            if not all([decider_class, handler_class, executor_class, interface_class]):
                if self.logger:
                    missing = []
                    if not decider_class: missing.append("Decider")
                    if not handler_class: missing.append("Handler")
                    if not executor_class: missing.append("Executor")
                    if not interface_class: missing.append("Interface")
                    
                    self.logger.error(
                        f"[Tool Registry] {tool_name} missing classes: {', '.join(missing)}"
                    )
                return False
            
            # CRITICAL FIX: Extract from metadata dict, not tool_info directly
            commands = tool_info.metadata.get('available_commands', [])
            examples = tool_info.metadata.get('tool_usage_examples', [])
            timeout = tool_info.metadata.get('timeout_seconds', 30)
            
            # Create metadata
            metadata = ToolMetadata(
                tool_name=tool_name,
                control_variable=tool_info.control_variable_name,
                description=tool_info.tool_description,
                commands=commands,
                examples=examples,
                timeout_seconds=timeout,
                tool_directory=tool_dir,
                decider_class=decider_class,
                handler_class=handler_class,
                executor_class=executor_class,
                interface_class=interface_class,
                is_enabled=getattr(controls_module, tool_info.control_variable_name, False)
            )
            
            self._tools[tool_name] = metadata
            
            if self.logger:
                self.logger.system(
                    f"[Tool Registry] [SUCCESS] Registered {tool_name} "
                    f"({len(commands)} commands, {timeout}s timeout)"
                )
            
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Tool Registry] Failed to register {tool_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_tool_directory_path(self, tool_info) -> Path:
        """
        Get tool directory as Path object
        
        Args:
            tool_info: ToolInfo object
            
        Returns:
            Path to tool directory
        """
        # tool_info.tool_directory is the directory NAME (string)
        # Reconstruct full path from project root
        project_root = Path(__file__).parent.parent.parent
        tools_base = project_root / 'BASE' / 'tools' / 'installed'
        
        if hasattr(tool_info, 'tool_directory') and tool_info.tool_directory:
            return tools_base / tool_info.tool_directory
        
        # Fallback: try to extract from module_path
        if hasattr(tool_info, 'module_path'):
            parts = tool_info.module_path.split('.')
            if 'installed' in parts:
                idx = parts.index('installed')
                tool_dir_name = parts[idx + 1]
                return tools_base / tool_dir_name
        
        raise ValueError(f"Cannot determine tool directory for {tool_info.tool_name}")
    
    def _load_module(self, file_path: Path, module_name: str):
        """Dynamically load a Python module from file path"""
        if not file_path.exists():
            raise FileNotFoundError(f"Module file not found: {file_path}")
        
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    
    def _find_class_by_tool_name(self, module, tool_name: str, suffix: str) -> Optional[Type]:
        """
        Find class by constructing expected name from tool_name
        More explicit than searching by suffix
        
        Args:
            module: Python module
            tool_name: Tool name (e.g., 'wiki_search')
            suffix: Class type suffix ('Decider', 'Handler', 'Executor', 'Interface')
            
        Returns:
            Class type or None
        """
        # Convert tool_name to class name format
        # wiki_search -> WikiSearch
        parts = tool_name.split('_')
        class_prefix = ''.join(word.capitalize() for word in parts)
        
        # Expected class name: WikiSearchDecider, WikiSearchHandler, etc.
        expected_name = f"{class_prefix}{suffix}"
        
        # Try to get the class directly
        if hasattr(module, expected_name):
            obj = getattr(module, expected_name)
            if isinstance(obj, type):
                return obj
        
        # Fallback to suffix search (with base class filtering)
        return self._find_class(module, suffix)
    
    def _find_class(self, module, suffix: str) -> Optional[Type]:
        """
        Find a class in module that ends with suffix
        FIXED: Skips base classes (those that start with "Base")
        
        Args:
            module: Python module
            suffix: Class name suffix (e.g., 'Decider', 'Handler', 'Executor', 'Interface')
            
        Returns:
            Class type or None
        """
        found_classes = []
        
        for name in dir(module):
            # Skip private/protected
            if name.startswith('_'):
                continue
            
            # CRITICAL FIX: Skip base classes
            if name.startswith('Base'):
                continue
            
            # Must end with suffix
            if not name.endswith(suffix):
                continue
            
            obj = getattr(module, name)
            
            # Must be a class (not instance or function)
            if not isinstance(obj, type):
                continue
            
            found_classes.append((name, obj))
        
        # Return the first non-base class found
        if found_classes:
            # Sort to ensure consistent ordering
            found_classes.sort(key=lambda x: x[0])
            
            if self.logger:
                class_name = found_classes[0][0]
                if len(found_classes) > 1:
                    all_names = [c[0] for c in found_classes]
                    self.logger.system(
                        f"[Tool Registry] Found multiple {suffix} classes: {all_names}, "
                        f"using {class_name}"
                    )
            
            return found_classes[0][1]
        
        return None

    
    def unregister_tool(self, tool_name: str):
        """
        Unregister a tool (when disabled)
        
        Args:
            tool_name: Name of tool to unregister
        """
        if tool_name in self._tools:
            # Cleanup instances if they exist
            tool = self._tools[tool_name]
            if tool.interface_instance and hasattr(tool.interface_instance, 'cleanup'):
                try:
                    tool.interface_instance.cleanup()
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Error cleaning up {tool_name}: {e}")
            
            del self._tools[tool_name]
            if self.logger:
                self.logger.system(f"[Tool Registry] Unregistered {tool_name}")

    
    def get_tool(self, tool_name: str) -> Optional[ToolMetadata]:
        """
        Get tool metadata by name (only if enabled)
        
        Args:
            tool_name: Name of tool
            
        Returns:
            ToolMetadata if found and enabled, None otherwise
        """
        tool = self._tools.get(tool_name)
        if tool and tool.is_enabled:
            return tool
        return None
    
    def get_all_tools(self) -> Dict[str, ToolMetadata]:
        """Get all registered tools (enabled or disabled)"""
        return self._tools.copy()
    
    def get_enabled_tools(self) -> Dict[str, ToolMetadata]:
        """Get only enabled tools"""
        return {
            name: tool for name, tool in self._tools.items()
            if tool.is_enabled
        }
    
    def get_enabled_tool_names(self) -> List[str]:
        """Get list of enabled tool names"""
        return [name for name, tool in self._tools.items() if tool.is_enabled]
    
    def update_tool_enabled_state(self, tool_name: str, is_enabled: bool):
        """
        Update tool enabled state
        
        Args:
            tool_name: Name of tool
            is_enabled: New enabled state
        """
        if tool_name in self._tools:
            self._tools[tool_name].is_enabled = is_enabled
            if self.logger:
                state = "enabled" if is_enabled else "disabled"
                self.logger.system(f"[Tool Registry] {tool_name} {state}")
    
    def is_tool_registered(self, tool_name: str) -> bool:
        """Check if tool is registered"""
        return tool_name in self._tools
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if tool is registered and enabled"""
        tool = self._tools.get(tool_name)
        return tool is not None and tool.is_enabled
    
    def clear(self):
        """Clear all registered tools"""
        # Cleanup all tool instances
        for tool_name, tool in self._tools.items():
            if tool.interface_instance and hasattr(tool.interface_instance, 'cleanup'):
                try:
                    tool.interface_instance.cleanup()
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Error cleaning up {tool_name}: {e}")
        
        self._tools.clear()
        if self.logger:
            self.logger.system("[Tool Registry] Cleared all tools")