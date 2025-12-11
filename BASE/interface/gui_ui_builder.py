# Filename: BASE/interface/gui_ui_builder.py
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_theme_manager import ThemeManager
from BASE.interface.gui_controls_view import ControlsView
from BASE.interface.gui_chat_view import ChatView
from BASE.interface.gui_coding_view import CodingView
from BASE.interface.gui_tools_view import ToolsView
from BASE.interface.gui_info_view import InfoView
from BASE.interface.gui_config_view import ConfigView  # NEW: Config editor
from BASE.interface.gui_theme_manager import DarkTheme
import personality.controls as controls

class UIBuilder:
    """Handles main UI creation and view switching for the GUI"""
    
    def __init__(self, parent):
        self.parent = parent
        # Set the default window size
        self.parent.root.geometry("770x870")
        self.theme_manager = ThemeManager(self.parent)
        self.controls_view = ControlsView(self.parent)
        self.chat_view = ChatView(self.parent)
        self.coding_view = CodingView(self.parent, self.parent.session_files_panel)
        self.tools_view = ToolsView(self.parent, project_root)
        self.info_view = InfoView(self.parent, project_root)
        self.config_view = ConfigView(self.parent, project_root)  # NEW: Config editor
        
    def setup_gui(self):
        self.theme_manager.apply_dark_theme()
        self.create_menu()
        self.create_main_frames()
        self.create_all_views()
        self.switch_view("Chat")  # Show Chat view by default

    def create_main_frames(self):
        # Create main container for all views
        self.parent.main_container = ttk.Frame(self.parent.root)
        self.parent.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frames for each view
        self.parent.controls_view = ttk.Frame(self.parent.main_container)
        self.parent.chat_view = ttk.Frame(self.parent.main_container)
        self.parent.coding_view = ttk.Frame(self.parent.main_container)
        self.parent.tools_view = ttk.Frame(self.parent.main_container)
        self.parent.info_view = ttk.Frame(self.parent.main_container)
        self.parent.config_view = ttk.Frame(self.parent.main_container)  # NEW
        
        # Store view frames for easy access
        self.view_frames = {
            "Config": self.parent.config_view,  # NEW: First in list
            "Controls": self.parent.controls_view,
            "Chat": self.parent.chat_view,
            "Coding": self.parent.coding_view,
            "Tools": self.parent.tools_view,
            "Info": self.parent.info_view
        }

    def create_all_views(self):
        """Create all view content"""
        self.config_view.create_config_view()  # NEW: Create config view first
        self.controls_view.create_controls_view()
        self.chat_view.create_chat_view()
        self.coding_view.create_coding_view()
        self.tools_view.create_tools_view()
        self.info_view.create_info_view()


    def create_menu(self):
        # Create a modern tab-style menu bar
        menubar_frame = tk.Frame(self.parent.root, bg=DarkTheme.BG_DARKER, height=40)
        menubar_frame.pack(side=tk.TOP, fill=tk.X)
        menubar_frame.pack_propagate(False)
        
        # Store the current view
        self.current_view = "Chat"  # Default to Chat view
        
        # Create tab buttons with responsive positioning using place
        tab_style = {
            'font': ("Segoe UI", 10),
            'relief': 'solid',
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2',
            'borderwidth': 2,
            'bg': DarkTheme.ACCENT_PURPLE,
            'fg': 'white',
            'highlightbackground': DarkTheme.ACCENT_PURPLE,
            'highlightcolor': DarkTheme.ACCENT_PURPLE,
            'activebackground': DarkTheme.ACCENT_PURPLE,
            'activeforeground': 'white'
        }
        
        # Create tabs with even spacing (6 tabs)
        self.config_tab = tk.Button(menubar_frame, text="Config", **tab_style,
                                    command=lambda: self.switch_view("Config"))
        self.config_tab.place(relx=0.083, rely=0.5, anchor=tk.CENTER)
        
        self.controls_tab = tk.Button(menubar_frame, text="Controls", **tab_style,
                                    command=lambda: self.switch_view("Controls"))
        self.controls_tab.place(relx=0.250, rely=0.5, anchor=tk.CENTER)
        
        self.chat_tab = tk.Button(menubar_frame, text="Chat", **tab_style,
                                command=lambda: self.switch_view("Chat"))
        self.chat_tab.place(relx=0.417, rely=0.5, anchor=tk.CENTER)
        
        self.coding_tab = tk.Button(menubar_frame, text="Coding", **tab_style,
                                    command=lambda: self.switch_view("Coding"))
        self.coding_tab.place(relx=0.583, rely=0.5, anchor=tk.CENTER)
        
        self.tools_tab = tk.Button(menubar_frame, text="Tools", **tab_style,
                                   command=lambda: self.switch_view("Tools"))
        self.tools_tab.place(relx=0.750, rely=0.5, anchor=tk.CENTER)
        
        self.info_tab = tk.Button(menubar_frame, text="Info", **tab_style,
                                  command=lambda: self.switch_view("Info"))
        self.info_tab.place(relx=0.917, rely=0.5, anchor=tk.CENTER)
        
        # Add NEW badge to Config tab
        config_badge = tk.Label(menubar_frame, text="NEW", 
                               bg=DarkTheme.ACCENT_GREEN, 
                               fg="white",
                               font=("Segoe UI", 7, "bold"),
                               padx=4, pady=1)
        config_badge.place(in_=self.config_tab, relx=0.85, rely=0.2)
        
        # Add NEW badge to Coding tab
        new_badge = tk.Label(menubar_frame, text="NEW", 
                            bg=DarkTheme.ACCENT_GREEN, 
                            fg="white",
                            font=("Segoe UI", 7, "bold"),
                            padx=4, pady=1)
        new_badge.place(in_=self.coding_tab, relx=0.85, rely=0.2)
        
        # Add NEW badge to Tools tab
        tools_badge = tk.Label(menubar_frame, text="NEW", 
                              bg=DarkTheme.ACCENT_GREEN, 
                              fg="white",
                              font=("Segoe UI", 7, "bold"),
                              padx=4, pady=1)
        tools_badge.place(in_=self.tools_tab, relx=0.85, rely=0.2)
        
        # Store tabs for styling
        self.tabs = {
            "Config": self.config_tab,  # NEW
            "Controls": self.controls_tab,
            "Chat": self.chat_tab,
            "Coding": self.coding_tab,
            "Tools": self.tools_tab,
            "Info": self.info_tab
        }
        
        # Set initial active tab
        self.update_tab_styles()

    def switch_view(self, view_name):
        """Switch between different views"""
        self.current_view = view_name
        self.update_tab_styles()
        
        # Hide all views
        for frame in self.view_frames.values():
            frame.pack_forget()
        
        # Show selected view
        self.view_frames[view_name].pack(fill=tk.BOTH, expand=True)
        
        # Force update to ensure content is rendered
        self.parent.root.update_idletasks()
        
        # Use logger instead of log_system_message
        # self.parent.logger.system(f"Switched to {view_name} view")

    def update_tab_styles(self):
        """Update tab button styles to show active tab"""
        from BASE.interface.gui_themes import DarkTheme
        for name, tab in self.tabs.items():
            if name == self.current_view:
                # Active tab: green background with white text
                tab.config(
                    bg=DarkTheme.ACCENT_GREEN,
                    fg='white',
                    font=("Segoe UI", 10, "bold"),
                    highlightbackground=DarkTheme.ACCENT_GREEN,
                    highlightcolor=DarkTheme.ACCENT_GREEN,
                    activebackground=DarkTheme.ACCENT_GREEN,
                    activeforeground='white'
                )
            else:
                # Inactive tabs: purple background with white text
                tab.config(
                    bg=DarkTheme.ACCENT_PURPLE,
                    fg='white',
                    font=("Segoe UI", 10),
                    highlightbackground=DarkTheme.ACCENT_PURPLE,
                    highlightcolor=DarkTheme.ACCENT_PURPLE,
                    activebackground=DarkTheme.ACCENT_PURPLE,
                    activeforeground='white'
                )


    def show_status_dialog(self):
        from BASE.interface.gui_themes import DarkTheme
        from tkinter import scrolledtext
        dialog = tk.Toplevel(self.parent.root)
        dialog.title("Current Status")
        dialog.configure(bg=DarkTheme.BG_DARK)
        dialog.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(
            dialog,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.config(state=tk.DISABLED)

    def validate_config(self):
        from tkinter import messagebox
        is_valid = self.parent.control_manager.validate_all_configs()
        if is_valid:
            messagebox.showinfo("Validation", "Configuration is valid!")
        else:
            messagebox.showwarning("Validation", "Configuration has issues. Check system log for details.")

    def export_settings(self):
        from tkinter import messagebox
        import json
        from datetime import datetime
        try:
            settings = self.parent.control_manager.get_all_features()
            filename = f"ai_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Export", f"Settings exported to {filename}")
            self.parent.logger.success(f"Settings exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export settings: {e}")
            self.parent.logger.error(f"Failed to export settings: {e}")

    def check_coding_status(self):
        from tkinter import messagebox
        """Show detailed coding tool status"""
        try:
            coding_tool = getattr(self.parent.ai_core, 'coding_tool', None)
            
            if not coding_tool:
                status_text = "Coding Tool Status: Not Initialized\n\n"
                status_text += "To enable:\n"
                status_text += "1. Set USE_CODING = True in controls.py\n"
                status_text += "2. Restart the application"
            else:
                is_available = coding_tool.is_available()
                status_text = f"Coding Tool Status: {'Connected' if is_available else 'Disconnected'}\n\n"
                status_text += f"Server URL: {coding_tool.server_url}\n"
                status_text += f"Timeout: {coding_tool.timeout}s\n"
                status_text += f"Auto-Execute: {'ON' if controls.USE_CODING else 'OFF'}\n"
                status_text += f"Include Context: {'ON' if controls.USE_CODING else 'OFF'}\n"
                
                if not is_available:
                    status_text += "\n\nTroubleshooting:\n"
                    status_text += "- Ensure VS Code is running\n"
                    status_text += "- Press F5 in VS Code to activate extension\n"
                    status_text += "- Check port 3000 is not blocked\n"
            
            messagebox.showinfo("Coding Tool Status", status_text)
            self.parent.logger.system(f"Coding tool status checked: {coding_tool is not None}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error checking coding status:\n{str(e)}")
            self.parent.logger.error(f"Error checking coding status: {e}")

    def test_coding_connection(self):
        from tkinter import messagebox
        """Test coding tool connection via menu"""
        if hasattr(self.parent, 'coding_panel_manager'):
            self.parent.coding_panel_manager.test_connection()
        else:
            messagebox.showwarning("Not Available", "Coding panel manager not initialized")
            self.parent.logger.warning("Coding panel manager not initialized")

    def toggle_auto_execute(self):
        from tkinter import messagebox
        """Toggle auto-execution of coding tasks"""
        try:
            current = controls.USE_CODING
            new_value = self.parent.ai_core.toggle_control_setting("USE_CODING")

            if new_value is not None:
                status = "enabled" if new_value else "disabled"
                self.parent.logger.system(f"Auto-execute coding tasks: {status}")
                messagebox.showinfo(
                    "Auto-Execute Toggled",
                    f"Auto-execution of coding tasks is now {status}"
                )
            else:
                messagebox.showerror("Error", "Failed to toggle auto-execute setting")
                self.parent.logger.error("Failed to toggle auto-execute setting")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling auto-execute:\n{str(e)}")
            self.parent.logger.error(f"Error toggling auto-execute: {e}")