# Filename: BASE/interface/gui_coding_view.py
import tkinter as tk
from tkinter import ttk

class CodingView:
    """Manages the Coding view, integrating the Coding Tool panel and the Session Files panel."""
    
    # NOTE: The SessionFilesPanel instance is passed here by gui_ui_builder.py
    def __init__(self, parent, session_files_panel):
        self.parent = parent
        # Store the panel instance
        self.session_files_panel = session_files_panel 
    
    def create_coding_view(self):
        """Create the Coding view with a vertical split layout."""
        
        main_container = ttk.Frame(self.parent.coding_view)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Use a PanedWindow for a resizable vertical split
        # We change the orientation to tk.VERTICAL
        paned_window = ttk.PanedWindow(main_container, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- 1. Top Panel: Coding Tool (Primary Area) ---
        coding_frame = ttk.Frame(paned_window)
        
        # Create the existing coding panel inside the top frame
        self.parent.coding_panel_manager.create_coding_panel(coding_frame)
        
        # Add to PanedWindow (weight=1 means it takes up all available height)
        paned_window.add(coding_frame, weight=1)

        # --- 2. Bottom Panel: Session Files ---
        # Create a frame for the file panel and set an initial height
        files_frame = ttk.Frame(paned_window, height=250) 
        files_frame.pack_propagate(False) # Prevents the frame from shrinking/growing past height setting
        
        # Create the session files panel inside the bottom frame
        self.session_files_panel.create_panel(files_frame)
        
        # Add to PanedWindow (weight=0 means it only takes up its set height)
        paned_window.add(files_frame, weight=0)