# Filename: BASE/interface/gui_discord_panel.py
"""
Discord panel for GUI - manages Discord bot controls, settings, and status
Updated to use Logger instance for proper colorization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from BASE.interface.gui_themes import DarkTheme


class DiscordPanel:
    """Manages Discord integration panel in GUI with settings"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.discord_integration = None
        self.status_label = None
        self.start_button = None
        self.stop_button = None
        self.stats_text = None
        self.update_scheduled = False
        
        # Setting variables
        self.token_var = None
        self.prefix_var = None
        self.auto_start_var = None
        self.channels_var = None
        self.guilds_var = None
        self.respond_mentions_var = None
        self.respond_replies_var = None
        self.respond_dms_var = None
        
    def create_discord_panel(self, parent_frame):
        """Create Discord control panel with settings"""
        discord_frame = ttk.LabelFrame(
            parent_frame, 
            text="Discord Bot", 
            style="Dark.TLabelframe"
        )
        discord_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Get Discord integration from AI core
        self.discord_integration = getattr(self.gui.ai_core, 'discord_integration', None)
        
        # Settings section
        self._create_settings_section(discord_frame)
        
        # Status section
        self._create_status_section(discord_frame)
        
        # Control buttons
        self._create_control_buttons(discord_frame)
        
        # Statistics section
        self._create_stats_section(discord_frame)
        
        # Initial update
        self.update_status()
        
        # Auto-update every 3 seconds
        self.schedule_update()
    
    def _create_settings_section(self, parent):
        """Create settings configuration section"""
        settings_frame = ttk.LabelFrame(parent, text="Configuration", style="Dark.TLabelframe")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Bot Token
        token_frame = ttk.Frame(settings_frame)
        token_frame.pack(fill=tk.X, padx=3, pady=2)
        
        tk.Label(
            token_frame,
            text="Bot Token:",
            font=("Arial", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.token_var = tk.StringVar(value=self.gui.config.discord_token)
        token_entry = ttk.Entry(token_frame, textvariable=self.token_var, show="*", width=40)
        token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        ttk.Button(
            token_frame,
            text="Show",
            command=lambda: self._toggle_token_visibility(token_entry),
            width=6
        ).pack(side=tk.LEFT, padx=2)
        
        # Command Prefix
        prefix_frame = ttk.Frame(settings_frame)
        prefix_frame.pack(fill=tk.X, padx=3, pady=2)
        
        tk.Label(
            prefix_frame,
            text="Command Prefix:",
            font=("Arial", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.prefix_var = tk.StringVar(value=self.gui.config.discord_command_prefix)
        ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=10).pack(side=tk.LEFT, padx=2)
        
        # Auto Start
        self.auto_start_var = tk.BooleanVar(value=self.gui.config.discord_auto_start)
        ttk.Checkbutton(
            prefix_frame,
            text="Auto-start on launch",
            variable=self.auto_start_var
        ).pack(side=tk.LEFT, padx=10)
        
        # Allowed Channels
        channels_frame = ttk.Frame(settings_frame)
        channels_frame.pack(fill=tk.X, padx=3, pady=2)
        
        tk.Label(
            channels_frame,
            text="Allowed Channels:",
            font=("Arial", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        channels_val = ','.join(map(str, self.gui.config.discord_allowed_channels)) if self.gui.config.discord_allowed_channels else ""
        self.channels_var = tk.StringVar(value=channels_val)
        ttk.Entry(channels_frame, textvariable=self.channels_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(
            channels_frame,
            text="(comma-separated IDs)",
            font=("Arial", 8),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        ).pack(side=tk.LEFT, padx=2)
        
        # Allowed Guilds
        guilds_frame = ttk.Frame(settings_frame)
        guilds_frame.pack(fill=tk.X, padx=3, pady=2)
        
        tk.Label(
            guilds_frame,
            text="Allowed Guilds:",
            font=("Arial", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        guilds_val = ','.join(map(str, self.gui.config.discord_allowed_guilds)) if self.gui.config.discord_allowed_guilds else ""
        self.guilds_var = tk.StringVar(value=guilds_val)
        ttk.Entry(guilds_frame, textvariable=self.guilds_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(
            guilds_frame,
            text="(comma-separated IDs)",
            font=("Arial", 8),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        ).pack(side=tk.LEFT, padx=2)
        
        # Behavior options
        behavior_frame = ttk.Frame(settings_frame)
        behavior_frame.pack(fill=tk.X, padx=3, pady=2)
        
        tk.Label(
            behavior_frame,
            text="Respond to:",
            font=("Arial", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.respond_mentions_var = tk.BooleanVar(value=self.gui.config.discord_respond_to_mentions)
        ttk.Checkbutton(behavior_frame, text="Mentions", variable=self.respond_mentions_var).pack(side=tk.LEFT, padx=5)
        
        self.respond_replies_var = tk.BooleanVar(value=self.gui.config.discord_respond_to_replies)
        ttk.Checkbutton(behavior_frame, text="Replies", variable=self.respond_replies_var).pack(side=tk.LEFT, padx=5)
        
        self.respond_dms_var = tk.BooleanVar(value=self.gui.config.discord_respond_to_dms)
        ttk.Checkbutton(behavior_frame, text="DMs", variable=self.respond_dms_var).pack(side=tk.LEFT, padx=5)
        
        # Save button
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, padx=3, pady=5)
        
        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=15
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Reload Config",
            command=self.reload_settings,
            width=15
        ).pack(side=tk.LEFT, padx=2)
    
    def _create_status_section(self, parent):
        """Create status display section"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(
            status_frame,
            text="Status:",
            font=("Arial", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER
        ).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            status_frame,
            text="Not Configured",
            font=("Arial", 9),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_control_buttons(self, parent):
        """Create control buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Bot",
            command=self.start_discord,
            width=12
        )
        self.start_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Bot",
            command=self.stop_discord,
            width=12,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Refresh Status",
            command=self.update_status,
            width=12
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.test_connection,
            width=12
        ).pack(side=tk.LEFT, padx=2)
    
    def _create_stats_section(self, parent):
        """Create statistics display section"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=6,
            font=("Consolas", 8),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            borderwidth=0,
            highlightthickness=0,
            wrap=tk.WORD
        )
        self.stats_text.pack(fill=tk.X)
        self.stats_text.config(state=tk.DISABLED)
    
    def _toggle_token_visibility(self, entry_widget):
        """Toggle token visibility"""
        current = entry_widget.cget('show')
        entry_widget.config(show='' if current == '*' else '*')
    
    def save_settings(self):
        """Save Discord settings to config.json"""
        try:
            # Validate token
            token = self.token_var.get().strip()
            if not token:
                messagebox.showwarning("Invalid Token", "Bot token cannot be empty")
                return
            
            # Parse channel and guild IDs
            channels = []
            if self.channels_var.get().strip():
                try:
                    channels = [int(x.strip()) for x in self.channels_var.get().split(',') if x.strip()]
                except ValueError:
                    messagebox.showerror("Invalid Input", "Channel IDs must be numbers")
                    return
            
            guilds = []
            if self.guilds_var.get().strip():
                try:
                    guilds = [int(x.strip()) for x in self.guilds_var.get().split(',') if x.strip()]
                except ValueError:
                    messagebox.showerror("Invalid Input", "Guild IDs must be numbers")
                    return
            
            # Load current config
            config_path = Path(__file__).parent.parent.parent / "personality" / "config.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update Discord section
            config['discord'] = {
                'enabled': True,
                'bot_token': token,
                'command_prefix': self.prefix_var.get().strip(),
                'auto_start': self.auto_start_var.get(),
                'allowed_channels': channels,
                'allowed_guilds': guilds,
                'respond_to_mentions': self.respond_mentions_var.get(),
                'respond_to_replies': self.respond_replies_var.get(),
                'respond_to_dms': self.respond_dms_var.get(),
                'respond_in_threads': self.gui.config.discord_respond_in_threads,
                'typing_indicator': self.gui.config.discord_typing_indicator,
                'message_history_limit': self.gui.config.discord_message_history_limit,
                'max_message_length': self.gui.config.discord_max_message_length,
                'split_long_messages': self.gui.config.discord_split_long_messages,
                'command_cooldown': self.gui.config.discord_command_cooldown
            }
            
            # Save config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update in-memory config
            self.gui.config.discord_token = token
            self.gui.config.discord_command_prefix = self.prefix_var.get().strip()
            self.gui.config.discord_auto_start = self.auto_start_var.get()
            self.gui.config.discord_allowed_channels = channels if channels else None
            self.gui.config.discord_allowed_guilds = guilds if guilds else None
            self.gui.config.discord_respond_to_mentions = self.respond_mentions_var.get()
            self.gui.config.discord_respond_to_replies = self.respond_replies_var.get()
            self.gui.config.discord_respond_to_dms = self.respond_dms_var.get()
            self.gui.config.discord_enabled = True
            self.gui.config.IN_DISCORD_CHAT = True
            
            self.gui.logger.discord("Settings saved to config.json")
            messagebox.showinfo("Success", "Settings saved! Restart the bot for changes to take effect.")
            
        except Exception as e:
            self.gui.logger.error(f"Failed to save Discord settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")
    
    def reload_settings(self):
        """Reload settings from config.json"""
        try:
            # Reload config
            
            # Update UI
            self.token_var.set(self.gui.config.discord_token)
            self.prefix_var.set(self.gui.config.discord_command_prefix)
            self.auto_start_var.set(self.gui.config.discord_auto_start)
            
            channels_val = ','.join(map(str, self.gui.config.discord_allowed_channels)) if self.gui.config.discord_allowed_channels else ""
            self.channels_var.set(channels_val)
            
            guilds_val = ','.join(map(str, self.gui.config.discord_allowed_guilds)) if self.gui.config.discord_allowed_guilds else ""
            self.guilds_var.set(guilds_val)
            
            self.respond_mentions_var.set(self.gui.config.discord_respond_to_mentions)
            self.respond_replies_var.set(self.gui.config.discord_respond_to_replies)
            self.respond_dms_var.set(self.gui.config.discord_respond_to_dms)
            
            self.gui.logger.discord("Settings reloaded from config.json")
            
        except Exception as e:
            self.gui.logger.error(f"Failed to reload settings: {e}")
    
    def test_connection(self):
        """Test Discord bot connection"""
        token = self.token_var.get().strip()
        if not token:
            messagebox.showwarning("No Token", "Please enter a bot token first")
            return
        
        self.gui.logger.discord("Testing Discord connection...")
        
        try:
            import discord
            import asyncio
            
            async def test():
                intents = discord.Intents.default()
                client = discord.Client(intents=intents)
                
                @client.event
                async def on_ready():
                    self.gui.logger.discord(f"Connected as {client.user}")
                    self.gui.logger.discord(f"Bot ID: {client.user.id}")
                    await client.close()
                
                try:
                    await asyncio.wait_for(client.start(token), timeout=10)
                except asyncio.TimeoutError:
                    await client.close()
            
            asyncio.run(test())
            messagebox.showinfo("Success", "Connection test successful!")
            
        except discord.LoginFailure:
            self.gui.logger.error("Invalid token")
            messagebox.showerror("Error", "Invalid bot token")
        except Exception as e:
            self.gui.logger.error(f"Connection test failed: {e}")
            messagebox.showerror("Error", f"Connection test failed:\n{e}")
    
    def start_discord(self):
        """Start Discord bot through unified chat handler"""
        if not self.discord_integration:
            # Need to initialize
            token = self.token_var.get().strip()
            if not token:
                messagebox.showwarning("No Token", "Please configure and save settings first")
                return
            
            try:
                self.gui._initialize_discord()
                self.discord_integration = getattr(self.gui.ai_core, 'discord_integration', None)
                
                if not self.discord_integration:
                    messagebox.showerror("Error", "Failed to initialize Discord integration")
                    return
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize:\n{e}")
                return
        
        try:
            if self.discord_integration.running:
                self.gui.logger.discord("Bot already running")
                return
            
            # Start through chat handler (unified)
            if hasattr(self.gui.ai_core, 'chat_handler'):
                success = self.gui.ai_core.chat_handler.start_platform("Discord")
                if not success:
                    messagebox.showerror("Error", "Failed to start Discord through chat handler")
                    return
            else:
                # Fallback to direct start
                self.gui.logger.discord("Starting Discord bot...")
                self.discord_integration.start()
            
            # Update button states
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Update status after brief delay
            self.gui.root.after(2000, self.update_status)
            
        except Exception as e:
            self.gui.logger.error(f"Failed to start Discord bot: {e}")
            messagebox.showerror("Error", f"Failed to start bot:\n{e}")
    
    def stop_discord(self):
        """Stop Discord bot"""
        if not self.discord_integration:
            return
        
        try:
            self.gui.logger.discord("Stopping Discord bot...")
            self.discord_integration.stop()
            
            # Update button states
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Update status
            self.update_status()
            
        except Exception as e:
            self.gui.logger.error(f"Failed to stop Discord bot: {e}")
    
    def update_status(self):
        """Update Discord status display"""
        if not self.discord_integration:
            self.status_label.config(
                text="Not Initialized",
                foreground=DarkTheme.FG_MUTED
            )
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "Configure settings and save to initialize")
            self.stats_text.config(state=tk.DISABLED)
            return
        
        try:
            # Get status
            running = self.discord_integration.running
            enabled = self.discord_integration.enabled
            stats = self.discord_integration.stats
            
            # Update status label
            if running and enabled:
                status_text = "Connected & Running"
                status_color = DarkTheme.ACCENT_GREEN
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
            elif running:
                status_text = "Starting..."
                status_color = DarkTheme.ACCENT_BLUE
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
            else:
                status_text = "Stopped"
                status_color = DarkTheme.ACCENT_RED
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
            
            self.status_label.config(text=status_text, foreground=status_color)
            
            # Update statistics
            guild_count = 0
            if self.discord_integration.bot and self.discord_integration.bot.guilds:
                guild_count = len(self.discord_integration.bot.guilds)
            
            uptime = "N/A"
            if stats.get('start_time'):
                from datetime import datetime
                elapsed = datetime.now() - stats['start_time']
                hours = elapsed.total_seconds() / 3600
                uptime = f"{hours:.1f}h"
            
            stats_text = f"""Messages Received: {stats['messages_received']}
Messages Sent: {stats['messages_sent']}
Errors: {stats['errors']}
Servers: {guild_count}
Uptime: {uptime}
Prefix: {self.discord_integration.command_prefix}"""
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.gui.logger.error(f"Error updating Discord status: {e}")
    
    def schedule_update(self):
        """Schedule periodic status updates"""
        if not self.update_scheduled:
            self.update_scheduled = True
            self._do_scheduled_update()
    
    def _do_scheduled_update(self):
        """Perform scheduled update"""
        try:
            if self.discord_integration:
                self.update_status()
        except Exception as e:
            pass
        
        # Schedule next update
        if hasattr(self.gui, 'root') and self.gui.root:
            self.gui.root.after(3000, self._do_scheduled_update)