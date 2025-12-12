# Filename: BASE/interface/gui_controls_view.py
"""

"""

import tkinter as tk
from tkinter import ttk
from BASE.interface.gui_themes import DarkTheme


class ControlsView:
    """Manages the Controls view, including control panel and auxiliary panels"""
    
    def __init__(self, parent):
        self.parent = parent
        
    
    def create_controls_view(self):
        """Create the Controls view with control panel and auxiliary panels"""
        controls_paned = ttk.PanedWindow(self.parent.controls_view, orient=tk.HORIZONTAL)
        controls_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Control Panel (wider fixed width)
        left_frame = ttk.Frame(controls_paned, width=460)
        left_frame.pack_propagate(False)
        controls_paned.add(left_frame, weight=0)
        
        # Right side - Stats, Voice, YouTube, Twitch, Discord, Warudo
        right_frame = ttk.Frame(controls_paned)
        controls_paned.add(right_frame, weight=1)
        
        # Create control panel
        self.parent.control_panel_manager.create_control_panel(left_frame)
        
        # Create auxiliary panels (stats, voice, external integrations)
        self.create_auxiliary_panels(right_frame)

    def create_auxiliary_panels(self, parent_frame):
        """Create voice, YouTube, Twitch, Discord, and Warudo panels"""

        
        # Voice panel
        self.parent.voice_manager.create_voice_panel(parent_frame)
        
        # External Integrations section
        integrations_frame = ttk.LabelFrame(
            parent_frame, 
            text="External Integrations", 
            style="Dark.TLabelframe"
        )
        integrations_frame.pack(fill=tk.X, pady=(5, 0))