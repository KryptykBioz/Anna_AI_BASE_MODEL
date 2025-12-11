# Filename: BASE/handlers/tool_identifier.py
"""
Tool Identifier - Tool Discovery System
FIXED: Silent cache reads, only logs during actual discovery
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class ToolInfo:
    """Information about a discovered tool"""
    tool_name: str
    tool_directory: str
    module_path: str
    control_variable_name: str
    control_variable_value: bool
    tool_description: str
    metadata: Dict[str, Any]
    is_enabled: bool


class ToolIdentifier:
    """
    Discovers tools in BASE/tools/installed/
    Checks control variables to determine enabled state
    """
    
    def __init__(self, controls_module, project_root: Path, logger=None):
        """
        Initialize tool identifier
        
        Args:
            controls_module: Controls module with tool control variables
            project_root: Project root path
            logger: Optional logger
        """
        self.controls = controls_module
        self.project_root = project_root
        self.logger = logger
        
        # Tools directory
        self.tools_dir = project_root / 'BASE' / 'tools' / 'installed'
        
        # Cache discovered tools
        self._tool_cache: Optional[List[ToolInfo]] = None
        self._cache_timestamp = 0
    
    def discover_tools(self, force_rescan: bool = False) -> List[ToolInfo]:
        """
        Discover all tools in BASE/tools/installed/ that are ENABLED
        OPTIMIZED: Returns cached results unless force_rescan=True
        SILENT: No logging during cache reads
        
        Args:
            force_rescan: Force re-scan even if cache exists
            
        Returns:
            List of ToolInfo objects for enabled tools
        """
        # Return from cache if available (SILENT - no logs)
        if not force_rescan and self._tool_cache is not None:
            # Filter to enabled tools only
            return [tool for tool in self._tool_cache if tool.is_enabled]
        
        # ONLY log during actual discovery
        if self.logger:
            self.logger.system("[Tool Discovery] Scanning BASE/tools/installed/...")
        
        # Perform discovery
        all_tools = self.discover_all_tools()
        
        # Update cache
        self._tool_cache = all_tools
        
        # Filter to enabled tools
        enabled_tools = [tool for tool in all_tools if tool.is_enabled]
        
        if self.logger:
            self.logger.system(
                f"[Tool Discovery] Found {len(all_tools)} tools, "
                f"{len(enabled_tools)} enabled"
            )
        
        return enabled_tools
    
    def discover_all_tools(self) -> List[ToolInfo]:
        """
        Discover ALL tools (enabled or disabled)
        LOGS each tool found
        
        Returns:
            List of all ToolInfo objects
        """
        tools = []
        
        if not self.tools_dir.exists():
            if self.logger:
                self.logger.warning(f"[Tool Discovery] Tools directory not found: {self.tools_dir}")
            return tools
        
        # Scan each subdirectory in BASE/tools/installed/
        for tool_dir in self.tools_dir.iterdir():
            if not tool_dir.is_dir():
                continue
            
            # Skip special directories
            if tool_dir.name.startswith('_') or tool_dir.name.startswith('.'):
                continue
            
            # Check for information.json
            info_file = tool_dir / 'information.json'
            if not info_file.exists():
                if self.logger:
                    self.logger.warning(
                        f"[Tool Discovery] Skipping {tool_dir.name}: no information.json"
                    )
                continue
            
            # Load tool information
            try:
                tool_info = self._load_tool_info(tool_dir, info_file)
                if tool_info:
                    tools.append(tool_info)
                    
                    # ONLY log individual tools during full discovery
                    if self.logger:
                        status = "enabled" if tool_info.is_enabled else "disabled"
                        self.logger.system(
                            f"[Tool Discovery] Found {tool_info.tool_name} ({status})"
                        )
            
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"[Tool Discovery] Error loading {tool_dir.name}: {e}"
                    )
        
        return tools
    
    def _load_tool_info(self, tool_dir: Path, info_file: Path) -> Optional[ToolInfo]:
        """
        Load tool information from information.json
        
        Args:
            tool_dir: Tool directory path
            info_file: information.json file path
            
        Returns:
            ToolInfo object or None if invalid
        """
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract required fields
            tool_name = data.get('tool_name')
            control_var_name = data.get('control_variable_name')
            control_var_value = data.get('control_variable_value', False)
            tool_description = data.get('tool_description', 'No description')
            
            if not tool_name or not control_var_name:
                if self.logger:
                    self.logger.warning(
                        f"[Tool Discovery] {tool_dir.name}: missing tool_name or control_variable_name"
                    )
                return None
            
            # Check if tool is enabled via control variable
            is_enabled = getattr(self.controls, control_var_name, False)
            
            # Build module path
            module_path = f"BASE.tools.installed.{tool_dir.name}"
            
            # Create ToolInfo
            return ToolInfo(
                tool_name=tool_name,
                tool_directory=tool_dir.name,
                module_path=module_path,
                control_variable_name=control_var_name,
                control_variable_value=control_var_value,
                tool_description=tool_description,
                metadata=data.get('metadata', {}),
                is_enabled=is_enabled
            )
        
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(
                    f"[Tool Discovery] {tool_dir.name}: Invalid JSON - {e}"
                )
            return None
        
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"[Tool Discovery] {tool_dir.name}: Error loading - {e}"
                )
            return None
    
    def get_tool_by_name(self, tool_name: str) -> Optional[ToolInfo]:
        """
        Get specific tool by name
        SILENT: Uses cache if available
        
        Args:
            tool_name: Name of tool
            
        Returns:
            ToolInfo or None
        """
        # Use cached discovery (silent)
        all_tools = self.discover_tools(force_rescan=False)
        
        for tool in all_tools:
            if tool.tool_name == tool_name:
                return tool
        
        return None
    
    def get_enabled_tool_names(self) -> List[str]:
        """
        Get list of enabled tool names
        SILENT: Uses cache
        
        Returns:
            List of tool names
        """
        enabled_tools = self.discover_tools(force_rescan=False)
        return [tool.tool_name for tool in enabled_tools]
    
    def invalidate_cache(self):
        """Force cache invalidation for next discovery"""
        self._tool_cache = None
        if self.logger:
            self.logger.system("[Tool Discovery] Cache invalidated")
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        Check if specific tool is enabled
        SILENT: Uses cache
        
        Args:
            tool_name: Name of tool
            
        Returns:
            True if enabled, False otherwise
        """
        tool = self.get_tool_by_name(tool_name)
        return tool.is_enabled if tool else False
    
    def get_tool_count(self) -> Dict[str, int]:
        """
        Get count of total and enabled tools
        SILENT: Uses cache
        
        Returns:
            Dict with 'total' and 'enabled' counts
        """
        all_tools = self.discover_all_tools() if self._tool_cache is None else self._tool_cache
        enabled_count = sum(1 for tool in all_tools if tool.is_enabled)
        
        return {
            'total': len(all_tools),
            'enabled': enabled_count
        }
    
    def get_tools_by_category(self) -> Dict[str, List[ToolInfo]]:
        """
        Group tools by category from metadata
        SILENT: Uses cache
        
        Returns:
            Dict mapping category names to lists of ToolInfo
        """
        all_tools = self.discover_all_tools() if self._tool_cache is None else self._tool_cache
        
        categories: Dict[str, List[ToolInfo]] = {}
        
        for tool in all_tools:
            category = tool.metadata.get('category', 'Other Tools')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(tool)
        
        return categories
    
    def get_tool_info_summary(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information for a specific tool
        SILENT: Uses cache
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Dict with tool summary or None
        """
        tool = self.get_tool_by_name(tool_name)
        
        if not tool:
            return None
        
        return {
            'name': tool.tool_name,
            'description': tool.tool_description,
            'enabled': tool.is_enabled,
            'control_variable': tool.control_variable_name,
            'category': tool.metadata.get('category', 'Other Tools'),
            'version': tool.metadata.get('version', 'unknown'),
            'requires_api': tool.metadata.get('requires_api', False)
        }
    
    def list_all_tool_names(self) -> List[str]:
        """
        Get list of all tool names (enabled and disabled)
        SILENT: Uses cache
        
        Returns:
            List of all tool names
        """
        all_tools = self.discover_all_tools() if self._tool_cache is None else self._tool_cache
        return [tool.tool_name for tool in all_tools]
    
    def get_disabled_tool_names(self) -> List[str]:
        """
        Get list of disabled tool names
        SILENT: Uses cache
        
        Returns:
            List of disabled tool names
        """
        all_tools = self.discover_all_tools() if self._tool_cache is None else self._tool_cache
        return [tool.tool_name for tool in all_tools if not tool.is_enabled]
    
    def refresh_tool_state(self, tool_name: str) -> bool:
        """
        Refresh enabled state for a specific tool by re-reading control variable
        Used when control variables change
        
        Args:
            tool_name: Name of tool to refresh
            
        Returns:
            True if tool was found and updated, False otherwise
        """
        if self._tool_cache is None:
            return False
        
        for tool in self._tool_cache:
            if tool.tool_name == tool_name:
                # Re-read control variable
                old_state = tool.is_enabled
                tool.is_enabled = getattr(self.controls, tool.control_variable_name, False)
                
                if self.logger and old_state != tool.is_enabled:
                    status = "enabled" if tool.is_enabled else "disabled"
                    self.logger.system(
                        f"[Tool Discovery] Updated {tool_name} state: {status}"
                    )
                
                return True
        
        return False
    
    def refresh_all_tool_states(self):
        """
        Refresh enabled state for all cached tools
        Useful after bulk control variable changes
        """
        if self._tool_cache is None:
            return
        
        changes = []
        
        for tool in self._tool_cache:
            old_state = tool.is_enabled
            tool.is_enabled = getattr(self.controls, tool.control_variable_name, False)
            
            if old_state != tool.is_enabled:
                status = "enabled" if tool.is_enabled else "disabled"
                changes.append(f"{tool.tool_name} → {status}")
        
        if changes and self.logger:
            self.logger.system(
                f"[Tool Discovery] State changes: {', '.join(changes)}"
            )