# ============================================================================
# BASE/tools/chat/youtube_chat_direct.py
# ============================================================================
"""
YouTube Chat Integration - Based on working legacy version
Updated for ChatHandler compatibility
"""
import time
import threading
import requests
from datetime import datetime
from typing import Optional, Callable, List, Dict
import atexit
import weakref
import re

from BASE.core.logger import Logger, MessageType

YOUTUBE_AVAILABLE = True
_active_instances = weakref.WeakSet()
_initialization_lock = threading.Lock()


class YouTubeChatMonitor:
    """Monitor YouTube live chat using direct API calls"""

    def __init__(self, video_id: str, max_messages: int = 10, message_callback: Optional[Callable] = None,
                 gui_logger: Optional[Callable[..., None]] = None):
        self.video_id = video_id
        self.max_messages = max_messages
        self.message_callback = message_callback

        self.chat_buffer: List[Dict] = []
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        self.shutdown_flag = threading.Event()
        self.start_time = None

        # Use simple print if no GUI logger provided
        self.gui_logger = gui_logger
        if gui_logger:
            self.logger = Logger(
                name="YouTube Monitor",
                enable_timestamps=True,
                enable_console=False,
                gui_callback=gui_logger,
                config=config
            )
        else:
            self.logger = None

        self.live_chat_id = None
        self.next_page_token = None
        self.polling_interval = 2.0
        self.session = None

        _active_instances.add(self)

    def _log(self, message: str, level: str = "system"):
        """Unified logging"""
        if self.logger:
            if level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
            else:
                self.logger.system(message)
        else:
            print(f"[YouTube Chat] {message}")

    def _extract_live_chat_id(self) -> Optional[str]:
        """Extract live chat ID from video page"""
        try:
            url = f"https://www.youtube.com/watch?v={self.video_id}"
            self._log(f"Fetching video page for {self.video_id}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Look for liveChatRenderer in the page HTML
            patterns = [
                r'"liveChatRenderer":\{"continuations":\[\{"reloadContinuationData":\{"continuation":"([^"]+)"',
                r'"conversationBar":\{"liveChatRenderer":\{"continuations":\[\{"reloadContinuationData":\{"continuation":"([^"]+)"',
                r'continuation":"([A-Za-z0-9_-]{100,})"'
            ]

            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    continuation = match.group(1)
                    self._log("[SUCCESS] Found live chat continuation token")
                    return continuation

            self._log("[FAILED] Could not find live chat - stream may not be live or chat disabled", "error")
            return None

        except Exception as e:
            self._log(f"Error extracting chat ID: {e}", "error")
            return None

    def _fetch_chat_messages(self) -> List[Dict]:
        """Fetch chat messages using continuation token"""
        if not self.live_chat_id:
            return []

        try:
            url = "https://www.youtube.com/youtubei/v1/live_chat/get_live_chat"

            # YouTube's internal API payload
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20231201.00.00"
                    }
                },
                "continuation": self.live_chat_id
            }

            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract messages and next continuation
            messages = []

            # Navigate the response structure
            continuation_contents = data.get("continuationContents", {})
            live_chat_continuation = continuation_contents.get("liveChatContinuation", {})

            # Get actions (messages)
            actions = live_chat_continuation.get("actions", [])
            for action in actions:
                item = action.get("addChatItemAction", {}).get("item", {})

                # Handle text messages
                text_message = item.get("liveChatTextMessageRenderer", {})
                if text_message:
                    author = text_message.get("authorName", {}).get("simpleText", "Unknown")
                    message_parts = text_message.get("message", {}).get("runs", [])
                    message_text = "".join(part.get("text", "") for part in message_parts)
                    timestamp_usec = text_message.get("timestampUsec", str(int(time.time() * 1000000)))
                    timestamp = int(timestamp_usec) // 1000  # milliseconds
                    author_id = text_message.get("authorExternalChannelId", author)

                    messages.append({
                        'author': author,
                        'message': message_text,
                        'timestamp': timestamp,
                        'datetime': datetime.fromtimestamp(timestamp / 1000),
                        'user_id': author_id
                    })

            # Get next continuation token
            continuations = live_chat_continuation.get("continuations", [])
            if continuations:
                for cont in continuations:
                    if "invalidationContinuationData" in cont:
                        self.live_chat_id = cont["invalidationContinuationData"]["continuation"]
                        timeout_ms = cont["invalidationContinuationData"].get("timeoutDurationMillis", 2000)
                        self.polling_interval = max(timeout_ms / 1000, 1.0)
                        break
                    elif "timedContinuationData" in cont:
                        self.live_chat_id = cont["timedContinuationData"]["continuation"]
                        timeout_ms = cont["timedContinuationData"].get("timeoutDurationMillis", 2000)
                        self.polling_interval = max(timeout_ms / 1000, 1.0)
                        break

            return messages

        except requests.exceptions.RequestException:
            # Don't spam logs with connection errors
            return []
        except Exception as e:
            self._log(f"Error parsing messages: {e}", "error")
            return []

    def start(self):
        """Start monitoring the live chat"""
        with _initialization_lock:
            if self.running:
                self._log("Already running")
                return True

            # Stop other instances
            for instance in list(_active_instances):
                if instance is not self and instance.running:
                    try:
                        instance._force_stop()
                    except:
                        pass

            try:
                self._log(f"Initializing for video: {self.video_id}")

                # Create session with proper headers
                self.session = requests.Session()
                self.session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                })

                # Extract chat ID
                self.live_chat_id = self._extract_live_chat_id()
                if not self.live_chat_id:
                    self._log("Failed to get live chat ID", "error")
                    return False

                self.running = True
                self.shutdown_flag.clear()
                self.start_time = time.time()

                self.monitor_thread = threading.Thread(
                    target=self._monitor_loop,
                    daemon=True,
                    name=f"YouTubeChat-{self.video_id}"
                )
                self.monitor_thread.start()
                self._log(f"[SUCCESS] Started monitoring (poll interval: {self.polling_interval}s)")
                return True

            except Exception as e:
                self._log(f"Failed to start: {e}", "error")
                self.running = False
                self._cleanup_resources()
                return False

    def _force_stop(self):
        """Force stop without acquiring locks"""
        self.running = False
        self.shutdown_flag.set()
        self._cleanup_resources()

    def stop(self):
        """Stop monitoring the live chat"""
        with _initialization_lock:
            if not self.running:
                return

            self._log("Stopping monitoring...")
            self.shutdown_flag.set()
            self.running = False

            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=3.0)

            self._cleanup_resources()
            self._log("[SUCCESS] Stopped")

    def _cleanup_resources(self):
        """Clean up resources"""
        if self.session:
            try:
                self.session.close()
            except:
                pass
            self.session = None

    def _monitor_loop(self):
        """Main monitoring loop"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        message_count = 0
        first_message_logged = False

        self._log("Monitor loop started, waiting for messages...")

        while not self.shutdown_flag.is_set():
            try:
                if not self.live_chat_id:
                    self._log("No chat ID, exiting", "error")
                    break

                # Fetch new messages
                messages = self._fetch_chat_messages()

                if messages:
                    for msg in messages:
                        message_count += 1
                        
                        # Add to buffer
                        self.chat_buffer.append(msg)
                        if len(self.chat_buffer) > self.max_messages:
                            self.chat_buffer = self.chat_buffer[-self.max_messages:]

                        # Log first message as confirmation
                        if not first_message_logged:
                            self._log(f"[SUCCESS] Receiving messages: {msg['author']}: {msg['message'][:50]}...")
                            first_message_logged = True

                        # Call callback (forward to ChatHandler)
                        if self.message_callback:
                            try:
                                self.message_callback(msg)
                            except Exception as cb_error:
                                self._log(f"Callback error: {cb_error}", "error")

                    consecutive_errors = 0

                # Wait before next poll
                time.sleep(self.polling_interval)

            except Exception as e:
                consecutive_errors += 1
                self._log(f"Error ({consecutive_errors}/{max_consecutive_errors}): {e}", "error")

                if consecutive_errors >= max_consecutive_errors:
                    self._log("Too many errors, stopping", "error")
                    break

                time.sleep(min(2.0 ** consecutive_errors, 30.0))

        self.running = False
        self._log(f"Monitor loop ended ({message_count} messages processed)")

    def get_recent_messages(self, count: Optional[int] = None) -> str:
        """Get recent messages as formatted string"""
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


class YouTubeIntegration:
    """
    YouTube chat integration with ChatHandler compatibility
    """

    def __init__(
        self,
        video_id: str,
        max_context_messages: int = 10,
        gui_logger: Optional[Callable] = None
    ):
        self.video_id = video_id
        self.max_context_messages = max_context_messages
        self.gui_logger = gui_logger
        
        if gui_logger:
            self.logger = Logger(name="YouTube Chat", gui_callback=gui_logger, config=config, enable_timestamps=True)
        else:
            self.logger = None
            
        self.monitor: Optional[YouTubeChatMonitor] = None
        self.enabled = False
        self._message_callback = None  # For ChatHandler
        self._last_start_attempt = 0.0

    def _log(self, message: str, level: str = "system"):
        """Unified logging"""
        if self.logger:
            if level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
            else:
                self.logger.system(message)
        else:
            print(f"[YouTube Chat] {message}")

    # ========================================================================
    # CHAT HANDLER COMPATIBILITY (REQUIRED)
    # ========================================================================

    def set_message_callback(self, callback: Callable):
        """Set callback for ChatHandler (REQUIRED)"""
        self._message_callback = callback
        self._log("[SUCCESS] Message callback registered")

    def _on_new_message(self, message: Dict):
        """Internal callback from monitor - forwards to ChatHandler"""
        if self._message_callback:
            try:
                self._message_callback(message)
            except Exception as e:
                self._log(f"Error forwarding message: {e}", "error")

    # ========================================================================
    # PLATFORM CONTROL
    # ========================================================================

    def start(self):
        """Start monitoring"""
        current_time = time.time()

        # Rate limit start attempts
        if current_time - self._last_start_attempt < 3.0:
            self._log("Too soon since last start attempt", "warning")
            return False

        self._last_start_attempt = current_time

        if self.monitor:
            self.stop()
            time.sleep(0.5)

        try:
            self._log(f"Starting monitor for video: {self.video_id}")

            self.monitor = YouTubeChatMonitor(
                video_id=self.video_id,
                max_messages=self.max_context_messages,
                message_callback=self._on_new_message,
                gui_logger=self.gui_logger
            )

            success = self.monitor.start()
            self.enabled = success and self.monitor.running

            if self.enabled:
                self._log("[SUCCESS] Monitoring started successfully")
            else:
                self._log("[FAILED] Failed to start monitoring", "error")

            return self.enabled

        except Exception as e:
            self._log(f"Error starting: {e}", "error")
            import traceback
            traceback.print_exc()
            self.monitor = None
            self.enabled = False
            return False

    def stop(self):
        """Stop monitoring"""
        if self.monitor:
            self.monitor.stop()
            self._log("[SUCCESS] Stopped monitoring")
            self.monitor = None
        self.enabled = False

    def get_context_for_ai(self) -> str:
        """Legacy method for backward compatibility"""
        if not self.enabled or not self.monitor:
            return ""
        return self.monitor.get_recent_messages()


def cleanup_all_instances():
    """Clean up all active instances"""
    for instance in list(_active_instances):
        try:
            if instance.running:
                instance._force_stop()
        except:
            pass

atexit.register(cleanup_all_instances)