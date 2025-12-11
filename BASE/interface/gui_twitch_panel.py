# Filename: BASE/interface/gui_twitch_panel.py
"""
Twitch panel for GUI - manages Twitch chat controls
UPDATED for centralized architecture with ChatHandler integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_themes import DarkTheme

class TwitchPanel:
    """Manages the Twitch chat integration panel and functionality"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def create_twitch_panel(self, parent_frame):
        """Create Twitch chat control panel with channel input"""
        from BASE.tools.internal.chat.twitch_chat_direct import TWITCH_AVAILABLE
        
        if not TWITCH_AVAILABLE:
            return
            
        twitch_frame = ttk.LabelFrame(
            parent_frame, text="Twitch Live Chat", style="Dark.TLabelframe"
        )
        twitch_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Channel Input Section
        channel_frame = ttk.Frame(twitch_frame)
        channel_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        channel_label = tk.Label(
            channel_frame,
            text="Channel Name:",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        channel_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.parent.twitch_channel_entry = tk.Entry(
            channel_frame,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE,
            width=20
        )
        self.parent.twitch_channel_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Pre-fill with config value if available
        config_channel = getattr(self.parent.config, 'twitch_channel', '')
        if config_channel and config_channel.strip() != "":
            self.parent.twitch_channel_entry.insert(0, config_channel)
        
        # Set button to apply channel
        set_button = ttk.Button(
            channel_frame,
            text="Set",
            command=self.set_twitch_channel,
            width=8
        )
        set_button.pack(side=tk.RIGHT)
        
        # OAuth Section (collapsible)
        oauth_frame = ttk.LabelFrame(
            twitch_frame, text="Authentication (Optional)", style="Dark.TLabelframe"
        )
        oauth_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        oauth_info_label = tk.Label(
            oauth_frame,
            text="For sending messages, provide OAuth token:",
            font=("Segoe UI", 8),
            foreground=DarkTheme.FG_SECONDARY,
            background=DarkTheme.BG_DARKER
        )
        oauth_info_label.pack(anchor="w", padx=5, pady=(5, 2))
        
        oauth_input_frame = ttk.Frame(oauth_frame)
        oauth_input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(
            oauth_input_frame,
            text="OAuth:",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.parent.twitch_oauth_entry = tk.Entry(
            oauth_input_frame,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE,
            show="*"
        )
        self.parent.twitch_oauth_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Pre-fill OAuth if available
        config_oauth = getattr(self.parent.config, 'twitch_oauth_token', '')
        if config_oauth and config_oauth.strip() != "":
            self.parent.twitch_oauth_entry.insert(0, config_oauth)
        
        help_button = ttk.Button(
            oauth_input_frame,
            text="?",
            command=self.show_oauth_help,
            width=3
        )
        help_button.pack(side=tk.RIGHT)
        
        # Nickname input
        nickname_frame = ttk.Frame(oauth_frame)
        nickname_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(
            nickname_frame,
            text="Nickname:",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.parent.twitch_nickname_entry = tk.Entry(
            nickname_frame,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE
        )
        self.parent.twitch_nickname_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Pre-fill nickname if available
        config_nickname = getattr(self.parent.config, 'twitch_nickname', '')
        if config_nickname and config_nickname.strip() != "":
            self.parent.twitch_nickname_entry.insert(0, config_nickname)
        
        # Status and Controls Section
        controls_frame = ttk.Frame(twitch_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        self.parent.twitch_status_label = tk.Label(
            controls_frame,
            text="Status: Not initialized",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_SECONDARY,
            background=DarkTheme.BG_DARKER
        )
        self.parent.twitch_status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        button_container = ttk.Frame(controls_frame)
        button_container.pack(side=tk.RIGHT)
        
        self.parent.twitch_start_btn = ttk.Button(
            button_container,
            text="Start",
            command=self.start_twitch_monitoring,
            width=10
        )
        self.parent.twitch_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.parent.twitch_stop_btn = ttk.Button(
            button_container,
            text="Stop",
            command=self.stop_twitch_monitoring,
            width=10,
            state=tk.DISABLED
        )
        self.parent.twitch_stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Send message section (if authenticated)
        send_frame = ttk.Frame(twitch_frame)
        send_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        self.parent.twitch_send_entry = tk.Entry(
            send_frame,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DarkTheme.BORDER,
            highlightcolor=DarkTheme.ACCENT_PURPLE
        )
        self.parent.twitch_send_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.parent.twitch_send_entry.bind('<Return>', lambda e: self.send_twitch_message())
        
        self.parent.twitch_send_btn = ttk.Button(
            send_frame,
            text="Send",
            command=self.send_twitch_message,
            width=10,
            state=tk.DISABLED
        )
        self.parent.twitch_send_btn.pack(side=tk.RIGHT)
        
        # Stats label
        self.parent.twitch_msg_label = tk.Label(
            twitch_frame,
            text="Messages: 0",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        )
        self.parent.twitch_msg_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    def show_oauth_help(self):
        """Show OAuth help dialog"""
        help_text = """OAuth Token for Twitch

To get an OAuth token:
1. Visit: https://twitchapps.com/tmi/
2. Click 'Connect' and authorize
3. Copy the token (starts with 'oauth:')
4. Paste it in the OAuth field

Without OAuth:
• Read-only mode (justinfan)
• Cannot send messages

With OAuth:
• Can send messages to chat
• Use your custom nickname"""
        
        messagebox.showinfo("OAuth Help", help_text)

    def set_twitch_channel(self):
        """
        Set Twitch channel and reinitialize chat integration
        UPDATED: Works with ChatHandler registration
        """
        channel = self.parent.twitch_channel_entry.get().strip().lower().lstrip('#')
        
        if not channel:
            messagebox.showwarning("Invalid Input", "Please enter a Twitch channel name")
            return
        
        try:
            # Check if currently running via ChatHandler
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'Twitch' in chat_handler._platforms:
                # Stop via ChatHandler
                chat_handler.stop_platform('Twitch')
                self.parent.logger.twitch("Stopped previous monitoring via ChatHandler")
            elif self.parent.twitch_chat and self.parent.twitch_chat.enabled:
                # Legacy stop
                self.parent.twitch_chat.stop()
                self.parent.logger.twitch("Stopped previous Twitch monitoring")
            
            # Get OAuth and nickname if provided
            oauth_token = self.parent.twitch_oauth_entry.get().strip()
            nickname = self.parent.twitch_nickname_entry.get().strip()
            
            # Update config
            self.parent.config.twitch_channel = channel
            self.parent.config.twitch_oauth_token = oauth_token
            self.parent.config.twitch_nickname = nickname
            
            # Reinitialize Twitch chat (NO ai_core parameter)
            from BASE.tools.internal.chat.twitch_chat_direct import TwitchIntegration
            
            max_messages = getattr(self.parent.config, 'twitch_max_messages', 10)
            
            self.parent.logger.twitch(f"Initializing chat for channel: #{channel}")
            self.parent.twitch_chat = TwitchIntegration(
                channel=channel,
                max_context_messages=max_messages,
                oauth_token=oauth_token if oauth_token else "",
                nickname=nickname if nickname else "",
                gui_logger=self.parent._gui_log_callback
            )
            
            # Register with ChatHandler if available
            if chat_handler:
                success = chat_handler.register_platform(
                    platform_name="Twitch",
                    integration_instance=self.parent.twitch_chat,
                    auto_start=False
                )
                if success:
                    self.parent.logger.twitch("[SUCCESS] Registered with ChatHandler")
                else:
                    self.parent.logger.error("Failed to register with ChatHandler")
            else:
                self.parent.logger.warning("ChatHandler not available - integration may not work")
            
            # Update status
            mode = "authenticated" if oauth_token else "anonymous (read-only)"
            self.parent.twitch_status_label.config(
                text=f"Status: Ready ({mode})",
                foreground=DarkTheme.FG_PRIMARY
            )
            
            self.parent.logger.twitch(f"Chat configured for channel: #{channel} ({mode})")
            messagebox.showinfo("Success", f"Twitch chat configured:\nChannel: #{channel}\nMode: {mode}")
            
        except Exception as e:
            error_msg = f"Failed to configure Twitch chat: {e}"
            self.parent.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def verify_chat_integration(self):
        """
        Diagnostic method to verify chat handler integration
        Call this after starting Twitch monitoring to verify setup
        """
        if not self.parent.twitch_chat:
            self.parent.logger.error("[Diagnostic] Twitch chat not initialized")
            return False
        
        chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
        if not chat_handler:
            self.parent.logger.error("[Diagnostic] Chat handler not initialized")
            return False
        
        if 'Twitch' not in chat_handler._platforms:
            self.parent.logger.error("[Diagnostic] Twitch not registered with chat handler")
            return False
        
        if not hasattr(self.parent.ai_core, 'main_loop'):
            self.parent.logger.error("[Diagnostic] AI Core has no main_loop")
            return False
        
        if not self.parent.ai_core.main_loop:
            self.parent.logger.error("[Diagnostic] AI Core main_loop is None")
            return False
        
        if not self.parent.ai_core.main_loop.is_running():
            self.parent.logger.error("[Diagnostic] AI Core main_loop is not running")
            return False
        
        self.parent.logger.system("[Diagnostic] [SUCCESS] All chat integration components verified")
        self.parent.logger.system(f"[Diagnostic] Event loop: {self.parent.ai_core.main_loop}")
        self.parent.logger.system(f"[Diagnostic] Loop running: {self.parent.ai_core.main_loop.is_running()}")
        self.parent.logger.system(f"[Diagnostic] Twitch enabled: {self.parent.twitch_chat.enabled}")
        self.parent.logger.system(f"[Diagnostic] Chat handler platforms: {list(chat_handler._platforms.keys())}")
        
        return True
    
    def start_twitch_monitoring(self):
        """
        Start Twitch chat monitoring - UPDATED WITH DIAGNOSTICS
        """
        if not self.parent.twitch_chat:
            self.parent.logger.twitch("Chat not initialized")
            messagebox.showwarning("Not Initialized", "Please set a channel first")
            return
        
        self.parent.twitch_start_btn.config(state=tk.DISABLED)
        if hasattr(self.parent, 'twitch_status_label'):
            self.parent.twitch_status_label.config(
                text="Status: Starting...", 
                foreground=DarkTheme.ACCENT_YELLOW
            )
        
        self.parent.logger.twitch("Starting chat monitoring...")
        
        try:
            # Try to start via ChatHandler first
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'Twitch' in chat_handler._platforms:
                success = chat_handler.start_platform('Twitch')
            else:
                # Fallback to direct start
                self.parent.logger.warning("ChatHandler not available - using direct start")
                success = self.parent.twitch_chat.start()
            
            self._update_twitch_ui_after_start(success)
            
            # Run diagnostics after starting
            if success:
                self.parent.root.after(2000, self.verify_chat_integration)
            
        except Exception as e:
            error_msg = f"Error starting Twitch monitoring: {e}"
            self.parent.logger.error(error_msg)
            self._update_twitch_ui_after_start(False, error_msg)

    def _update_twitch_ui_after_start(self, success, error_msg=None):
        """Update UI after start attempt"""
        if success:
            self.parent.logger.twitch("[SUCCESS] Chat monitoring started successfully")
            if hasattr(self.parent, 'twitch_stop_btn'):
                self.parent.twitch_stop_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'twitch_status_label'):
                self.parent.twitch_status_label.config(
                    text="Status: Running", 
                    foreground=DarkTheme.ACCENT_GREEN
                )
            
            # Enable send button if authenticated
            oauth_token = self.parent.twitch_oauth_entry.get().strip()
            if oauth_token and hasattr(self.parent, 'twitch_send_btn'):
                self.parent.twitch_send_btn.config(state=tk.NORMAL)
        else:
            if error_msg:
                self.parent.logger.error(error_msg)
            else:
                self.parent.logger.error("Failed to start Twitch chat monitoring")
            if hasattr(self.parent, 'twitch_start_btn'):
                self.parent.twitch_start_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'twitch_status_label'):
                self.parent.twitch_status_label.config(
                    text="Status: Failed", 
                    foreground=DarkTheme.ACCENT_RED
                )
        
        self.parent.root.after(1000, self.update_twitch_status)
    
    def stop_twitch_monitoring(self):
        """
        Stop Twitch chat monitoring
        UPDATED: Uses ChatHandler if available
        """
        if not self.parent.twitch_chat:
            return
        
        if hasattr(self.parent, 'twitch_stop_btn'):
            self.parent.twitch_stop_btn.config(state=tk.DISABLED)
        if hasattr(self.parent, 'twitch_send_btn'):
            self.parent.twitch_send_btn.config(state=tk.DISABLED)
        if hasattr(self.parent, 'twitch_status_label'):
            self.parent.twitch_status_label.config(
                text="Status: Stopping...", 
                foreground=DarkTheme.ACCENT_YELLOW
            )
        
        self.parent.logger.twitch("Stopping chat monitoring...")
        
        try:
            # Try to stop via ChatHandler first
            chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
            if chat_handler and 'Twitch' in chat_handler._platforms:
                chat_handler.stop_platform('Twitch')
            else:
                # Fallback to direct stop
                self.parent.twitch_chat.stop()
            
            self.parent.logger.twitch("[SUCCESS] Chat monitoring stopped")
            if hasattr(self.parent, 'twitch_start_btn'):
                self.parent.twitch_start_btn.config(state=tk.NORMAL)
            if hasattr(self.parent, 'twitch_status_label'):
                self.parent.twitch_status_label.config(
                    text="Status: Stopped", 
                    foreground=DarkTheme.FG_MUTED
                )
            self.update_twitch_status()
        except Exception as e:
            error_msg = f"Error stopping Twitch monitoring: {e}"
            self.parent.logger.error(error_msg)
            if hasattr(self.parent, 'twitch_stop_btn'):
                self.parent.twitch_stop_btn.config(state=tk.NORMAL)
    
    def send_twitch_message(self):
        """
        Send a message to Twitch chat
        NEW: Added functionality to send messages from GUI
        """
        if not self.parent.twitch_chat or not self.parent.twitch_chat.enabled:
            messagebox.showwarning("Not Connected", "Twitch chat is not running")
            return
        
        message = self.parent.twitch_send_entry.get().strip()
        if not message:
            return
        
        oauth_token = self.parent.twitch_oauth_entry.get().strip()
        if not oauth_token:
            messagebox.showwarning(
                "Authentication Required", 
                "OAuth token required to send messages.\nCurrently in read-only mode."
            )
            return
        
        try:
            success = self.parent.twitch_chat.send_message(message)
            
            if success:
                self.parent.logger.twitch(f"[SUCCESS] Sent: {message}")
                self.parent.twitch_send_entry.delete(0, tk.END)
            else:
                self.parent.logger.error(f"Failed to send message")
                messagebox.showerror("Send Failed", "Failed to send message to Twitch")
                
        except Exception as e:
            error_msg = f"Error sending message: {e}"
            self.parent.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def update_twitch_status(self):
        """
        Update Twitch status display
        UPDATED: Shows ChatHandler stats if available
        """
        if not self.parent.twitch_chat:
            if hasattr(self.parent, 'twitch_status_label'):
                self.parent.twitch_status_label.config(
                    text="Status: Not available",
                    foreground=DarkTheme.FG_MUTED
                )
            return
        
        is_running = self.parent.twitch_chat.enabled
        
        # Get message count from ChatHandler if available
        msg_count = 0
        chat_handler = getattr(self.parent.ai_core, 'chat_handler', None)
        
        if chat_handler:
            stats = chat_handler.get_stats()
            platform_stats = stats.get('platforms', {}).get('Twitch', {})
            msg_count = platform_stats.get('buffered', 0)
            
            # Also show received/processed counts
            received = platform_stats.get('received', 0)
            processed = platform_stats.get('processed', 0)
            
            if hasattr(self.parent, 'twitch_msg_label'):
                self.parent.twitch_msg_label.config(
                    text=f"Messages: {msg_count} buffered | {received} received | {processed} processed"
                )
        elif is_running and self.parent.twitch_chat.monitor:
            # Fallback to direct monitor stats
            msg_count = len(self.parent.twitch_chat.monitor.chat_buffer)
            if hasattr(self.parent, 'twitch_msg_label'):
                self.parent.twitch_msg_label.config(text=f"Messages buffered: {msg_count}")
        
        # Update status label
        if hasattr(self.parent, 'twitch_status_label'):
            status_text = "Status: " + ("Running" if is_running else "Stopped")
            status_color = DarkTheme.ACCENT_GREEN if is_running else DarkTheme.FG_MUTED
            self.parent.twitch_status_label.config(text=status_text, foreground=status_color)
        
        # Continue updating if running
        if is_running:
            self.parent.root.after(2000, self.update_twitch_status)