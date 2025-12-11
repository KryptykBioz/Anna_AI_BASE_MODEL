# Filename: BASE/interface/gui_tools_view.py
"""
Dynamic Tools View - Creates GUI pages for installed tool components
Uses nested tabs - each tool gets its own dedicated tab
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from BASE.interface.gui_themes import DarkTheme
from BASE.interface.dynamic_tool_panel_loader import DynamicToolPanelLoader


class ToolsView:
    """
    Manages the Tools view with dynamically loaded tool panels
    Each installed tool with a component.py gets its own tab
    """
    
    def __init__(self, parent, project_root):
        """
        Initialize tools view
        
        Args:
            parent: Parent GUI instance
            project_root: Project root path
        """
        self.parent = parent
        self.project_root = project_root
        
        # Panel loader
        self.panel_loader = DynamicToolPanelLoader(
            project_root=project_root,
            logger=parent.logger
        )
        
        # GUI elements
        self.notebook = None
        self.tool_tabs: Dict[str, ttk.Frame] = {}
        self.tool_components: Dict[str, Any] = {}
    
    def create_tools_view(self):
        """
        Create the Tools view with nested tabs for each tool
        
        Returns:
            Main frame containing notebook with individual tool tabs
        """
        # Main container
        main_container = ttk.Frame(self.parent.tools_view)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with info
        self._create_header(main_container)
        
        # Notebook for individual tool tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Discover and create tool panels (each tool gets its own tab)
        self._discover_and_create_panels()
        
        return main_container
    
    def _create_header(self, parent):
        """Create header with information"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🔧 Tool Panels",
            font=("Segoe UI", 11, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER
        )
        title_label.pack(side=tk.LEFT)
        
        # Info text
        info_label = tk.Label(
            header_frame,
            text="Each tool in its own tab • Auto-discovered from BASE/tools/installed/",
            font=("Segoe UI", 8, "italic"),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Refresh button
        refresh_button = ttk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_panels,
            width=12
        )
        refresh_button.pack(side=tk.RIGHT)
    
    def _discover_and_create_panels(self):
        """Discover tools and create individual tabs for those with components"""
        # Discover all tool panels
        panels = self.panel_loader.discover_tool_panels()
        
        if not panels:
            self._create_no_tools_message()
            return
        
        # Filter to only tools with components
        tools_with_components = [p for p in panels if p['has_component']]
        
        if not tools_with_components:
            self._create_no_components_message()
            return
        
        # Sort by display name, handling None values
        # FIX: Provide fallback for None display_name
        tools_with_components.sort(key=lambda x: x['display_name'] or x['tool_name'] or '')
        
        # Create individual tab for each tool
        for panel_info in tools_with_components:
            self._create_tool_tab(panel_info)
        
        # Log summary
        self.parent.logger.system(
            f"[Tools View] Created {len(tools_with_components)} tool tab(s)"
        )
    
    def _create_tool_tab(self, panel_info: Dict):
        """
        Create an individual tab for a single tool
        
        Args:
            panel_info: Tool panel metadata dict
        """
        tool_name = panel_info['tool_name']
        display_name = panel_info['display_name'] or tool_name.replace('_', ' ').title()
        icon = panel_info.get('icon', '🔧')
        component_path = panel_info['component_path']
        
        # Create tab frame with scrolling support
        tab_frame = ttk.Frame(self.notebook)
        
        # Add tab with icon and name
        tab_label = f"{icon} {display_name}"
        self.notebook.add(tab_frame, text=tab_label)
        
        # Create scrollable container for the tool panel
        canvas = tk.Canvas(tab_frame, bg=DarkTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configure canvas to expand with window
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", configure_scroll_region)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Load and create the tool's component panel
        self._load_tool_component(scrollable_frame, panel_info)
    
    def _load_tool_component(self, parent, panel_info: Dict):
        """
        Load and create a tool's component in the given parent frame
        
        Args:
            parent: Parent frame
            panel_info: Tool panel metadata dict
        """
        tool_name = panel_info['tool_name']
        component_path = panel_info['component_path']
        
        # Load component
        component = self.panel_loader.load_component(
            tool_name=tool_name,
            component_path=component_path,
            parent_gui=self.parent,
            ai_core=self.parent.ai_core
        )
        
        if not component:
            self.parent.logger.warning(
                f"[Tools View] Failed to load component for {tool_name}"
            )
            self._create_error_panel(parent, tool_name)
            return
        
        # Create panel frame
        try:
            panel_frame = component.create_panel(parent)
            
            # Store references
            self.tool_tabs[tool_name] = panel_frame
            self.tool_components[tool_name] = component
            
            self.parent.logger.system(
                f"[Tools View] Loaded tab for {tool_name}"
            )
        
        except Exception as e:
            self.parent.logger.error(
                f"[Tools View] Error creating panel for {tool_name}: {e}"
            )
            import traceback
            traceback.print_exc()
            self._create_error_panel(parent, tool_name, str(e))
    
    def _create_error_panel(self, parent, tool_name: str, error_msg: str = ""):
        """Create error message panel for failed tool loads"""
        error_frame = ttk.LabelFrame(
            parent,
            text=f"❌ Error Loading {tool_name}",
            style="Dark.TLabelframe"
        )
        error_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        error_text = f"Failed to load component for {tool_name}"
        if error_msg:
            error_text += f"\n\nError: {error_msg}"
        
        error_label = tk.Label(
            error_frame,
            text=error_text,
            font=("Segoe UI", 10),
            foreground=DarkTheme.ACCENT_RED,
            background=DarkTheme.BG_DARKER,
            justify=tk.LEFT,
            wraplength=500
        )
        error_label.pack(expand=True, padx=20, pady=20)
    
    def _create_no_tools_message(self):
        """Create message when no tools are installed"""
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="No Tools")
        
        message_label = tk.Label(
            message_frame,
            text="No tools found in BASE/tools/installed/",
            font=("Segoe UI", 10),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        message_label.pack(expand=True)
    
    def _create_no_components_message(self):
        """Create message when no tool components are available"""
        message_frame = ttk.Frame(self.notebook)
        self.notebook.add(message_frame, text="No Components")
        
        message_label = tk.Label(
            message_frame,
            text=(
                "Tools are installed but none have GUI components.\n\n"
                "To add a GUI component, create a component.py file\n"
                "in the tool's directory with a create_component() function."
            ),
            font=("Segoe UI", 10),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
            justify=tk.CENTER
        )
        message_label.pack(expand=True)
    
    def _refresh_panels(self):
        """Refresh all tool panels (reload discovery)"""
        self.parent.logger.system("[Tools View] Refreshing tool panels...")
        
        # Cleanup existing components
        for component in self.tool_components.values():
            if hasattr(component, 'cleanup'):
                try:
                    component.cleanup()
                except Exception as e:
                    self.parent.logger.warning(
                        f"[Tools View] Error cleaning up component: {e}"
                    )
        
        # Clear references
        self.tool_tabs.clear()
        self.tool_components.clear()
        
        # Clear notebook tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Re-discover and create individual tool tabs
        self._discover_and_create_panels()
        
        self.parent.logger.success("[Tools View] Tool panels refreshed")
    
    def cleanup(self):
        """Cleanup all tool components"""
        self.panel_loader.cleanup_all()
        self.tool_tabs.clear()
        self.tool_components.clear()