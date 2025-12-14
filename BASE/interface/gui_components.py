# Filename: BASE/interface/gui_components.py
"""
Component managers for control panel functionality.
REFACTORED: Dynamic tool discovery from new modular system
Works with BASE/tools/installed/ filesystem-based tool discovery
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

from BASE.interface.gui_themes import DarkTheme

try:
    import personality.controls as controls
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")


class ControlPanelManager:
    """
    Manages the control panel GUI with dynamic tool discovery
    All control logic delegated to AI Core's ControlManager
    Tool system updates delegated to ToolManager (modular system)
    """

    def __init__(self, ai_core, logger):
        """Initialize control panel manager"""
        self.ai_core = ai_core
        self.control_manager = ai_core.get_control_manager()
        self.logger = logger

        self.control_vars = {}
        self.status_labels = {}
        
        # Initialize TTS backend switcher
        self.tts_backend_switcher = None
        self._init_tts_backend_switcher()

    def _init_tts_backend_switcher(self):
        """Initialize TTS backend switcher with diagnostics"""
        try:
            
            self.logger.system("TTS BACKEND SWITCHER INITIALIZATION")
            
            
            self.logger.system("[1/4] Importing TTSBackendSwitcher...")
            from BASE.tools.internal.voice.tts_backend_switcher import TTSBackendSwitcher
            self.logger.system("  Import successful")
            
            self.logger.system("[2/4] Verifying AI Core controls module...")
            if not hasattr(self.ai_core, 'controls'):
                raise RuntimeError("AI Core missing 'controls' attribute")
            if self.ai_core.controls is None:
                raise RuntimeError("AI Core controls is None")
            self.logger.system(f"  Controls module present: {id(self.ai_core.controls)}")
            
            self.logger.system("[3/4] Creating TTSBackendSwitcher instance...")
            self.tts_backend_switcher = TTSBackendSwitcher(self.ai_core, self.logger)
            
            self.logger.system("[4/4] Verifying controls capture...")
            if not self.tts_backend_switcher.controls_module:
                raise RuntimeError("Switcher failed to capture controls module")
            
            if id(self.tts_backend_switcher.controls_module) != id(self.ai_core.controls):
                self.logger.warning("Controls module IDs don't match (may be OK)")
            
            self.logger.system(f"  Switcher controls: {id(self.tts_backend_switcher.controls_module)}")
            
            
            self.logger.speech("TTS backend switcher initialized successfully")
            
                
        except Exception as e:
            
            self.logger.error(f"TTS backend switcher initialization FAILED")
            self.logger.error(f"Error: {e}")
            
            
            import traceback
            traceback.print_exc()
            
            self.tts_backend_switcher = None

    def toggle_control(self, var_name):
            """Toggle a control via AI Core"""
            
            # ====================================================================
            # SPECIAL CASE 1: AVATAR_SPEECH Toggle
            # ====================================================================
            if var_name == "AVATAR_SPEECH":
                # Toggle the control
                new_value = self.ai_core.control_manager.toggle_feature(var_name)
                
                if new_value is None:
                    self.logger.error("Failed to toggle AVATAR_SPEECH")
                    return
                
                # Update GUI immediately
                self.control_vars[var_name].set(new_value)
                self.status_labels[var_name].config(
                    text="ON" if new_value else "OFF",
                    foreground=DarkTheme.ACCENT_GREEN if new_value else DarkTheme.FG_MUTED,
                )
                
                # If enabling, check if TTS tool exists and is available
                if new_value:
                    if not hasattr(self.ai_core, 'tts_tool') or not self.ai_core.tts_tool:
                        self.logger.error("[FAILED] TTS tool not initialized")
                        self.logger.error("   Recommendation: Restart application with AVATAR_SPEECH enabled")
                        self.logger.error("   Or ensure _setup_tts_tool() initializes even when disabled")
                        
                        # Revert GUI change
                        self.control_vars[var_name].set(False)
                        self.status_labels[var_name].config(
                            text="OFF",
                            foreground=DarkTheme.FG_MUTED,
                        )
                        setattr(controls, var_name, False)
                        return
                    
                    # Check TTS availability
                    if not self.ai_core.tts_tool.is_available():
                        self.logger.error("[FAILED] TTS tool exists but is not available")
                        
                        # Revert
                        self.control_vars[var_name].set(False)
                        self.status_labels[var_name].config(
                            text="OFF",
                            foreground=DarkTheme.FG_MUTED,
                        )
                        setattr(controls, var_name, False)
                        return
                    
                    # Success - TTS enabled
                    info = self.ai_core.tts_tool.get_voice_info()
                    self.logger.speech(f"[SUCCESS] TTS enabled: {info.get('name')} ({info.get('type')})")
                    if 'volume_percent' in info:
                        self.logger.speech(f"  Volume: {info['volume_percent']}")
                else:
                    # TTS disabled
                    self.logger.speech("[INFO] TTS disabled")
                
                # Update controls module
                setattr(controls, var_name, new_value)
                
                # Notify tool manager
                if hasattr(self.ai_core, 'tool_manager'):
                    self.ai_core.tool_manager.handle_control_update(var_name, new_value)
                
                return
            
            # ====================================================================
            # SPECIAL CASE 2: USE_CUSTOM_VOICE Toggle
            # ====================================================================
            if var_name == "USE_CUSTOM_VOICE":
                if not getattr(controls, 'AVATAR_SPEECH', False):
                    self.logger.warning("Enable AVATAR_SPEECH first")
                    return
                
                if not self.tts_backend_switcher:
                    self.logger.error("TTS backend switcher not initialized")
                    self.logger.error("Recommendation: Restart application")
                    return
                
                if not self.tts_backend_switcher.controls_module:
                    self.logger.error("TTS backend switcher missing controls module")
                    return
                
                # Get new value from toggle
                new_value = self.ai_core.control_manager.toggle_feature(var_name)
        
                if new_value is None:
                    self.logger.error("Failed to toggle USE_CUSTOM_VOICE")
                    return
                
                # Update GUI controls BEFORE switching backend
                self.control_vars[var_name].set(new_value)
                self.status_labels[var_name].config(
                    text="ON" if new_value else "OFF",
                    foreground=DarkTheme.ACCENT_GREEN if new_value else DarkTheme.FG_MUTED,
                )
                
                # Determine backend name
                backend_name = "Custom Voice (XTTS)" if new_value else "System Voice (pyttsx3)"
                
                self.logger.speech(f"Switching to {backend_name}...")
                
                # Perform backend switch
                success = self.tts_backend_switcher.switch_backend(new_value)
                
                if success:
                    # Update controls module
                    setattr(controls, var_name, new_value)
                    
                    # Log backend info
                    if hasattr(self.ai_core, 'tts_tool') and self.ai_core.tts_tool:
                        info = self.ai_core.tts_tool.get_voice_info()
                        self.logger.speech(f"  Active backend: {info.get('name', 'Unknown')}")
                        
                        if 'volume_percent' in info:
                            self.logger.speech(f"  Volume: {info['volume_percent']}")
                        
                        if hasattr(self, 'tts_status_label'):
                            self.tts_status_label.config(
                                text=f"Status: Ready ({info.get('type', 'Unknown')})",
                                foreground=DarkTheme.ACCENT_GREEN
                            )
                else:
                    # Backend switch failed - revert GUI
                    self.control_vars[var_name].set(not new_value)
                    self.status_labels[var_name].config(
                        text="ON" if (not new_value) else "OFF",
                        foreground=DarkTheme.ACCENT_GREEN if (not new_value) else DarkTheme.FG_MUTED,
                    )
                    
                    self.logger.error(f"Failed to switch to {backend_name}")
                    
                    if hasattr(self, 'tts_status_label'):
                        self.tts_status_label.config(
                            text="Status: Switch Failed",
                            foreground=DarkTheme.ACCENT_RED
                        )
                
                # Notify tool manager
                if hasattr(self.ai_core, 'tool_manager'):
                    self.ai_core.tool_manager.handle_control_update(
                        var_name, new_value if success else (not new_value)
                    )
                
                return
            
            # ====================================================================
            # REGULAR CONTROLS: Standard Toggle Logic
            # ====================================================================
            new_value = self.ai_core.control_manager.toggle_feature(var_name)
            
            if new_value is not None:
                self.control_vars[var_name].set(new_value)
                self.status_labels[var_name].config(
                    text="ON" if new_value else "OFF",
                    foreground=DarkTheme.ACCENT_GREEN if new_value else DarkTheme.FG_MUTED,
                )

                # Notify tool execution manager of control change
                if hasattr(self.ai_core, 'tool_manager'):
                    self.ai_core.tool_manager.handle_control_update(var_name, new_value)
                    if new_value:
                        self.logger.system(f"{var_name} enabled")
                    else:
                        self.logger.system(f"{var_name} disabled")

                # Special logging for LIMIT_PROCESSING
                if var_name == "LIMIT_PROCESSING":
                    if new_value:
                        delay = getattr(controls, 'DELAY_TIMER', 30)
                        self.logger.system(f"Processing limited - {delay}s delay per cycle")
                    else:
                        self.logger.system("Processing speed normal - adaptive pacing")
            else:
                self.logger.error(f"Failed to toggle control: {var_name}")

    def create_control_panel(self, parent_frame):
        """Create comprehensive control panel with dynamic tools"""

        container_frame = ttk.Frame(parent_frame)
        container_frame.pack(fill=tk.BOTH, expand=True)

        control_canvas = tk.Canvas(
            container_frame, bg=DarkTheme.BG_DARK, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container_frame, orient="vertical", command=control_canvas.yview
        )
        scrollable_frame = ttk.Frame(control_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: control_canvas.configure(scrollregion=control_canvas.bbox("all")),
        )

        canvas_window = control_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw"
        )
        control_canvas.configure(yscrollcommand=scrollbar.set)

        def configure_scroll_region(event):
            control_canvas.configure(scrollregion=control_canvas.bbox("all"))
            control_canvas.itemconfig(canvas_window, width=event.width)

        control_canvas.bind("<Configure>", configure_scroll_region)

        control_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event):
            control_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event):
            control_canvas.unbind_all("<MouseWheel>")

        control_canvas.bind("<Enter>", _bind_mousewheel)
        control_canvas.bind("<Leave>", _unbind_mousewheel)

        # STATIC control groups (non-tool controls)
        static_control_groups = {
            "AI Behavior": [
                ("Continuous Thinking", "ENABLE_CONTINUOUS_THINKING",
                "Enable continuous thought processing"),
                ("Slow Mode", "LIMIT_PROCESSING",
                "Add delay to agent's processing loop"),
            ],
            "Agent Memory": [
                ("Base Memory", "USE_BASE_MEMORY", "Include base knowledge context"),
                ("Short Memory", "USE_SHORT_MEMORY", "Include working memory (latest messages)"),
                ("Long Memory", "USE_LONG_MEMORY", "Include past day summaries"),
                ("Save Memory", "SAVE_MEMORY", "Save conversations to memory system"),
            ],
            "Prompt Components": [
                ("System Prompt", "USE_SYSTEM_PROMPT", "Include system/personality prompt")
            ],
            "Output Actions": [
                ("TTS Speech", "AVATAR_SPEECH", "Enable text-to-speech"),
                ("Custom Voice", "USE_CUSTOM_VOICE", "Use voice cloning instead of system TTS")
            ],
            "Filters": [
                ("Content Filter", "ENABLE_CONTENT_FILTER",
                "Filter profanity and controversial content"),
                ("AI Filter", "USE_AI_CONTENT_FILTER",
                "Use AI model for semantic filtering")
            ],
            "Debug & Logging": [
                ("Log System", "LOG_SYSTEM_INFORMATION", "Log system messages"),
                ("Log Prompts", "LOG_PROMPT_CONSTRUCTION", "Log prompt building"),
                ("Log Responses", "LOG_RESPONSE_PROCESSING", "Log response generation"),
                ("Log Tools", "LOG_TOOL_EXECUTION", "Log tool executions"),
                ("Log Live Chat", "SHOW_CHAT", "Print live chat messages"),
            ],
        }

        # Create static control sections
        for group_name, controls_list in static_control_groups.items():
            self.create_control_group(scrollable_frame, group_name, controls_list)

        # Create dynamic tool sections
        dynamic_tool_groups = self._get_dynamic_tool_groups()
        for category_name, tools_list in dynamic_tool_groups.items():
            self.create_dynamic_tool_group(scrollable_frame, category_name, tools_list)

        # Global control buttons
        global_frame = ttk.LabelFrame(
            scrollable_frame, text="Global Controls", style="Dark.TLabelframe"
        )
        global_frame.pack(fill=tk.X, padx=3, pady=1)

        button_frame = ttk.Frame(global_frame)
        button_frame.pack(fill=tk.X, padx=3, pady=2)

        ttk.Button(
            button_frame, text="Enable All", command=self.enable_all_controls, width=10
        ).pack(side=tk.LEFT, padx=1)
        ttk.Button(
            button_frame, text="Disable All", command=self.disable_all_controls, width=10
        ).pack(side=tk.LEFT, padx=1)
        ttk.Button(
            button_frame, text="Reset", command=self.reset_controls, width=10
        ).pack(side=tk.LEFT, padx=1)

        # Add status sections
        self.create_tts_status_section(scrollable_frame)

    def _get_dynamic_tool_groups(self) -> Dict[str, List[Tuple]]:
        """
        Get dynamically discovered tools grouped by category
        REFACTORED: Works with new filesystem-based tool discovery
        
        Returns:
            Dict mapping category names to list of tool info tuples
        """
        if not hasattr(self.ai_core, 'tool_manager'):
            self.logger.warning("No tool execution manager - dynamic tools unavailable")
            return {}
        
        tool_manager = self.ai_core.tool_manager
        
        try:
            # Get tools directory
            project_root = Path(__file__).parent.parent.parent
            tools_dir = project_root / 'BASE' / 'tools' / 'installed'
            
            if not tools_dir.exists():
                self.logger.warning(f"Tools directory not found: {tools_dir}")
                return {}
            
            # Discover tools from filesystem
            discovered_tools = []
            
            for tool_dir in tools_dir.iterdir():
                if not tool_dir.is_dir():
                    continue
                
                info_file = tool_dir / 'information.json'
                if not info_file.exists():
                    continue
                
                try:
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                    
                    tool_name = info.get('tool_name')
                    control_var = info.get('control_variable_name')
                    
                    if not tool_name or not control_var:
                        continue
                    
                    # Extract metadata
                    metadata = info.get('metadata', {})
                    category = metadata.get('category', 'Other Tools')
                    display_name = metadata.get('gui_label', 
                                               tool_name.replace('_', ' ').title())
                    description = info.get('tool_description', 'No description')
                    
                    discovered_tools.append({
                        'tool_name': tool_name,
                        'control_var': control_var,
                        'category': category,
                        'display_name': display_name,
                        'description': description,
                        'info': info
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load tool from {tool_dir.name}: {e}")
                    continue
            
            # Group by category
            categories = {}
            for tool in discovered_tools:
                category = tool['category']
                
                if category not in categories:
                    categories[category] = []
                
                # Build tuple for GUI
                categories[category].append((
                    tool['display_name'],    # For checkbox label
                    tool['control_var'],     # For control binding
                    tool['description'],     # For tooltip
                    tool['tool_name'],       # For identification
                    tool['info']            # Full metadata
                ))
            
            self.logger.system(
                f"Loaded {len(discovered_tools)} dynamic tools in "
                f"{len(categories)} categories"
            )
            
            return categories
            
        except Exception as e:
            self.logger.error(f"Failed to load dynamic tools: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def create_dynamic_tool_group(self, parent, category_name: str, tools_list):
        """
        Create GUI section for dynamically discovered tools
        
        Args:
            parent: Parent frame
            category_name: Category display name
            tools_list: List of (display_name, control_var, description, tool_name, info) tuples
        """
        group_frame = ttk.LabelFrame(
            parent, 
            text=f"{category_name}", 
            style="Dark.TLabelframe"
        )
        group_frame.pack(fill=tk.X, padx=3, pady=1)
        
        # Add info label for dynamic tools
        info_label = tk.Label(
            group_frame,
            text="🔌 Modular tools - auto-discovered from filesystem",
            font=("Segoe UI", 8, "italic"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
        )
        info_label.pack(fill=tk.X, padx=3, pady=2)
        
        for tool_data in tools_list:
            display_name, var_name, description, tool_name, tool_info = tool_data
            self._create_dynamic_tool_control(
                group_frame, 
                display_name, 
                var_name, 
                description,
                tool_name
            )

    def _create_dynamic_tool_control(
        self, 
        parent, 
        display_name: str, 
        var_name: str, 
        description: str,
        tool_name: str
    ):
        """
        Create individual control for a dynamic tool
        
        Args:
            parent: Parent frame
            display_name: Human-readable name
            var_name: Control variable name
            description: Tool description
            tool_name: Tool identifier name
        """
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=2, pady=0)
        
        # Get current value - create if doesn't exist
        if not hasattr(controls, var_name):
            setattr(controls, var_name, False)
            self.logger.system(f"Created missing control variable: {var_name}")
        
        current_value = getattr(controls, var_name, False)
        bool_var = tk.BooleanVar(value=current_value)
        self.control_vars[var_name] = bool_var
        
        # Create checkbox
        checkbox = ttk.Checkbutton(
            control_frame,
            text=display_name,
            variable=bool_var,
            command=lambda vn=var_name: self.toggle_control(vn),
        )
        checkbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create status label
        status_color = (
            DarkTheme.ACCENT_GREEN if current_value 
            else DarkTheme.FG_MUTED
        )
        status_label = tk.Label(
            control_frame,
            text="ON" if current_value else "OFF",
            font=("Segoe UI", 8, "bold"),
            foreground=status_color,
            background=DarkTheme.BG_DARKER,
            width=4,
        )
        status_label.pack(side=tk.RIGHT, padx=1)
        self.status_labels[var_name] = status_label
        
        # Add tooltip
        if description:
            full_description = f"{description}\n\n[Modular Tool: {tool_name}]"
            self.create_tooltip(checkbox, full_description)

    def create_control_group(self, parent, group_name, controls_list):
        """Create a standard control group"""
        group_frame = ttk.LabelFrame(parent, text=group_name, style="Dark.TLabelframe")
        group_frame.pack(fill=tk.X, padx=3, pady=1)
        
        # Define logging controls (stored in Config, not controls module)
        logging_controls = {
            'LOG_TOOL_EXECUTION', 'LOG_PROMPT_CONSTRUCTION',
            'LOG_RESPONSE_PROCESSING', 'LOG_SYSTEM_INFORMATION', 'SHOW_CHAT'
        }

        for display_name, var_name, description in controls_list:
            control_frame = ttk.Frame(group_frame)
            control_frame.pack(fill=tk.X, padx=2, pady=0)
            
            # Read current value from appropriate source
            if var_name in logging_controls:
                # Logging controls: read from Config
                current_value = getattr(self.ai_core.config, var_name, False)
            else:
                # Other controls: read from controls module
                current_value = getattr(controls, var_name, False)
            
            bool_var = tk.BooleanVar(value=current_value)
            self.control_vars[var_name] = bool_var

            checkbox = ttk.Checkbutton(
                control_frame,
                text=display_name,
                variable=bool_var,
                command=lambda vn=var_name: self.toggle_control(vn),
            )
            checkbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

            status_color = (
                DarkTheme.ACCENT_GREEN if current_value else DarkTheme.FG_MUTED
            )
            status_label = tk.Label(
                control_frame,
                text="ON" if current_value else "OFF",
                font=("Segoe UI", 8, "bold"),
                foreground=status_color,
                background=DarkTheme.BG_DARKER,
                width=4,
            )
            status_label.pack(side=tk.RIGHT, padx=1)
            self.status_labels[var_name] = status_label

            if description:
                self.create_tooltip(checkbox, description)
                
    def create_tts_status_section(self, parent):
        """Create TTS tool status section"""
        tts_frame = ttk.LabelFrame(
            parent, text="TTS System", style="Dark.TLabelframe"
        )
        tts_frame.pack(fill=tk.X, padx=3, pady=1)

        tts_controls = ttk.Frame(tts_frame)
        tts_controls.pack(fill=tk.X, padx=3, pady=2)

        self.tts_status_label = tk.Label(
            tts_controls,
            text="Status: Checking...",
            font=("Segoe UI", 8),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARK,
        )
        self.tts_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            tts_controls,
            text="Test",
            command=self.test_tts,
            width=10,
        ).pack(side=tk.RIGHT, padx=1)
        
        ttk.Button(
            tts_controls,
            text="Refresh",
            command=self.check_tts_status,
            width=10,
        ).pack(side=tk.RIGHT, padx=1)

        self.check_tts_status()

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""

        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tooltip.configure(bg=DarkTheme.BG_DARK)

            label = tk.Label(
                tooltip,
                text=text,
                background=DarkTheme.BG_DARK,
                foreground=DarkTheme.FG_PRIMARY,
                font=("Segoe UI", 9),
                wraplength=300,
                padx=8,
                pady=4,
            )
            label.pack()

            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def update_control_display(self):
        """Update all control displays"""
        for var_name, bool_var in self.control_vars.items():
            current_value = getattr(controls, var_name, False)
            bool_var.set(current_value)
            if var_name in self.status_labels:
                self.status_labels[var_name].config(
                    text="ON" if current_value else "OFF",
                    foreground=(
                        DarkTheme.ACCENT_GREEN if current_value else DarkTheme.FG_MUTED
                    ),
                )

    def enable_all_controls(self):
        """Enable all controls"""
        for var_name in self.control_vars:
            self.ai_core.control_manager.set_feature(var_name, True)
        self.update_control_display()
        self.logger.system("All controls enabled")

    def disable_all_controls(self):
        """Disable all controls"""
        for var_name in self.control_vars:
            self.ai_core.control_manager.set_feature(var_name, False)
        self.update_control_display()
        self.logger.system("All controls disabled")

    def reset_controls(self):
        """Reset controls to defaults"""
        self.ai_core.control_manager.reset_to_defaults()
        self.update_control_display()
        self.logger.system("Controls reset to defaults")

    def check_tts_status(self):
        """Check TTS tool status (TTS is still in internal/passive system)"""
        try:
            if not hasattr(self.ai_core, 'tts_tool') or not self.ai_core.tts_tool:
                self.tts_status_label.config(
                    text="Status: Not Configured",
                    foreground=DarkTheme.FG_MUTED
                )
                return
            
            available = self.ai_core.tts_tool.is_available()
            
            if available:
                info = self.ai_core.tts_tool.get_voice_info()
                voice_type = info.get('type', 'Unknown')
                voice_name = info.get('name', 'Unknown')
                
                status_text = f"Status: Ready ({voice_type})"
                status_color = DarkTheme.ACCENT_GREEN
                self.logger.system(f"[TTS] {status_text} - {voice_name}")
            else:
                status_text = "Status: Not Available"
                status_color = DarkTheme.ACCENT_RED
            
            self.tts_status_label.config(
                text=status_text,
                foreground=status_color
            )
            
        except Exception as e:
            self.tts_status_label.config(
                text=f"Status: Error - {str(e)[:30]}",
                foreground=DarkTheme.ACCENT_RED
            )
            self.logger.error(f"Error checking TTS status: {e}")
    
    def test_tts(self):
        """Test TTS with sample phrase"""
        try:
            if not hasattr(self.ai_core, 'tts_tool') or not self.ai_core.tts_tool:
                self.logger.warning("TTS tool not configured")
                return
            
            if not self.ai_core.tts_tool.is_available():
                self.logger.warning("TTS tool not available")
                return
            
            self.logger.system("Testing TTS...")
            
            test_phrase = "Hello! This is a TTS system test."
            
            import threading
            
            def speak_test():
                result = self.ai_core.tts_tool.speak(test_phrase, stream=False)
                if "completed" in result.lower():
                    self.logger.system("TTS test successful")
                else:
                    self.logger.warning(f"TTS test result: {result}")
            
            thread = threading.Thread(target=speak_test, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error testing TTS: {e}")
            import traceback
            traceback.print_exc()