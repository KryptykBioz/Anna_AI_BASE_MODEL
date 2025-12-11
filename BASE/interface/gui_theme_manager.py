# Filename: BASE/interface/gui_theme_manager.py

from tkinter import ttk
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_themes import DarkTheme

class ThemeManager:
    """Manages the application of the dark theme and Tkinter style configurations"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def apply_dark_theme(self):
        """Apply dark theme including title bar"""
        self.parent.root.configure(bg=DarkTheme.BG_DARKER)
        
        # Apply dark title bar (Windows 10/11)
        try:
            import ctypes as ct
            
            def set_dark_title_bar(window):
                """
                Set dark title bar on Windows 10/11
                Uses DWM (Desktop Window Manager) API
                """
                window.update()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
                get_parent = ct.windll.user32.GetParent
                hwnd = get_parent(window.winfo_id())
                
                # Try newer attribute first (Windows 11)
                rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
                value = 2
                value = ct.c_int(value)
                set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
            
            set_dark_title_bar(self.parent.root)
            
        except Exception as e:
            # Silently fail if not on Windows or if API unavailable
            print(f"Could not set dark title bar: {e}")
        
        # Configure default Tkinter scrollbar colors (for ScrolledText widgets)
        self.parent.root.option_add("*Scrollbar.background", DarkTheme.BG_LIGHTER)
        self.parent.root.option_add("*Scrollbar.troughColor", DarkTheme.BG_DARKER)
        self.parent.root.option_add("*Scrollbar.activeBackground", DarkTheme.BUTTON_HOVER)
        self.parent.root.option_add("*Scrollbar.highlightBackground", DarkTheme.BG_DARKER)
        self.parent.root.option_add("*Scrollbar.borderWidth", 0)
        self.parent.root.option_add("*Scrollbar.relief", "flat")
        
        style = ttk.Style()
        style.theme_use('clam')

        # Frame styling
        style.configure('TFrame', background=DarkTheme.BG_DARKER)
        
        # Label styling
        style.configure('TLabel', background=DarkTheme.BG_DARKER, foreground=DarkTheme.FG_PRIMARY, 
                    font=("Segoe UI", 9))
        
        # Button styling - modern flat with purple accent
        style.configure('TButton', 
                    background=DarkTheme.BUTTON_BG, 
                    foreground=DarkTheme.FG_PRIMARY,
                    borderwidth=1, 
                    bordercolor=DarkTheme.BORDER,
                    focuscolor='none',
                    font=("Segoe UI", 9, "bold"),
                    relief='flat',
                    padding=(12, 6))
        style.map('TButton',
                background=[('active', DarkTheme.BUTTON_HOVER),
                        ('pressed', DarkTheme.ACCENT_PURPLE)])
        
        # Checkbutton styling with rounded look
        style.configure('TCheckbutton', 
                    background=DarkTheme.BG_DARKER, 
                    foreground=DarkTheme.FG_PRIMARY,
                    focuscolor='none',
                    indicatorcolor=DarkTheme.ACCENT_PURPLE,
                    font=("Segoe UI", 9))
        style.map('TCheckbutton',
                background=[('active', DarkTheme.BG_DARKER)],
                foreground=[('active', DarkTheme.FG_PRIMARY)],
                indicatorcolor=[('selected', DarkTheme.ACCENT_PURPLE)])

        # Scrollbar styling - dark grey to match theme
        style.configure('Vertical.TScrollbar',
                    background=DarkTheme.BG_LIGHTER,
                    troughcolor=DarkTheme.BG_DARKER,
                    bordercolor=DarkTheme.BG_DARKER,
                    arrowcolor=DarkTheme.FG_MUTED,
                    relief='flat',
                    borderwidth=0)
        style.map('Vertical.TScrollbar',
                background=[('active', DarkTheme.BUTTON_HOVER),
                        ('pressed', DarkTheme.ACCENT_PURPLE)])
        
        style.configure('Horizontal.TScrollbar',
                    background=DarkTheme.BG_LIGHTER,
                    troughcolor=DarkTheme.BG_DARKER,
                    bordercolor=DarkTheme.BG_DARKER,
                    arrowcolor=DarkTheme.FG_MUTED,
                    relief='flat',
                    borderwidth=0)
        style.map('Horizontal.TScrollbar',
                background=[('active', DarkTheme.BUTTON_HOVER),
                        ('pressed', DarkTheme.ACCENT_PURPLE)])

        # LabelFrame styling - clean borders
        style.configure("Dark.TLabelframe", 
                    background=DarkTheme.BG_DARKER,
                    foreground=DarkTheme.FG_SECONDARY, 
                    bordercolor=DarkTheme.BORDER,
                    borderwidth=1,
                    relief='solid')
        style.configure("Dark.TLabelframe.Label", 
                    background=DarkTheme.BG_DARKER,
                    foreground=DarkTheme.FG_SECONDARY,
                    font=("Segoe UI", 9))
        
        # Purple accent labelframe for NEW badges and highlights
        style.configure("Accent.TLabelframe", 
                    background=DarkTheme.BG_DARKER,
                    foreground=DarkTheme.ACCENT_PURPLE, 
                    bordercolor=DarkTheme.ACCENT_PURPLE,
                    relief='solid',
                    borderwidth=2)
        style.configure("Accent.TLabelframe.Label", 
                    background=DarkTheme.BG_DARKER,
                    foreground=DarkTheme.ACCENT_PURPLE,
                    font=("Segoe UI", 10, "bold"))