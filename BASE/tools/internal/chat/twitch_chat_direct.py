# ============================================================================
# BASE/tools/chat/twitch_chat_direct.py
# ============================================================================
"""
Twitch Chat Integration - UPDATED for Centralized Architecture
Works with ChatHandler for unified message routing to thought processor
"""
import time
import threading
import socket
from datetime import datetime
from typing import Optional, Callable, List, Dict
import atexit
import weakref
import re

from BASE.core.logger import Logger, MessageType

TWITCH_AVAILABLE = True
_active_instances = weakref.WeakSet()
_initialization_lock = threading.Lock()


class TwitchChatMonitor:
    """Monitor Twitch live chat using IRC"""

    def __init__(self, channel: str, max_messages: int = 10, message_callback: Optional[Callable] = None,
                 oauth_token: str = "", nickname: str = "", gui_logger: Optional[Callable[..., None]] = None):
        self.channel = channel.lower().strip().lstrip('#')
        self.max_messages = max_messages
        self.message_callback = message_callback

        self.oauth_token = oauth_token
        self.nickname = nickname if nickname else f"justinfan{int(time.time()) % 100000}"
        self.use_auth = bool(oauth_token and nickname)

        self.chat_buffer: List[Dict] = []
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        self.shutdown_flag = threading.Event()
        self.start_time = None
        self.connected = False

        self.logger = Logger(
            name="Twitch Chat",
            enable_timestamps=True,
            enable_console=False,
            gui_callback=gui_logger,
            config=config
        )

        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.irc_socket = None

        _active_instances.add(self)

    def _parse_irc_message(self, message: str) -> Optional[Dict]:
        """
        Parse IRC message to extract username and message text
        FIXED: Strip ALL IRC metadata completely
        """
        try:
            if message.startswith("PING"):
                return {"type": "ping", "data": message.split(":", 1)[1].strip()}

            if "PRIVMSG" in message:
                # Extract username (after : and before !)
                username_match = re.search(r':([^!]+)!', message)
                if not username_match:
                    return None
                username = username_match.group(1)

                # Extract message text (after final :)
                # Split on PRIVMSG first to avoid metadata confusion
                if 'PRIVMSG' in message:
                    privmsg_part = message.split('PRIVMSG', 1)[1]
                    # Now extract just the message content after the final :
                    if ':' in privmsg_part:
                        text = privmsg_part.split(':', 1)[1].strip()
                    else:
                        return None
                else:
                    return None
                
                # Final cleanup: remove any remaining IRC metadata patterns
                # Pattern: numbers-numbers;key=value;key=value: username: message
                # We want just the message part
                if ';' in text and ':' in text:
                    # This might be metadata still attached
                    # Find the last : which should be before the actual message
                    parts = text.rsplit(':', 1)
                    if len(parts) == 2:
                        potential_msg = parts[1].strip()
                        # Check if the first part looks like metadata
                        if '=' in parts[0] or ';' in parts[0]:
                            text = potential_msg

                return {
                    "type": "message",
                    "author": username,
                    "message": text
                }

            return None

        except Exception as e:
            # Log parsing errors for debugging
            return None

    def start(self):
        """Start monitoring the Twitch chat"""
        with _initialization_lock:
            if self.running:
                return True

            for instance in list(_active_instances):
                if instance is not self and instance.running:
                    try:
                        instance._force_stop()
                    except:
                        pass

            try:
                self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.irc_socket.settimeout(10.0)
                self.irc_socket.connect((self.server, self.port))

                if self.use_auth:
                    self.irc_socket.send(f"PASS {self.oauth_token}\r\n".encode('utf-8'))
                else:
                    self.irc_socket.send(b"PASS SCHMOOPIIE\r\n")
                self.irc_socket.send(f"NICK {self.nickname}\r\n".encode('utf-8'))

                time.sleep(1)

                self.irc_socket.send(b"CAP REQ :twitch.tv/tags twitch.tv/commands\r\n")
                self.irc_socket.send(f"JOIN #{self.channel}\r\n".encode('utf-8'))
                time.sleep(0.5)

                self.running = True
                self.shutdown_flag.clear()
                self.start_time = time.time()

                self.monitor_thread = threading.Thread(
                    target=self._monitor_loop,
                    daemon=True,
                    name=f"TwitchChat-{self.channel}"
                )
                self.monitor_thread.start()
                return True

            except Exception:
                self.running = False
                self._cleanup_resources()
                return False

    def _force_stop(self):
        """Force stop without acquiring locks"""
        self.running = False
        self.connected = False
        self.shutdown_flag.set()
        self._cleanup_resources()

    def stop(self):
        """Stop monitoring the Twitch chat"""
        with _initialization_lock:
            if not self.running:
                return

            self.shutdown_flag.set()
            self.running = False
            self.connected = False

            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=3.0)

            self._cleanup_resources()

    def _cleanup_resources(self):
        """Clean up resources"""
        if self.irc_socket:
            try:
                self.irc_socket.send(f"PART #{self.channel}\r\n".encode('utf-8'))
                time.sleep(0.1)
                self.irc_socket.close()
            except:
                pass
            self.irc_socket = None

    def _monitor_loop(self):
        """Main monitoring loop"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        buffer = ""

        initial_timeout = time.time() + 5
        while time.time() < initial_timeout and not self.shutdown_flag.is_set():
            try:
                self.irc_socket.settimeout(1.0)
                data = self.irc_socket.recv(2048).decode('utf-8', errors='ignore')
                if data:
                    buffer += data

                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)

                        if line.startswith("PING"):
                            pong_data = line.split(":", 1)[1] if ":" in line else ""
                            self.irc_socket.send(f"PONG :{pong_data}\r\n".encode('utf-8'))

                        if "001" in line or "JOIN" in line or "353" in line:
                            self.connected = True
                            break

                    if self.connected:
                        break
            except socket.timeout:
                continue
            except Exception:
                break

        if not self.connected:
            self.running = False
            return

        buffer = ""

        while not self.shutdown_flag.is_set() and self.running:
            try:
                if not self.irc_socket:
                    break

                self.irc_socket.settimeout(1.0)
                try:
                    data = self.irc_socket.recv(2048).decode('utf-8', errors='ignore')
                except socket.timeout:
                    continue

                if not data:
                    break

                buffer += data

                while '\r\n' in buffer:
                    line, buffer = buffer.split('\r\n', 1)

                    if not line.strip():
                        continue

                    parsed = self._parse_irc_message(line)

                    if parsed:
                        if parsed["type"] == "ping":
                            self.irc_socket.send(f"PONG :{parsed['data']}\r\n".encode('utf-8'))
                        elif parsed["type"] == "message":
                            msg = {
                                'author': parsed['author'],
                                'message': parsed['message'],
                                'timestamp': int(time.time() * 1000),
                                'datetime': datetime.now(),
                                'user_id': parsed['author']  # Use author as user_id
                            }

                            self.chat_buffer.append(msg)
                            if len(self.chat_buffer) > self.max_messages:
                                self.chat_buffer = self.chat_buffer[-self.max_messages:]

                            if self.message_callback:
                                try:
                                    self.message_callback(msg)
                                except Exception:
                                    pass

                consecutive_errors = 0

            except Exception:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    break
                time.sleep(min(2.0 ** consecutive_errors, 30.0))

        self.running = False
        self.connected = False

    def send_message(self, message: str) -> bool:
        """
        Send a message to Twitch chat (requires OAuth)
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self.enabled or not self.monitor:
            self.logger.warning("Cannot send message: Not connected")
            return False
        
        if not self.oauth_token:
            self.logger.warning("Cannot send message: No OAuth token (read-only mode)")
            return False
        
        success = self.monitor.send_message(message)
        
        if success:
            self.logger.system(f"[SUCCESS] Sent to chat: {message}")
        else:
            self.logger.error(f"[FAILED] Failed to send: {message}")
        
        return success

    def get_recent_messages(self, count: Optional[int] = None) -> str:
        """Get recent messages as formatted string (legacy compatibility)"""
        if not self.chat_buffer:
            return ""

        messages_to_use = self.chat_buffer[-(count or len(self.chat_buffer)):]
        formatted = ""
        for msg in messages_to_use:
            formatted += f"{msg['author']}: {msg['message']}\n"

        return formatted.strip()

    def __del__(self):
        if self.running:
            self._force_stop()


class TwitchIntegration:
    """
    Twitch chat integration with ChatHandler compatibility
    UPDATED: Removed ai_core dependency - uses callback-based routing instead
    """

    def __init__(
        self,
        channel: str,
        oauth_token: str = "",
        nickname: str = "",
        max_context_messages: int = 10,
        gui_logger: Optional[Callable] = None
    ):
        self.channel = channel
        self.oauth_token = oauth_token
        self.nickname = nickname
        self.max_context_messages = max_context_messages
        self.logger = Logger(name="Twitch Chat", gui_callback=gui_logger, config=config, enable_timestamps=True)
        self.monitor: Optional[TwitchChatMonitor] = None
        self.enabled = False
        self._message_callback = None  # For ChatHandler

    # ========================================================================
    # CHAT HANDLER COMPATIBILITY (REQUIRED)
    # ========================================================================

    def set_message_callback(self, callback: Callable):
        """
        Set callback for ChatHandler (REQUIRED)
        Callback signature: callback(message_dict)
        """
        self._message_callback = callback
        self.logger.system("[SUCCESS] Message callback registered")

    def _on_new_message(self, message: Dict):
        """
        Internal callback from monitor - forwards to ChatHandler
        
        Message format from monitor:
        {
            'author': str,
            'message': str,
            'timestamp': int (milliseconds),
            'datetime': datetime,
            'user_id': str
        }
        """
        if self._message_callback:
            # Pass through to ChatHandler which will:
            # 1. Normalize to ChatMessage
            # 2. Apply rate limiting
            # 3. Forward to AI Core's process_user_message
            self._message_callback(message)

    # ========================================================================
    # PLATFORM CONTROL
    # ========================================================================

    def start(self):
        """Start monitoring"""
        if self.monitor:
            self.stop()
            time.sleep(0.5)

        try:
            self.monitor = TwitchChatMonitor(
                channel=self.channel,
                max_messages=self.max_context_messages,
                message_callback=self._on_new_message,  # Internal callback
                oauth_token=self.oauth_token,
                nickname=self.nickname,
                gui_logger=None
            )

            success = self.monitor.start()
            self.enabled = success and self.monitor.running
            
            if self.enabled:
                mode = "authenticated" if self.oauth_token else "read-only"
                self.logger.system(f"[SUCCESS] Started monitoring #{self.channel} ({mode})")
            else:
                self.logger.error(f"[FAILED] Failed to start monitoring #{self.channel}")
            
            return self.enabled

        except Exception as e:
            self.logger.error(f"Error starting Twitch monitoring: {e}")
            self.monitor = None
            self.enabled = False
            return False

    def stop(self):
        """Stop monitoring"""
        if self.monitor:
            self.monitor.stop()
            self.logger.system(f"[SUCCESS] Stopped monitoring #{self.channel}")
            self.monitor = None
        self.enabled = False

    def get_context_for_ai(self) -> str:
        """
        Legacy method for backward compatibility
        Note: In centralized architecture, context is managed by ChatHandler
        """
        if not self.enabled or not self.monitor:
            return ""
        return self.monitor.get_recent_messages()

    def send_message(self, message: str) -> bool:
        """Send a message to Twitch chat (requires OAuth)"""
        if not self.enabled or not self.monitor:
            self.logger.warning("Cannot send message: Not connected")
            return False
        
        if not self.oauth_token:
            self.logger.warning("Cannot send message: No OAuth token (read-only mode)")
            return False
        
        success = self.monitor.send_message(message)
        
        if success:
            self.logger.system(f"[SUCCESS] Sent: {message}")
        else:
            self.logger.error(f"[FAILED] Failed to send: {message}")
        
        return success


def cleanup_all_instances():
    """Clean up all active instances"""
    for instance in list(_active_instances):
        try:
            if instance.running:
                instance._force_stop()
        except:
            pass

atexit.register(cleanup_all_instances)