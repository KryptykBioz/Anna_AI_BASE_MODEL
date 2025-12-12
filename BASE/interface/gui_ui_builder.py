# Filename: BASE/interface/gui_ui_builder.py
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_theme_manager import ThemeManager
from BASE.interface.gui_controls_view import ControlsView
from BASE.interface.gui_chat_view import ChatView
from BASE.interface.gui_tools_view import ToolsView
from BASE.interface.gui_info_view import InfoView
from BASE.interface.gui_config_view import ConfigView
from BASE.interface.gui_theme_manager import DarkTheme
import personality.controls as controls

class UIBuilder:
    """Handles main UI creation and view switching for the GUI"""
    
    def __init__(self, parent):
        self.parent = parent
        self.parent.root.geometry("770x870")
        self.theme_manager = ThemeManager(self.parent)
        self.controls_view = ControlsView(self.parent)
        self.chat_view = ChatView(self.parent)
        self.tools_view = ToolsView(self.parent, project_root)
        self.info_view = InfoView(self.parent, project_root)
        self.config_view = ConfigView(self.parent, project_root)
        
    def setup_gui(self):
        self.theme_manager.apply_dark_theme()
        self.create_menu()
        self.create_main_frames()
        self.create_all_views()
        self.switch_view("Chat")

    def create_main_frames(self):
        """Create main container and view frames"""
        self.parent.main_container = ttk.Frame(self.parent.root)
        self.parent.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frames for each view (removed coding_view)
        self.parent.controls_view = ttk.Frame(self.parent.main_container)
        self.parent.chat_view = ttk.Frame(self.parent.main_container)
        self.parent.tools_view = ttk.Frame(self.parent.main_container)
        self.parent.info_view = ttk.Frame(self.parent.main_container)
        self.parent.config_view = ttk.Frame(self.parent.main_container)
        
        # Store view frames for easy access
        self.view_frames = {
            "Config": self.parent.config_view,
            "Controls": self.parent.controls_view,
            "Chat": self.parent.chat_view,
            "Tools": self.parent.tools_view,
            "Info": self.parent.info_view
        }

    def create_all_views(self):
        """Create all view content"""
        self.config_view.create_config_view()
        self.controls_view.create_controls_view()
        self.chat_view.create_chat_view()
        self.tools_view.create_tools_view()
        self.info_view.create_info_view()

    def create_menu(self):
        """Create tab-style menu bar (removed Coding tab)"""
        menubar_frame = tk.Frame(self.parent.root, bg=DarkTheme.BG_DARKER, height=40)
        menubar_frame.pack(side=tk.TOP, fill=tk.X)
        menubar_frame.pack_propagate(False)
        
        self.current_view = "Chat"
        
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
        
        # Create tabs with even spacing (5 tabs now)
        self.config_tab = tk.Button(menubar_frame, text="Config", **tab_style,
                                    command=lambda: self.switch_view("Config"))
        self.config_tab.place(relx=0.1, rely=0.5, anchor=tk.CENTER)
        
        self.controls_tab = tk.Button(menubar_frame, text="Controls", **tab_style,
                                    command=lambda: self.switch_view("Controls"))
        self.controls_tab.place(relx=0.3, rely=0.5, anchor=tk.CENTER)
        
        self.chat_tab = tk.Button(menubar_frame, text="Chat", **tab_style,
                                command=lambda: self.switch_view("Chat"))
        self.chat_tab.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.tools_tab = tk.Button(menubar_frame, text="Tools", **tab_style,
                                   command=lambda: self.switch_view("Tools"))
        self.tools_tab.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
        
        self.info_tab = tk.Button(menubar_frame, text="Info", **tab_style,
                                  command=lambda: self.switch_view("Info"))
        self.info_tab.place(relx=0.9, rely=0.5, anchor=tk.CENTER)
        
        # Add NEW badge to Config tab
        config_badge = tk.Label(menubar_frame, text="NEW", 
                               bg=DarkTheme.ACCENT_GREEN, 
                               fg="white",
                               font=("Segoe UI", 7, "bold"),
                               padx=4, pady=1)
        config_badge.place(in_=self.config_tab, relx=0.85, rely=0.2)
        
        # Add NEW badge to Tools tab
        tools_badge = tk.Label(menubar_frame, text="NEW", 
                              bg=DarkTheme.ACCENT_GREEN, 
                              fg="white",
                              font=("Segoe UI", 7, "bold"),
                              padx=4, pady=1)
        tools_badge.place(in_=self.tools_tab, relx=0.85, rely=0.2)
        
        # Store tabs for styling
        self.tabs = {
            "Config": self.config_tab,
            "Controls": self.controls_tab,
            "Chat": self.chat_tab,
            "Tools": self.tools_tab,
            "Info": self.info_tab
        }
        
        self.update_tab_styles()

    def switch_view(self, view_name):
        """Switch between different views"""
        self.current_view = view_name
        self.update_tab_styles()
        
        for frame in self.view_frames.values():
            frame.pack_forget()
        
        self.view_frames[view_name].pack(fill=tk.BOTH, expand=True)
        
        self.parent.root.update_idletasks()

    def update_tab_styles(self):
        """Update tab button styles to show active tab"""
        from BASE.interface.gui_themes import DarkTheme
        for name, tab in self.tabs.items():
            if name == self.current_view:
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