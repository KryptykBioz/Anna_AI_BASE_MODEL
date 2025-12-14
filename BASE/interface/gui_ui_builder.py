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
from BASE.interface.gui_themes import THEMES
import personality.controls as controls

class UIBuilder:
    """Handles main UI creation and view switching for the GUI"""
    
    def __init__(self, parent):
        self.parent = parent
        self.parent.root.geometry("770x870")
        self.theme_manager = ThemeManager(self.parent)
        self.controls_view = ControlsView(self.parent)
        self.chat_view_instance = ChatView(self.parent)  # Store instance reference
        self.tools_view = ToolsView(self.parent, project_root)
        self.info_view = InfoView(self.parent, project_root)
        self.config_view = ConfigView(self.parent, project_root)
        
        # Store ChatView instance in parent for theme manager access
        self.parent.chat_view_instance = self.chat_view_instance
        
    def setup_gui(self):
        self.create_menu()
        self.create_main_frames()
        self.create_all_views()
        self.theme_manager.apply_theme()  # Apply after menu/frames/views exist
        self.switch_view("Chat")
        
        # Enable widget updates now that all widgets are created
        self.theme_manager.enable_widget_updates()

    def create_main_frames(self):
        """Create main container and view frames"""
        self.parent.main_container = ttk.Frame(self.parent.root)
        self.parent.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create frames for each view
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
        self.chat_view_instance.create_chat_view()
        self.tools_view.create_tools_view()
        self.info_view.create_info_view()

    def create_menu(self):
        """Create menu bar with tabs and theme selector"""
        theme = self.theme_manager.get_theme()
        
        menubar_frame = tk.Frame(self.parent.root, bg=theme.BG_DARKER, height=50)
        
        # Pack before main_container to ensure it stays at top
        if hasattr(self.parent, 'main_container') and self.parent.main_container.winfo_ismapped():
            menubar_frame.pack(side=tk.TOP, fill=tk.X, before=self.parent.main_container)
        else:
            menubar_frame.pack(side=tk.TOP, fill=tk.X)
        
        menubar_frame.pack_propagate(False)
        
        # Store reference for future theme changes
        self.menubar_frame = menubar_frame
        
        # Initialize current_view only if not already set (first time)
        if not hasattr(self, 'current_view'):
            self.current_view = "Chat"
        
        # Determine font based on theme
        font_name = "Courier New" if self.theme_manager.theme_name == "Cyber" else "Segoe UI"
        
        # Tab style based on current theme
        tab_style = {
            'font': (font_name, 10, "bold" if self.theme_manager.theme_name == "Cyber" else "normal"),
            'relief': 'flat' if self.theme_manager.theme_name == "Cyber" else 'solid',
            'padx': 20,
            'pady': 12 if self.theme_manager.theme_name == "Cyber" else 10,
            'cursor': 'hand2',
            'borderwidth': 2,
            'bg': theme.BUTTON_BG,
            'fg': theme.ACCENT_GREEN if self.theme_manager.theme_name == "Cyber" else 'white',
            'highlightthickness': 2 if self.theme_manager.theme_name == "Cyber" else 0,
            'highlightbackground': theme.BORDER,
            'highlightcolor': theme.ACCENT_GREEN if self.theme_manager.theme_name == "Cyber" else theme.ACCENT_PURPLE,
            'activebackground': theme.BUTTON_HOVER,
            'activeforeground': theme.ACCENT_GREEN if self.theme_manager.theme_name == "Cyber" else 'white'
        }
        
        # Create theme selector in top-right corner
        theme_frame = tk.Frame(menubar_frame, bg=theme.BG_DARKER)
        theme_frame.pack(side=tk.RIGHT, padx=10)
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            bg=theme.BG_DARKER,
            fg=theme.FG_PRIMARY,
            font=(font_name, 9)
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.theme_selector = ttk.Combobox(
            theme_frame,
            values=list(THEMES.keys()),
            state='readonly',
            width=10,
            font=(font_name, 9)
        )
        self.theme_selector.set(self.theme_manager.theme_name)
        self.theme_selector.bind('<<ComboboxSelected>>', self.on_theme_change)
        self.theme_selector.pack(side=tk.LEFT)
        
        # Create tabs with even spacing
        tab_text = lambda t: f"[ {t} ]" if self.theme_manager.theme_name == "Cyber" else t
        
        self.config_tab = tk.Button(menubar_frame, text=tab_text("CONFIG"), **tab_style,
                                    command=lambda: self.switch_view("Config"))
        self.config_tab.place(relx=0.1, rely=0.5, anchor=tk.CENTER)
        
        self.controls_tab = tk.Button(menubar_frame, text=tab_text("CONTROLS"), **tab_style,
                                    command=lambda: self.switch_view("Controls"))
        self.controls_tab.place(relx=0.25, rely=0.5, anchor=tk.CENTER)
        
        self.chat_tab = tk.Button(menubar_frame, text=tab_text("CHAT"), **tab_style,
                                command=lambda: self.switch_view("Chat"))
        self.chat_tab.place(relx=0.4, rely=0.5, anchor=tk.CENTER)
        
        self.tools_tab = tk.Button(menubar_frame, text=tab_text("TOOLS"), **tab_style,
                                   command=lambda: self.switch_view("Tools"))
        self.tools_tab.place(relx=0.55, rely=0.5, anchor=tk.CENTER)
        
        self.info_tab = tk.Button(menubar_frame, text=tab_text("INFO"), **tab_style,
                                  command=lambda: self.switch_view("Info"))
        self.info_tab.place(relx=0.7, rely=0.5, anchor=tk.CENTER)
        
        # # Add NEW badges to Config and Tools tabs
        # badge_style = {
        #     "bg": theme.ACCENT_GREEN,
        #     "fg": theme.BG_DARKER if self.theme_manager.theme_name in ["Dark", "Cyber"] else "white",
        #     "font": (font_name, 7, "bold"),
        #     "padx": 5 if self.theme_manager.theme_name == "Cyber" else 4,
        #     "pady": 2 if self.theme_manager.theme_name == "Cyber" else 1,
        #     "borderwidth": 1,
        #     "relief": 'solid'
        # }
        
        # config_badge = tk.Label(menubar_frame, 
        #                        text="✦ NEW" if self.theme_manager.theme_name == "Cyber" else "NEW",
        #                        **badge_style)
        # config_badge.place(in_=self.config_tab, relx=0.9, rely=0.15)
        
        # tools_badge = tk.Label(menubar_frame,
        #                       text="✦ NEW" if self.theme_manager.theme_name == "Cyber" else "NEW",
        #                       **badge_style)
        # tools_badge.place(in_=self.tools_tab, relx=0.9, rely=0.15)
        
        # Store tabs for styling
        self.tabs = {
            "Config": self.config_tab,
            "Controls": self.controls_tab,
            "Chat": self.chat_tab,
            "Tools": self.tools_tab,
            "Info": self.info_tab
        }
        
        self.update_tab_styles()

    def on_theme_change(self, event=None):
        """Handle theme selection change"""
        new_theme = self.theme_selector.get()
        self.theme_manager.set_theme(new_theme)
        
        # Destroy old menubar if it exists
        if hasattr(self, 'menubar_frame') and self.menubar_frame.winfo_exists():
            self.menubar_frame.destroy()
        
        # Recreate menu with new theme styling
        self.create_menu()
        
        # Update tab styles to reflect current view
        self.update_tab_styles()
        
        # Log theme change
        if hasattr(self.parent, 'logger'):
            self.parent.logger.system(f"Theme changed to: {new_theme}")

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
        theme = self.theme_manager.get_theme()
        font_name = "Courier New" if self.theme_manager.theme_name == "Cyber" else "Segoe UI"
        
        for name, tab in self.tabs.items():
            if name == self.current_view:
                # Active tab styling
                if self.theme_manager.theme_name == "Cyber":
                    tab.config(
                        bg=theme.ACCENT_PURPLE,
                        fg=theme.ACCENT_GREEN,
                        font=(font_name, 11, "bold"),
                        highlightbackground=theme.ACCENT_GREEN,
                        highlightcolor=theme.ACCENT_GREEN,
                        highlightthickness=3,
                        activebackground=theme.ACCENT_PURPLE,
                        activeforeground=theme.ACCENT_GREEN
                    )
                elif self.theme_manager.theme_name == "Light":
                    tab.config(
                        bg=theme.ACCENT_PURPLE,
                        fg='white',
                        font=(font_name, 10, "bold"),
                        highlightbackground=theme.ACCENT_PURPLE,
                        highlightcolor=theme.ACCENT_PURPLE,
                        activebackground=theme.ACCENT_PURPLE,
                        activeforeground='white'
                    )
                else:  # Dark theme
                    tab.config(
                        bg=theme.ACCENT_GREEN,
                        fg='white',
                        font=(font_name, 10, "bold"),
                        highlightbackground=theme.ACCENT_GREEN,
                        highlightcolor=theme.ACCENT_GREEN,
                        activebackground=theme.ACCENT_GREEN,
                        activeforeground='white'
                    )
            else:
                # Inactive tab styling
                if self.theme_manager.theme_name == "Cyber":
                    tab.config(
                        bg=theme.BUTTON_BG,
                        fg=theme.ACCENT_GREEN,
                        font=(font_name, 10, "bold"),
                        highlightbackground=theme.BORDER,
                        highlightcolor=theme.ACCENT_GREEN,
                        highlightthickness=2,
                        activebackground=theme.BUTTON_HOVER,
                        activeforeground=theme.ACCENT_GREEN
                    )
                else:
                    tab.config(
                        bg=theme.ACCENT_PURPLE if self.theme_manager.theme_name in ["Dark", "Light"] else theme.BUTTON_BG,
                        fg='white' if self.theme_manager.theme_name in ["Dark", "Light"] else theme.FG_PRIMARY,
                        font=(font_name, 10),
                        highlightbackground=theme.ACCENT_PURPLE if self.theme_manager.theme_name in ["Dark", "Light"] else theme.BORDER,
                        highlightcolor=theme.ACCENT_PURPLE,
                        activebackground=theme.ACCENT_PURPLE if self.theme_manager.theme_name in ["Dark", "Light"] else theme.BUTTON_HOVER,
                        activeforeground='white' if self.theme_manager.theme_name in ["Dark", "Light"] else theme.FG_PRIMARY
                    )

    def show_status_dialog(self):
        from tkinter import scrolledtext
        theme = self.theme_manager.get_theme()
        font_name = "Courier New" if self.theme_manager.theme_name == "Cyber" else "Segoe UI"
        
        dialog = tk.Toplevel(self.parent.root)
        dialog.title("Current Status")
        dialog.configure(bg=theme.BG_DARK)
        dialog.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(
            dialog,
            wrap=tk.WORD,
            font=(font_name, 10),
            bg=theme.BG_DARKER,
            fg=theme.FG_PRIMARY,
            insertbackground=theme.FG_PRIMARY
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