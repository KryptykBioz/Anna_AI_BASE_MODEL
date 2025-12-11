# Filename: BASE/interface/gui_youtube_panel.py
"""
YouTube panel for GUI - manages YouTube chat controls
FIXED: Now properly registers with ChatHandler when video is set
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_themes import DarkTheme

class YouTubePanel:
    """Manages the YouTube chat integration panel and functionality"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def create_youtube_panel(self, parent_frame):
        """Create YouTube chat control panel with URL input"""
        from BASE.tools.internal.chat.youtube_chat_direct import YOUTUBE_AVAILABLE
        
        if not YOUTUBE_AVAILABLE:
            return
            
        youtube_frame = ttk.LabelFrame(
            parent_frame, text="YouTube Live Chat", style="Dark.TLabelframe"
        )
        youtube_frame.pack(fill=tk.X, pady=(5, 0))
        
        # URL Input Section
        url_frame = ttk.Frame(youtube_frame)
        url_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        url_label = tk.Label(
            url_frame,
            text="Video URL or ID:",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        url_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.parent.youtube_url_entry = tk.Entry(
            url_frame,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE
        )
        self.parent.youtube_url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Pre-fill with config value if available
        config_video_id = getattr(self.parent.config, 'youtube_video_id', '')
        if config_video_id and config_video_id.strip() != "":
            self.parent.youtube_url_entry.insert(0, config_video_id)
        
        # Set button to apply URL
        set_button = ttk.Button(
            url_frame,
            text="Set",
            command=self.set_youtube_url,
            width=8
        )
        set_button.pack(side=tk.RIGHT)
        
        # Status and Controls Section
        controls_frame = ttk.Frame(youtube_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.parent.youtube_status_label = tk.Label(
            controls_frame,
            text="Status: Not initialized",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_SECONDARY,
            background=DarkTheme.BG_DARKER
        )
        self.parent.youtube_status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        button_container = ttk.Frame(controls_frame)
        button_container.pack(side=tk.RIGHT)
        
        self.parent.youtube_start_btn = ttk.Button(
            button_container,
            text="Start",
            command=self.start_youtube_monitoring,
            width=10
        )
        self.parent.youtube_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.parent.youtube_stop_btn = ttk.Button(
            button_container,
            text="Stop",
            command=self.stop_youtube_monitoring,
            width=10,
            state=tk.DISABLED
        )
        self.parent.youtube_stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.parent.youtube_msg_label = tk.Label(
            youtube_frame,
            text="Messages: 0",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        self.parent.youtube_msg_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    def set_youtube_url(self):
        """
        Set YouTube video URL/ID and reinitialize chat integration
        FIXED: Now registers with ChatHandler
        """
        url_or_id = self.parent.youtube_url_entry.get().strip()
        
        if not url_or_id:
            messagebox.showwarning("Invalid Input", "Please enter a YouTube video URL or ID")
            return
        
        # Extract video ID from URL if full URL provided
        video_id = self.extract_video_id(url_or_id)
        
        if not video_id:
            messagebox.showerror("Invalid URL", "Could not extract video ID from the provided URL")
            return
        
        try:
            # Check if currently running via ChatHandler
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'YouTube' in chat_handler._platforms:
                # Stop via ChatHandler
                chat_handler.stop_platform('YouTube')
                self.parent.logger.youtube("Stopped previous monitoring via ChatHandler")
            elif self.parent.youtube_chat and self.parent.youtube_chat.enabled:
                # Legacy stop
                self.parent.youtube_chat.stop()
                self.parent.logger.youtube("Stopped previous YouTube monitoring")
            
            # Update config
            self.parent.config.youtube_video_id = video_id
            
            # Reinitialize YouTube chat (NO ai_core parameter)
            from BASE.tools.internal.chat.youtube_chat_direct import YouTubeIntegration
            
            max_messages = getattr(self.parent.config, 'youtube_max_messages', 10)
            
            self.parent.logger.youtube(f"Initializing chat for video: {video_id}")
            self.parent.youtube_chat = YouTubeIntegration(
                video_id=video_id,
                max_context_messages=max_messages,
                gui_logger=self.parent._gui_log_callback
            )
            
            # Register with ChatHandler if available
            if chat_handler:
                success = chat_handler.register_platform(
                    platform_name="YouTube",
                    integration_instance=self.parent.youtube_chat,
                    auto_start=False
                )
                if success:
                    self.parent.logger.youtube("[SUCCESS] Registered with ChatHandler")
                else:
                    self.parent.logger.error("Failed to register with ChatHandler")
            else:
                self.parent.logger.warning("ChatHandler not available - integration may not work")
            
            # Update status
            self.parent.youtube_status_label.config(
                text="Status: Ready (not started)",
                foreground=DarkTheme.FG_PRIMARY
            )
            
            self.parent.logger.youtube(f"Chat configured for video ID: {video_id}")
            messagebox.showinfo("Success", f"YouTube chat configured for video:\n{video_id}")
            
            # Update entry to show just the video ID
            self.parent.youtube_url_entry.delete(0, tk.END)
            self.parent.youtube_url_entry.insert(0, video_id)
            
        except Exception as e:
            error_msg = f"Failed to configure YouTube chat: {e}"
            self.parent.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def extract_video_id(self, url_or_id):
        """Extract video ID from YouTube URL or return ID if already extracted"""
        import re
        
        # If it's already just an ID (11 characters, alphanumeric with - and _)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
            return url_or_id
        
        # Try to extract from various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})',
            r'[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None

    def start_youtube_monitoring(self):
        """
        Start YouTube chat monitoring
        UPDATED: Uses ChatHandler like Twitch
        """
        if not self.parent.youtube_chat:
            self.parent.logger.youtube("Chat not initialized")
            messagebox.showwarning("Not Initialized", "Please set a video ID first")
            return
        
        self.parent.youtube_start_btn.config(state=tk.DISABLED)
        if hasattr(self.parent, 'youtube_status_label'):
            self.parent.youtube_status_label.config(
                text="Status: Starting...", 
                foreground=DarkTheme.ACCENT_YELLOW
            )
        
        self.parent.logger.youtube("Starting chat monitoring...")
        
        try:
            # Try to start via ChatHandler first
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'YouTube' in chat_handler._platforms:
                success = chat_handler.start_platform('YouTube')
            else:
                # Fallback to direct start
                self.parent.logger.warning("ChatHandler not available - using direct start")
                success = self.parent.youtube_chat.start()
            
            self._update_youtube_ui_after_start(success)
            
        except Exception as e:
            error_msg = f"Error starting YouTube monitoring: {e}"
            self.parent.logger.error(error_msg)
            self._update_youtube_ui_after_start(False, error_msg)

    def _update_youtube_ui_after_start(self, success, error_msg=None):
        """Update UI after start attempt"""
        if success:
            self.parent.logger.youtube("[SUCCESS] Chat monitoring started successfully")
            if hasattr(self.parent, 'youtube_stop_btn'):
                self.parent.youtube_stop_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'youtube_status_label'):
                self.parent.youtube_status_label.config(
                    text="Status: Running", 
                    foreground=DarkTheme.ACCENT_GREEN
                )
        else:
            if error_msg:
                self.parent.logger.error(error_msg)
            else:
                self.parent.logger.error("Failed to start YouTube chat monitoring")
            if hasattr(self.parent, 'youtube_start_btn'):
                self.parent.youtube_start_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'youtube_status_label'):
                self.parent.youtube_status_label.config(
                    text="Status: Failed", 
                    foreground=DarkTheme.ACCENT_RED
                )
        
        self.parent.root.after(1000, self.update_youtube_status)
    
    def stop_youtube_monitoring(self):
        """
        Stop YouTube chat monitoring
        UPDATED: Uses ChatHandler if available
        """
        if not self.parent.youtube_chat:
            return
        
        if hasattr(self.parent, 'youtube_stop_btn'):
            self.parent.youtube_stop_btn.config(state=tk.DISABLED)
        if hasattr(self.parent, 'youtube_status_label'):
            self.parent.youtube_status_label.config(
                text="Status: Stopping...", 
                foreground=DarkTheme.ACCENT_YELLOW
            )
        
        self.parent.logger.youtube("Stopping chat monitoring...")
        
        try:
            # Try to stop via ChatHandler first
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'YouTube' in chat_handler._platforms:
                chat_handler.stop_platform('YouTube')
            else:
                # Fallback to direct stop
                self.parent.youtube_chat.stop()
            
            self.parent.logger.youtube("[SUCCESS] Chat monitoring stopped")
            if hasattr(self.parent, 'youtube_start_btn'):
                self.parent.youtube_start_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'youtube_status_label'):
                self.parent.youtube_status_label.config(
                    text="Status: Stopped", 
                    foreground=DarkTheme.FG_MUTED
                )
            self.update_youtube_status()
        except Exception as e:
            error_msg = f"Error stopping YouTube monitoring: {e}"
            self.parent.logger.error(error_msg)
            if hasattr(self.parent, 'youtube_stop_btn'):
                self.parent.youtube_stop_btn.config(state=tk.NORMAL)
    
    def update_youtube_status(self):
        """
        Update YouTube status display
        UPDATED: Shows ChatHandler stats if available
        """
        if not self.parent.youtube_chat:
            if hasattr(self.parent, 'youtube_status_label'):
                self.parent.youtube_status_label.config(
                    text="Status: Not available",
                    foreground=DarkTheme.FG_MUTED
                )
            return
        
        is_running = self.parent.youtube_chat.enabled
        
        # Get message count from ChatHandler if available
        msg_count = 0
        chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
        
        if chat_handler:
            stats = chat_handler.get_stats()
            platform_stats = stats.get('platforms', {}).get('YouTube', {})
            msg_count = platform_stats.get('buffered_count', 0)
            
            # Also show received/processed counts if available
            received = platform_stats.get('received', 0)
            buffered = platform_stats.get('buffered', 0)
            
            if hasattr(self.parent, 'youtube_msg_label'):
                self.parent.youtube_msg_label.config(
                    text=f"Messages: {msg_count} buffered | {received} received | {buffered} processed"
                )
        elif is_running and self.parent.youtube_chat.monitor:
            # Fallback to direct monitor stats
            msg_count = len(self.parent.youtube_chat.monitor.chat_buffer)
            if hasattr(self.parent, 'youtube_msg_label'):
                self.parent.youtube_msg_label.config(text=f"Messages buffered: {msg_count}")
        
        # Update status label
        if hasattr(self.parent, 'youtube_status_label'):
            status_text = "Status: " + ("Running" if is_running else "Stopped")
            status_color = DarkTheme.ACCENT_GREEN if is_running else DarkTheme.FG_MUTED
            self.parent.youtube_status_label.config(text=status_text, foreground=status_color)
        
        # Continue updating if running
        if is_running:
            self.parent.root.after(2000, self.update_youtube_status)