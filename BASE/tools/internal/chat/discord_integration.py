# Filename: BASE/tools/chat/discord_integration.py
"""
Discord Integration for VTuber AI
REFACTORED: Uses message callback pattern for unified chat handling
"""

import discord
from discord.ext import commands
import asyncio
import threading
from typing import Optional, Callable, List, Dict
from datetime import datetime
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.core.logger import Logger, MessageType


# Marker for availability checks
DISCORD_AVAILABLE = 'discord' in sys.modules


class DiscordIntegration:
    """
    Discord bot integration for unified chat system
    REFACTORED: Uses callback pattern for message handling
    """
    
    def __init__(
        self,
        token: str,
        command_prefix: str = "!",
        allowed_channels: Optional[List[int]] = None,
        allowed_guilds: Optional[List[int]] = None,
        max_message_length: int = 2000,
        auto_start: bool = False,
        gui_logger: Optional[Callable] = None
    ):
        """
        Initialize Discord integration
        
        Args:
            token: Discord bot token
            command_prefix: Prefix for bot commands (default: !)
            allowed_channels: List of channel IDs to monitor (None = all)
            allowed_guilds: List of guild IDs to monitor (None = all)
            max_message_length: Max chars per Discord message
            auto_start: Start bot on initialization
            gui_logger: GUI logging callback
        """
        self.token = token
        self.command_prefix = command_prefix
        # Convert to int set if not None
        self.allowed_channels = set(map(int, allowed_channels)) if allowed_channels else None
        self.allowed_guilds = set(map(int, allowed_guilds)) if allowed_guilds else None
        self.max_message_length = max_message_length
        self.enabled = False
        
        # Initialize logger
        self.logger = Logger(
            name="Discord",
            enable_timestamps=True,
            enable_console=False,
            gui_callback=gui_logger
            config=config
        )
        
        # UNIFIED: Message callback for chat handler
        self._message_callback = None
        
        # Message buffer for context
        self.context_buffer = []
        self.max_context_messages = 10
        
        # Bot setup
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True
        
        self.bot = commands.Bot(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None
        )
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'errors': 0,
            'start_time': None
        }
        
        # Threading
        self.bot_thread = None
        self.running = False
        self.loop = None
        
        # Response queue for sending messages
        self._response_queue = asyncio.Queue() if asyncio.get_event_loop().is_running() else None
        self._response_task = None
        
        # Setup event handlers
        self._setup_events()
        self._setup_commands()
        
        self.logger.discord(f"Bot configured: prefix='{command_prefix}', auto_start={auto_start}")
        if self.allowed_channels:
            self.logger.discord(f"Restricted to channels: {list(self.allowed_channels)}")
        if self.allowed_guilds:
            self.logger.discord(f"Restricted to guilds: {list(self.allowed_guilds)}")
        
        if auto_start:
            self.start()
    
    # ========================================================================
    # UNIFIED CALLBACK PATTERN
    # ========================================================================
    
    def set_message_callback(self, callback: Callable):
        """
        Set callback for incoming messages (called by ChatHandler)
        
        Args:
            callback: Function(message_dict) to call with new messages
        """
        self._message_callback = callback
        self.logger.discord("Message callback registered with ChatHandler")

        
    def _resolve_mentions(self, message: discord.Message) -> str:
        """
        Replace Discord mention IDs with actual usernames
        
        Args:
            message: Discord message object
            
        Returns:
            Message content with resolved mentions
        """
        content = message.content
        
        # Resolve user mentions <@123456> or <@!123456>
        for mention in message.mentions:
            # Handle both formats: <@id> and <@!id>
            content = content.replace(f'<@{mention.id}>', f'@{mention.display_name}')
            content = content.replace(f'<@!{mention.id}>', f'@{mention.display_name}')
        
        # Resolve role mentions <@&123456>
        if hasattr(message, 'role_mentions'):
            for role in message.role_mentions:
                content = content.replace(f'<@&{role.id}>', f'@{role.name}')
        
        # Resolve channel mentions <#123456>
        if hasattr(message, 'channel_mentions'):
            for channel in message.channel_mentions:
                content = content.replace(f'<#{channel.id}>', f'#{channel.name}')
        
        return content
    
    def _invoke_message_callback(self, message: discord.Message):
        """
        Invoke message callback with normalized message format
        
        Args:
            message: Discord message object
        """
        if not self._message_callback:
            return
        
        # Resolve mentions to usernames
        resolved_content = self._resolve_mentions(message)
        
        # Normalize to unified format (matching chat_handler.py expectations)
        message_dict = {
            'author': message.author.display_name or message.author.name,
            'message': resolved_content,  # Use resolved content
            'timestamp': message.created_at.timestamp() * 1000,  # Convert to milliseconds
            'user_id': str(message.author.id),
            'badges': self._extract_badges(message.author),
            'emotes': [],  # Discord emotes handled differently
            'color': str(message.author.color) if hasattr(message.author, 'color') else None,
            'channel_id': message.channel.id,
            'channel_name': message.channel.name if hasattr(message.channel, 'name') else 'DM',
            'guild_id': message.guild.id if message.guild else None,
            'guild_name': message.guild.name if message.guild else None,
            'is_mentioned': self.bot.user in message.mentions,
            'is_reply': message.reference is not None
        }
        
        # Invoke callback
        try:
            self._message_callback(message_dict)
        except Exception as e:
            self.logger.error(f"Error in message callback: {e}")
    
    def _extract_badges(self, member) -> List[str]:
        """Extract user badges/roles"""
        badges = []
        if hasattr(member, 'roles'):
            for role in member.roles:
                if role.name != '@everyone':
                    badges.append(role.name)
        return badges
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def _setup_events(self):
        """Setup Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            self.logger.discord(f"Bot logged in as {self.bot.user}")
            self.logger.discord(f"Connected to {len(self.bot.guilds)} guilds")
            self.stats['start_time'] = datetime.now()
            self.enabled = True
            
            # Start response processor
            if self._response_queue is None:
                self._response_queue = asyncio.Queue()
            self._response_task = asyncio.create_task(self._process_responses())

        @self.bot.event
        async def on_message(message: discord.Message):
            self.logger.debug(
                f"on_message triggered - Author: {message.author}, "
                f"Channel: {message.channel.id}, Content: {message.content[:50]}...",
                MessageType.DISCORD
            )
            
            # Ignore own messages
            if message.author == self.bot.user:
                self.logger.debug("Ignoring own message", MessageType.DISCORD)
                return
            
            # Check guild restrictions
            if self.allowed_guilds and message.guild:
                self.logger.debug(
                    f"Checking guild {message.guild.id} against allowed: {self.allowed_guilds}",
                    MessageType.DISCORD
                )
                if message.guild.id not in self.allowed_guilds:
                    self.logger.debug(
                        f"Guild {message.guild.id} not in allowed guilds",
                        MessageType.DISCORD
                    )
                    return
            
            # Check channel restrictions
            if self.allowed_channels:
                self.logger.debug(
                    f"Checking channel {message.channel.id} against allowed: {self.allowed_channels}",
                    MessageType.DISCORD
                )
                if message.channel.id not in self.allowed_channels:
                    self.logger.debug(
                        f"Channel {message.channel.id} not in allowed channels",
                        MessageType.DISCORD
                    )
                    return
            
            # Process commands first
            await self.bot.process_commands(message)
            
            # Don't process commands as regular messages
            if message.content.startswith(self.command_prefix):
                self.logger.debug("Message is a command, skipping as regular message", MessageType.DISCORD)
                return
            
            self.logger.discord(f"Processing message from {message.author}: {message.content[:50]}...")
            self.stats['messages_received'] += 1
            
            # Add to context buffer
            self._add_to_context(message)
            
            # UNIFIED: Send to ChatHandler via callback
            self._invoke_message_callback(message)
    
    def _setup_commands(self):
        """Setup bot commands"""
        
        @self.bot.command(name='ping')
        async def ping(ctx):
            """Check bot responsiveness"""
            latency = round(self.bot.latency * 1000)
            await ctx.send(f"Pong! Latency: {latency}ms")
            self.logger.discord(f"Ping command used by {ctx.author} - {latency}ms")
        
        @self.bot.command(name='status')
        async def status(ctx):
            """Show bot statistics"""
            uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else None
            
            embed = discord.Embed(
                title="Bot Status",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="Messages Received", value=self.stats['messages_received'])
            embed.add_field(name="Messages Sent", value=self.stats['messages_sent'])
            embed.add_field(name="Errors", value=self.stats['errors'])
            
            if uptime:
                hours = uptime.total_seconds() / 3600
                embed.add_field(name="Uptime", value=f"{hours:.1f} hours")
            
            embed.add_field(name="Guilds", value=len(self.bot.guilds))
            embed.add_field(name="Enabled", value="[SUCCESS]" if self.enabled else "[FAILED]")
            
            await ctx.send(embed=embed)
            self.logger.discord(f"Status command used by {ctx.author}")
        
        @self.bot.command(name='clear_context')
        async def clear_context(ctx):
            """Clear conversation context"""
            self.context_buffer.clear()
            await ctx.send("[SUCCESS] Context cleared!")
            self.logger.discord(f"Context cleared by {ctx.author}")
    
    # ========================================================================
    # CONTEXT MANAGEMENT
    # ========================================================================
    
    def _add_to_context(self, message: discord.Message):
        """Add message to context buffer"""
        self.context_buffer.append({
            'author': str(message.author),
            'content': message.content,
            'timestamp': message.created_at
        })
        
        # Keep only recent messages
        if len(self.context_buffer) > self.max_context_messages:
            self.context_buffer.pop(0)
    
    def get_context_for_ai(self) -> str:
        """Get formatted context for AI (used by ChatHandler)"""
        if not self.context_buffer:
            return ""
        
        context_lines = []
        for msg in self.context_buffer:
            author = msg['author']
            content = msg['content']
            context_lines.append(f"{author}: {content}")
        
        return "\n".join(context_lines)
    
    # ========================================================================
    # SENDING MESSAGES (Response Queue Pattern)
    # ========================================================================
    
    async def _process_responses(self):
        """Background task to process response queue"""
        while True:
            try:
                channel_id, content = await self._response_queue.get()
                
                # Get channel
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    self.logger.error(f"Channel {channel_id} not found")
                    continue
                
                # Send message
                await self._send_message_internal(channel, content)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in response processor: {e}")
    
    def send_message(self, channel_id: int, content: str):
        """
        Queue message for sending (thread-safe)
        
        Args:
            channel_id: Discord channel ID
            content: Message content
        """
        if not self.running or not self._response_queue:
            self.logger.error("Cannot send message: Bot not running")
            return
        
        # Queue for sending
        asyncio.run_coroutine_threadsafe(
            self._response_queue.put((channel_id, content)),
            self.loop
        )
    
    async def _send_message_internal(self, channel: discord.TextChannel, content: str):
        """
        Internal method to send message (handles long messages)
        
        Args:
            channel: Discord channel
            content: Message content
        """
        content = self._sanitize_message(content)
        
        if len(content) <= self.max_message_length:
            await channel.send(content)
            self.stats['messages_sent'] += 1
            self.logger.discord(f"Sent message to #{channel.name}")
        else:
            chunks = self._split_message(content)
            self.logger.discord(f"Splitting long message into {len(chunks)} chunks")
            for chunk in chunks:
                await channel.send(chunk)
                self.stats['messages_sent'] += 1
                await asyncio.sleep(0.5)
    
    def _sanitize_message(self, content: str) -> str:
        """Remove potentially problematic content"""
        # Zero-width space to prevent accidental pings
        content = content.replace('@everyone', '@\u200beveryone')
        content = content.replace('@here', '@\u200bhere')
        # Simple text replacement for remaining role/user mentions
        content = re.sub(r'<@&(\d+)>', r'[role]', content) 
        content = re.sub(r'<@!?(\d+)>', r'[user]', content)
        return content
    
    def _split_message(self, content: str) -> List[str]:
        """Split long message into chunks"""
        chunks = []
        current_chunk = ""
        
        # Split by sentence-ending punctuation and newlines
        parts = re.split(r'([.!?\n])', content)
        
        for i in range(0, len(parts), 2):
            part = parts[i]
            separator = parts[i+1] if i+1 < len(parts) else ''
            segment = part + separator
            
            if len(current_chunk) + len(segment) <= self.max_message_length - 50:
                current_chunk += segment
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = segment
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Fallback for chunks that are still too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_message_length:
                for i in range(0, len(chunk), self.max_message_length):
                    final_chunks.append(chunk[i:i + self.max_message_length].strip())
            else:
                final_chunks.append(chunk)
                
        return final_chunks
    
    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================
    
    def start(self):
        """Start the Discord bot"""
        if self.running:
            self.logger.discord("Bot already running")
            return
        
        if not self.token or self.token.strip() == "":
            self.logger.error("Cannot start Discord bot: Token is not set.")
            return
            
        self.running = True
        self.bot_thread = threading.Thread(
            target=self._run_bot,
            daemon=True
        )
        self.bot_thread.start()
        self.logger.discord("Bot starting...")
    
    def _run_bot(self):
        """Run bot in thread"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.bot.start(self.token))
        except discord.errors.LoginFailure:
            self.logger.error("Bot failed to log in: Invalid token.")
            self.running = False
            self.enabled = False
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
    
    def stop(self):
        """Stop the Discord bot"""
        if not self.running:
            return
        
        self.logger.discord("Stopping bot...")
        
        # Cancel response task
        if self._response_task and not self._response_task.done():
            self._response_task.cancel()
        
        if self.loop and self.bot:
            future = asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
            try:
                future.result(timeout=5.0) 
            except asyncio.TimeoutError:
                self.logger.warning("Timeout waiting for Discord bot to stop gracefully.")
            except Exception as e:
                self.logger.error(f"Error during bot close: {e}")
        
        if self.loop and self.loop.is_running():
             self.loop.stop()
             
        self.running = False
        self.enabled = False