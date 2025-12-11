import tkinter as tk
from tkinter import ttk
from datetime import datetime
from gui_themes import DarkTheme
from personality.bot_info import agentname, username
from BASE.core.logger import MessageType, Logger

class ChatView:
    """Manages the Chat view, including system information and chat panel"""
    
    # Map MessageType enum to GUI tag names for the chat display
    MESSAGE_TYPE_TO_TAG = {
        MessageType.USER: "user",
        MessageType.AGENT: "agent",
        MessageType.SYSTEM: "system",
        MessageType.ERROR: "error",
        MessageType.WARNING: "warning",
        MessageType.SUCCESS: "success",
        MessageType.DISCORD: "discord",
        MessageType.YOUTUBE: "youtube",
        MessageType.TWITCH: "twitch",
        MessageType.MINECRAFT: "minecraft",
        MessageType.LEAGUE: "league",
        MessageType.WARUDO: "warudo",
        MessageType.MEMORY: "memory",
        MessageType.THINKING: "thinking",
        MessageType.GOAL: "goal",
        MessageType.SPEECH: "speech",
        MessageType.AUDIO: "audio",
        MessageType.PROMPT: "prompt",
        MessageType.TOOL: "tool",
    }
    
    def __init__(self, parent):
        self.parent = parent
    
    def create_chat_view(self):
        """Create the Chat view with System Information and Chat"""
        chat_paned = ttk.PanedWindow(self.parent.chat_view, orient=tk.HORIZONTAL)
        chat_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - System Information
        left_frame = ttk.Frame(chat_paned)
        chat_paned.add(left_frame, weight=1)
        
        # Right side - Chat
        right_frame = ttk.Frame(chat_paned)
        chat_paned.add(right_frame, weight=1)
        
        # Create system panel
        self.create_system_panel(left_frame)
        
        # Create chat panel
        self.create_chat_panel(right_frame)

    def create_system_panel(self, parent_frame):
        """Create system information panel"""
        system_frame = ttk.LabelFrame(parent_frame, text="System Information", style="Dark.TLabelframe")
        system_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create frame for text widget and custom scrollbar
        text_frame = ttk.Frame(system_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create custom ttk scrollbar with dark theme
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', style='Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.parent.system_log = tk.Text(
            text_frame,
            height=15,
            width=100,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9),
            bg=DarkTheme.BG_DARK,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            selectbackground=DarkTheme.ACCENT_PURPLE,
            selectforeground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.parent.system_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.parent.system_log.yview)
        
        # Note: Tag colors are now configured dynamically by the logger callback
        # No need to pre-configure them here
        
        # Flush any pending messages that were logged before GUI was ready
        self.parent.flush_pending_log_messages()

    def create_chat_panel(self, parent_frame):
        """Create chat display and input panel"""
        chat_frame = ttk.LabelFrame(parent_frame, text=f"Chat with {agentname}", style="Dark.TLabelframe")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create frame for text widget and custom scrollbar
        text_frame = ttk.Frame(chat_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create custom ttk scrollbar with dark theme
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', style='Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.parent.chat_display = tk.Text(
            text_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Segoe UI", 10),
            bg=DarkTheme.BG_DARK,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            selectbackground=DarkTheme.ACCENT_PURPLE,
            selectforeground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.parent.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.parent.chat_display.yview)
        
        # Configure color tags for different message types using Logger colors
        self._configure_chat_display_tags()
        
        self.create_input_panel(parent_frame)

    def _configure_chat_display_tags(self):
        """Configure color tags for chat display using Logger's color scheme"""
        # Get colors from the logger instance, not from class directly
        logger = self.parent.logger
        
        # Font configurations (non-color styling)
        font_configs = {
            "user": ("Segoe UI", 10, "bold"),
            "agent": ("Segoe UI", 10, "bold"),
            "system": ("Segoe UI", 9, "italic"),
            "error": ("Segoe UI", 10, "bold"),
            "warning": ("Segoe UI", 10, "bold"),
            "success": ("Segoe UI", 10, "bold"),
            "voice": ("Segoe UI", 10, "italic"),
            "discord": ("Segoe UI", 10, "bold"),
            "youtube": ("Segoe UI", 10, "bold"),
            "twitch": ("Segoe UI", 10, "bold"),
            "minecraft": ("Segoe UI", 10, "bold"),
            "league": ("Segoe UI", 10, "bold"),
            "warudo": ("Segoe UI", 10, "bold"),
            "memory": ("Segoe UI", 9, "italic"),
            "thinking": ("Segoe UI", 9, "italic"),
            "goal": ("Segoe UI", 10, "bold"),
            "speech": ("Segoe UI", 9, "italic"),
            "audio": ("Segoe UI", 9, "italic"),
            "prompt": ("Segoe UI", 9, "italic"),
            "tool": ("Segoe UI", 9, "italic"),
        }
        
        # Configure tags with colors from logger
        for tag, font in font_configs.items():
            # Convert tag name to MessageType enum
            msg_type = self._convert_legacy_type(tag)
            # Get color from logger
            color = logger._get_gui_color(msg_type)
            # Configure tag
            self.parent.chat_display.tag_configure(
                tag,
                foreground=color,
                font=font
            )

    def create_input_panel(self, parent_frame):
        """Create input panel with text box and buttons"""
        input_frame = ttk.Frame(parent_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Button panel on the right with fixed width
        button_frame = ttk.Frame(input_frame, width=80)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        button_frame.pack_propagate(False)
        
        self.parent.send_button = ttk.Button(
            button_frame,
            text="Send",
            command=self.send_message
        )
        self.parent.send_button.pack(fill=tk.X, pady=(0, 3))
        
        clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_chat
        )
        clear_button.pack(fill=tk.X, pady=(0, 3))
        
        self.parent.processing_label = tk.Label(
            button_frame,
            text="",
            font=("Segoe UI", 7),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            wraplength=75
        )
        self.parent.processing_label.pack(fill=tk.X, pady=(3, 0))
        
        # Text input on the left
        text_container = ttk.Frame(input_frame)
        text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.parent.input_text = tk.Text(
            text_container,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            selectbackground=DarkTheme.ACCENT_PURPLE,
            selectforeground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=0,
            relief="flat"
        )
        self.parent.input_text.pack(fill=tk.BOTH, expand=True)
        
        self.parent.input_text.bind("<Control-Return>", lambda e: self.send_message())
        self.parent.input_text.bind("<Return>", self.handle_return)

    def handle_return(self, event):
        if event.state & 0x1:
            return None
        else:
            self.send_message()
            return "break"

    def send_message(self):
        import time
        message = self.parent.input_text.get("1.0", tk.END).strip()
        if not message:
            return
        self.parent.input_text.delete("1.0", tk.END)
        self.add_message(username, message, MessageType.USER)
        self.parent.input_queue.put(message)
        self.parent.last_interaction = time.time()

    def add_message(self, sender, message, msg_type=MessageType.USER):
        """
        Instance method - add a message to the chat display with proper color formatting
        
        Args:
            sender: The sender name
            message: The message text
            msg_type: MessageType enum or legacy string type
        """
        # Convert legacy string types to MessageType enum
        if isinstance(msg_type, str):
            msg_type = self._convert_legacy_type(msg_type)
        
        self.parent.chat_display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add timestamp in system color
        self.parent.chat_display.insert(tk.END, f"[{timestamp}] ", "system")
        
        # Get the tag name for this message type
        tag = self.MESSAGE_TYPE_TO_TAG.get(msg_type, "system")
        
        # Format message based on type
        if msg_type == MessageType.SYSTEM:
            self.parent.chat_display.insert(tk.END, f"{message}\n", tag)
        elif msg_type in (MessageType.ERROR, MessageType.WARNING):
            self.parent.chat_display.insert(tk.END, f"{sender}: ", tag)
            self.parent.chat_display.insert(tk.END, f"{message}\n", tag)
        elif msg_type == MessageType.USER:
            self.parent.chat_display.insert(tk.END, f"{sender}: ", tag)
            self.parent.chat_display.insert(tk.END, f"{message}\n\n")
        elif msg_type == MessageType.BOT:
            self.parent.chat_display.insert(tk.END, f"{sender}: ", tag)
            self.parent.chat_display.insert(tk.END, f"{message}\n\n")
        else:
            # For all other types (Discord, YouTube, etc.)
            self.parent.chat_display.insert(tk.END, f"{sender}: ", tag)
            self.parent.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.parent.chat_display.see(tk.END)
        self.parent.chat_display.config(state=tk.DISABLED)


    @staticmethod
    def _get_tag_for_type(msg_type):
        """
        Convert MessageType enum to display tag
        
        Args:
            msg_type: MessageType enum value
            
        Returns:
            str: Tag name for text formatting
        """
        from BASE.core.logger import MessageType
        
        type_map = {
            MessageType.USER: "user",
            MessageType.AGENT: "agent",
            MessageType.SYSTEM: "system",
            MessageType.ERROR: "error",
            MessageType.SPEECH: "user",  # Speech input displays like user
            MessageType.TOOL: "tool",
            MessageType.MEMORY: "memory",
            MessageType.DISCORD: "discord",
            MessageType.YOUTUBE: "youtube",
            MessageType.TWITCH: "twitch",
            MessageType.WARUDO: "warudo"
        }
        
        return type_map.get(msg_type, "system")

    @staticmethod
    def add_chat_message(gui_instance, sender, message, msg_type, original_timestamp=None):
        """
        Add message to chat display with timestamp
        
        Args:
            gui_instance: GUI instance
            sender: Message sender name
            message: Message content
            msg_type: MessageType enum value
            original_timestamp: Optional original timestamp string (e.g., "03:59:56 PM")
        """
        gui_instance.chat_display.config(state="normal")
        
        # Use original timestamp if provided, otherwise current time
        if original_timestamp:
            display_timestamp = original_timestamp
        else:
            from datetime import datetime
            display_timestamp = datetime.now().strftime("%I:%M:%S %p")
        
        # Add timestamp
        gui_instance.chat_display.insert("end", f"[{display_timestamp}] ", "system")
        
        # Add sender and message based on type
        from BASE.core.logger import MessageType
        
        if msg_type == MessageType.SYSTEM:
            gui_instance.chat_display.insert("end", f"{message}\n", "system")
        elif msg_type == MessageType.ERROR:
            gui_instance.chat_display.insert("end", f"{sender}: {message}\n", "error")
        else:
            # User, agent, speech, etc.
            tag = ChatView._get_tag_for_type(msg_type)
            gui_instance.chat_display.insert("end", f"{sender}: ", tag)
            gui_instance.chat_display.insert("end", f"{message}\n\n")
        
        gui_instance.chat_display.see("end")
        gui_instance.chat_display.config(state="disabled")
        
        
    @staticmethod
    def _convert_legacy_type(legacy_type):
        """
        Convert legacy string message types to MessageType enum
        
        Args:
            legacy_type: String type like "user", "agent", "system", "voice_input"
            
        Returns:
            MessageType enum value
        """
        legacy_map = {
            "user": MessageType.USER,
            "agent": MessageType.AGENT,
            "system": MessageType.SYSTEM,
            "error": MessageType.ERROR,
            "warning": MessageType.WARNING,
            "success": MessageType.SUCCESS,
            "voice_input": MessageType.USER,
            "voice": MessageType.USER,
            "discord": MessageType.DISCORD,
            "youtube": MessageType.YOUTUBE,
            "twitch": MessageType.TWITCH,
            "minecraft": MessageType.MINECRAFT,
            "league": MessageType.LEAGUE,
            "warudo": MessageType.WARUDO,
            "memory": MessageType.MEMORY,
            "thinking": MessageType.THINKING,
            "goal": MessageType.GOAL,
            "speech": MessageType.SPEECH,
            "audio": MessageType.AUDIO,
            "prompt": MessageType.PROMPT,
            "tool": MessageType.TOOL,
        }
        
        return legacy_map.get(legacy_type, MessageType.SYSTEM)
        
        
    def clear_chat(self):
        self.parent.chat_display.config(state=tk.NORMAL)
        self.parent.chat_display.delete("1.0", tk.END)
        self.parent.chat_display.config(state=tk.DISABLED)
        self.parent.logger.system("Chat cleared")