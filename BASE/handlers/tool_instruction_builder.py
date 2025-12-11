# Filename: BASE/handlers/tool_instruction_builder.py
"""
Tool Instruction Builder - New BaseTool Architecture  
Builds tool instruction sections from information.json files
Reads directly from filesystem - FIXED: Complete instruction formatting
"""
from typing import Dict, List, Optional
from pathlib import Path
import json


class ToolInstructionBuilder:
    """
    Dynamically builds tool instructions from information.json files
    Designed for new BaseTool architecture (tool.py format)
    FIXED: Now includes ALL fields from information.json
    """
    
    def __init__(self, tool_manager, logger=None):
        """
        Initialize tool instruction builder
        
        Args:
            tool_manager: ToolManager instance
            logger: Optional logger
        """
        self.tool_manager = tool_manager
        self.logger = logger
        
        # Get project root from tool_manager's lifecycle_manager
        if hasattr(tool_manager, 'lifecycle_manager') and hasattr(tool_manager.lifecycle_manager, 'project_root'):
            self.project_root = tool_manager.lifecycle_manager.project_root
        elif hasattr(tool_manager, 'project_root'):
            self.project_root = tool_manager.project_root
        else:
            # Fallback to calculating from this file's location
            self.project_root = Path(__file__).parent.parent.parent
        
        self.tools_base_dir = self.project_root / 'BASE' / 'tools' / 'installed'
        
        if self.logger:
            self.logger.system(
                f"[Instruction Builder] Initialized\n"
                f"  Project root: {self.project_root}\n"
                f"  Tools dir: {self.tools_base_dir}\n"
                f"  Tools dir exists: {self.tools_base_dir.exists()}"
            )
    
    def build_tool_list_section(self) -> str:
        """Build minimal tool list with retrieval instructions"""
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        
        if not enabled_tools:
            return self._build_no_tools_section()
        
        lines = [
            "## AVAILABLE TOOLS",
            "",
            f"You have access to **{len(enabled_tools)}** enabled tool(s).",
            "",
            "**Tool List:**"
        ]
        
        for tool_name in enabled_tools:
            description = self._get_brief_description(tool_name)
            lines.append(f"- `{tool_name}` [ENABLED - RETRIEVE INSTRUCTIONS TO USE]: {description}")
        
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
            "- You must retrieve the instructions for a tool before the tool may be used",
            "- If you do not see the tool instructions, you cannot use that tool without retrieving the instructions first",
            "- Retrieve up to 3 tool instructions at a time",
            "",
            "**Example:**",
            "```xml",
            "<action_list>[",
            '{"tool": "instructions", "args": ["sounds"]},',
            '{"tool": "instructions", "args": ["wiki_search"]}',
            "]</action_list>",
            "```",
            "",
            "**Important:**",
            "- Only tools listed above are currently available",
            "- Disabled tools are NOT shown in this list",
            "- If a tool you remember is missing, it has been disabled",
            "- Do not ask follow-up questions about how to use tools, simply use the tool",
            ""
        ])
        
        return "\n".join(lines)
    
    def build_retrieved_tool_instructions(self, tool_names: List[str]) -> str:
        """
        Build detailed instructions for specific requested tools
        FIXED: Complete formatting with all information.json fields
        """
        if not tool_names:
            return ""
        
        # Get enabled tools from tool manager
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        
        # Filter to only requested tools that are enabled
        requested_tools = [name for name in tool_names if name in enabled_tools]
        
        if not requested_tools:
            if self.logger:
                self.logger.warning(
                    f"[Instruction Builder] No enabled tools match request: {tool_names}\n"
                    f"  Enabled tools: {enabled_tools}"
                )
            return ""
        
        lines = [
            "## RETRIEVED TOOL INSTRUCTIONS",
            "",
            f"Instructions for {len(requested_tools)} tool(s) as requested:",
            ""
        ]
        
        for tool_name in requested_tools:
            tool_section = self._build_tool_section(tool_name)
            if tool_section:
                lines.append(tool_section)
            else:
                if self.logger:
                    self.logger.warning(
                        f"[Instruction Builder] Failed to build section for {tool_name}"
                    )
        
        # Add usage reminder
        lines.extend([
            "",
            "## TOOL USAGE REMINDER",
            "",
            "Format your tool calls as:",
            "```xml",
            "<action_list>[",
            '{"tool": "tool_name.command", "args": ["arg1", "arg2"]}',
            "]</action_list>",
            "```",
            "",
            "**IMPORTANT**",
            "- If you do not see the instructions for a tool, you must first retrieve the instructions for that tool",
            "- Do not ask the user how a tool should be used or for clarification",
            ""
        ])
        
        result = "\n".join(lines)
        
        if self.logger:
            self.logger.system(
                f"[Instruction Builder] [SUCCESS] Built instructions: {len(result)} chars, "
                f"{len(requested_tools)} tools"
            )
        
        return result
    
    def _build_tool_section(self, tool_name: str) -> str:
        """
        Build COMPLETE instruction section for a single tool
        FIXED: Now includes ALL fields from information.json
        """
        # Load information.json directly from filesystem
        info_data = self._load_info_json(tool_name)
        
        if not info_data:
            if self.logger:
                self.logger.error(
                    f"[Instruction Builder] Cannot load information.json for {tool_name}"
                )
            return ""
        
        lines = []
        
        # ===================================================================
        # TOOL HEADER with display name
        # ===================================================================
        display_name = info_data.get('metadata', {}).get(
            'display_name', 
            tool_name.replace('_', ' ').title()
        )
        
        lines.extend([
            f"### {display_name.upper()} [ENABLED]",
            ""
        ])
        
        # ===================================================================
        # TOOL NAME (from information.json)
        # ===================================================================
        lines.append(f"**Tool Name:** `{info_data.get('tool_name', tool_name)}`")
        lines.append("")
        
        # ===================================================================
        # TOOL DESCRIPTION (from information.json)
        # ===================================================================
        description = info_data.get('tool_description', 'No description available')
        lines.append(f"**Description:** {description}")
        lines.append("")
        
        # ===================================================================
        # AVAILABLE COMMANDS (from information.json)
        # ===================================================================
        commands = info_data.get('available_commands', [])
        if commands:
            lines.append("**Available Commands:**")
            lines.append("")
            for cmd in commands:
                lines.extend(self._format_command(tool_name, cmd))
            lines.append("")
        
        # ===================================================================
        # USAGE GUIDANCE (from information.json - tool_usage_guidance)
        # ===================================================================
        guidance = info_data.get('tool_usage_guidance', [])
        if guidance:
            lines.append("**Usage Guidelines:**")
            for guide in guidance:
                lines.append(f"- {guide}")
            lines.append("")
        
        # ===================================================================
        # USAGE EXAMPLES (from information.json - tool_usage_examples)
        # ===================================================================
        examples = info_data.get('tool_usage_examples', [])
        if examples:
            lines.append("**Usage Examples:**")
            lines.append("")
            for i, example in enumerate(examples, 1):
                lines.append(f"Example {i}:")
                lines.append("```json")
                lines.append(example)
                lines.append("```")
                lines.append("")
        
        # ===================================================================
        # TECHNICAL DETAILS (timeout, cooldown, etc.)
        # ===================================================================
        tech_details = []
        timeout = info_data.get('timeout_seconds')
        cooldown = info_data.get('cooldown_seconds')
        
        if timeout:
            tech_details.append(f"Timeout: {timeout}s")
        if cooldown and cooldown > 0:
            tech_details.append(f"Cooldown: {cooldown}s")
        
        if tech_details:
            lines.append(f"**Technical Details:** {' | '.join(tech_details)}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)
    
    def _load_info_json(self, tool_name: str) -> Optional[dict]:
        """
        Load information.json directly from filesystem
        Strategy 1: Direct path construction
        Strategy 2: Search all subdirectories
        """
        # Strategy 1: Direct path construction
        tool_dir = self.tools_base_dir / tool_name
        info_file = tool_dir / 'information.json'
        
        if self.logger:
            self.logger.system(
                f"[Instruction Builder] Attempting to load {tool_name}\n"
                f"  Expected path: {info_file}\n"
                f"  Tool dir exists: {tool_dir.exists()}\n"
                f"  Info file exists: {info_file.exists()}"
            )
        
        if info_file.exists():
            data = self._read_json_safe(info_file)
            if data:
                if self.logger:
                    self.logger.system(
                        f"[Instruction Builder] [SUCCESS] Loaded {tool_name} from: {info_file}"
                    )
                return data
        
        # Strategy 2: Search all subdirectories
        if self.tools_base_dir.exists():
            if self.logger:
                self.logger.system(
                    f"[Instruction Builder] Strategy 1 failed, searching in: {self.tools_base_dir}"
                )
            
            for subdir in self.tools_base_dir.iterdir():
                if not subdir.is_dir():
                    continue
                
                # Skip special directories
                if subdir.name.startswith('_') or subdir.name.startswith('.'):
                    continue
                
                potential_info = subdir / 'information.json'
                if not potential_info.exists():
                    continue
                
                data = self._read_json_safe(potential_info)
                if data and data.get('tool_name') == tool_name:
                    if self.logger:
                        self.logger.system(
                            f"[Instruction Builder] [SUCCESS] Found {tool_name} via search in: {subdir}"
                        )
                    return data
        
        # All strategies failed
        if self.logger:
            self.logger.error(
                f"[Instruction Builder] Cannot locate information.json for {tool_name}\n"
                f"  Expected path: {info_file}\n"
                f"  Tools base: {self.tools_base_dir}\n"
                f"  Base exists: {self.tools_base_dir.exists()}"
            )
        
        return None
    
    def _read_json_safe(self, file_path: Path) -> Optional[dict]:
        """Safely read and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if self.logger:
                self.logger.system(
                    f"[Instruction Builder] [SUCCESS] JSON parsed successfully: {file_path.name}"
                )
            
            return data
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(
                    f"[Instruction Builder] JSON decode error in {file_path}: {e}"
                )
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"[Instruction Builder] Error reading {file_path}: {e}"
                )
            return None
    
    def _get_brief_description(self, tool_name: str) -> str:
        """Get one-line description from information.json"""
        info_data = self._load_info_json(tool_name)
        if info_data:
            return info_data.get('tool_description', 'No description')
        return 'No description available'
    
    def _format_command(self, tool_name: str, cmd_info: dict) -> List[str]:
        """
        Format a single command with ALL its details
        FIXED: Now includes command name, description, format, and arguments
        """
        lines = []
        
        cmd_name = cmd_info.get('command', 'unknown')
        cmd_desc = cmd_info.get('description', 'No description')
        cmd_format = cmd_info.get('format', '')
        cmd_args = cmd_info.get('arguments', [])
        
        # Command header with description
        lines.append(f"**{cmd_name}**")
        lines.append(f"  - Description: {cmd_desc}")
        
        # Exact format to use
        if cmd_format:
            lines.append(f"  - Format: `{cmd_format}`")
        
        # Argument details (if provided in information.json)
        if cmd_args:
            lines.append(f"  - Arguments:")
            for arg in cmd_args:
                arg_name = arg.get('name', 'unknown')
                arg_type = arg.get('type', 'any')
                arg_desc = arg.get('description', '')
                arg_required = arg.get('required', False)
                
                req_str = " (required)" if arg_required else " (optional)"
                lines.append(f"    - `{arg_name}` ({arg_type}){req_str}: {arg_desc}")
        
        lines.append("")
        
        return lines
    
    def _build_no_tools_section(self) -> str:
        """Section for when no tools are enabled"""
        return """## NO TOOLS CURRENTLY AVAILABLE

You currently have no external tools available. Focus on:
- Internal reasoning and analysis
- Using available context and memory
- Providing thoughtful responses based on existing knowledge
"""
    
    def get_tool_summary(self) -> str:
        """Get brief summary of available tools"""
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        
        if not enabled_tools:
            return "No tools enabled"
        
        return f"{len(enabled_tools)} tools: {', '.join(enabled_tools)}"
    
    def validate_tool_action(self, action: dict) -> tuple[bool, str]:
        """Validate a tool action format"""
        # Check required fields
        if 'tool' not in action:
            return False, "Missing 'tool' field"
        
        if 'args' not in action:
            return False, "Missing 'args' field"
        
        if not isinstance(action['args'], list):
            return False, "'args' must be a list"
        
        # Parse tool name
        tool_call = action['tool']
        if '.' not in tool_call:
            return False, f"Tool format should be 'tool_name.command', got '{tool_call}'"
        
        tool_name = tool_call.split('.')[0]
        
        # Check if tool exists and is enabled
        enabled_tools = self.tool_manager.get_enabled_tool_names()
        if tool_name not in enabled_tools:
            available = ', '.join(enabled_tools) if enabled_tools else 'none'
            return False, f"Tool '{tool_name}' not enabled. Available: {available}"
        
        return True, "Valid"