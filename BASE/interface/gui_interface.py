# File: BASE/interface/gui_interface.py
"""
REFACTORED GUI: Uses centralized AI Core with new modular tool system
UPDATED: Removed hardcoded Coding panel - now uses modular component system
"""
import tkinter as tk
from tkinter import messagebox
import sys
import time
import queue
import threading
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from BASE.core.ai_core import AICore
    from BASE.core.config import Config
    from BASE.core.logger import Logger, MessageType
    from personality.bot_info import agentname
    import personality.controls as controls

    from BASE.interface.voice_manager import VoiceManager
    from BASE.interface.gui_components import ControlPanelManager
    from BASE.interface.gui_session_files_panel import SessionFilesPanel
    from BASE.interface.gui_message_processor import MessageProcessor
    from BASE.interface.gui_chat_handler import GUIMessageHandler
    from BASE.interface.gui_ui_builder import UIBuilder
    from BASE.interface.gui_chat_view import ChatView

except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running from the correct directory structure")
    sys.exit(1)

class OllamaGUI:
    def __init__(self, root):
        """
        Initialize GUI with VERIFIED singleton Config and Logger
        """
        self.root = root
        
        from personality.bot_info import agentname
        self.agentname = agentname
        
        import personality.controls as controls
        self.controls = controls
        
        self.root.title(f"{agentname} - Ollama Agent GUI")
        self.root.geometry("1600x1000")
        
        self.twitch_chat = None
        self.youtube_chat = None

        # Create singleton Config
        from BASE.core.config import Config
        self.config = Config()
        
        print(f"[Init] Created singleton Config: {id(self.config)}")

        # Create Logger with Config reference
        from BASE.core.logger import Logger
        
        self.logger = Logger(
            name="GUI",
            enable_timestamps=True,
            enable_console=False,
            gui_callback=self._gui_log_callback,
            config=self.config
        )
        
        # Verify logger has config reference
        if not hasattr(self.logger, 'config') or self.logger.config is None:
            raise RuntimeError("CRITICAL: Logger initialization failed - no config reference!")
        
        if id(self.logger.config) != id(self.config):
            raise RuntimeError(f"CRITICAL: Logger has DIFFERENT config instance!")
        
        print(f"[Init] Logger has correct config: {id(self.logger.config)}")

        # Create AI Core with same Config
        from BASE.core.ai_core import AICore
        
        self.ai_core = AICore(
            config=self.config,
            controls_module=controls,
            project_root=project_root,
            gui_logger=self._gui_log_callback
        )
        
        self._verify_config_chain()

        # Verify tool execution manager
        if not hasattr(self.ai_core, 'tool_manager'):
            self.logger.error("CRITICAL: AI Core missing tool_manager!")
            raise RuntimeError("Tool manager not initialized")

        self.logger.system(f"[SUCCESS] Tool manager initialized")
        enabled_tools = self.ai_core.tool_manager.get_enabled_tool_names()
        if enabled_tools:
            self.logger.system(f"Enabled tools: {', '.join(enabled_tools)}")
        else:
            self.logger.system("No tools currently enabled")

        # Setup external tools
        self._setup_tts_tool()
        # self._setup_integrations()

        # GUI-specific components
        import queue
        self.message_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.processing = False
        self.current_message = None
        self.speech_stop_flag = threading.Event()
        self.last_interaction = time.time()
        self.last_auto_prompt = time.time()

        # Voice manager
        from BASE.interface.voice_manager import VoiceManager
        self.voice_manager = VoiceManager(
            self.message_queue,
            self.input_queue,
            self.logger
        )

        # Control panel manager
        from BASE.interface.gui_components import ControlPanelManager
        self.control_panel_manager = ControlPanelManager(self.ai_core, self.logger)

        # Inject AI core into control manager
        if hasattr(self.ai_core, 'control_manager') and self.ai_core.control_manager:
            self.ai_core.control_manager.set_ai_core(self.ai_core)
            
            if hasattr(self.ai_core, 'tool_manager'):
                self.ai_core.control_manager.set_tool_manager(
                    self.ai_core.tool_manager
                )
                self.logger.system("[SUCCESS] Control manager connected to tool manager")
            
            self.logger.system("[SUCCESS] AI Core injected into ControlManager")
        else:
            self.logger.warning("[WARNING] Control manager not found")

        # Session files panel (no longer needs coding panel reference)
        from BASE.interface.gui_session_files_panel import SessionFilesPanel
        self.session_files_panel = SessionFilesPanel(
            self.root,
            self.ai_core,
            self.logger
        )

        # Message processor
        from BASE.interface.gui_message_processor import MessageProcessor
        self.message_processor = MessageProcessor(
            self.ai_core,
            self.message_queue,
            self.speech_stop_flag,
            self.logger
        )

        # Message handler
        from BASE.interface.gui_chat_handler import GUIMessageHandler
        self.chat_handler = GUIMessageHandler(
            ai_core=self.ai_core,
            message_processor=self.message_processor,
            message_queue=self.message_queue,
            logger=self.logger
        )

        # UI components
        from BASE.interface.gui_ui_builder import UIBuilder
        self.ui_builder = UIBuilder(self)
        self.send_button = None
        self.processing_label = None
        self.system_log = None

        # Setup external tools
        self._setup_tts_tool()  # This will now initialize even if disabled
        # self._setup_integrations()

        # Apply theme and setup GUI
        # Note: Theme manager is now initialized in UIBuilder
        self.ui_builder.setup_gui()

        # Start queue processor
        self.start_queue_processor()

        self.logger.system("GUI initialized successfully")
        self.logger.system("INITIALIZATION SUMMARY")
        self._print_config_summary()

    def _verify_config_chain(self):
        """Verify all components share the same config instance"""
        print("CONFIG CHAIN VERIFICATION")
        
        base_id = id(self.config)
        all_match = True
        
        checks = {
            'Main Config': self.config,
            'Logger Config': self.logger.config if hasattr(self.logger, 'config') else None,
            'AICore Config': self.ai_core.config if hasattr(self.ai_core, 'config') else None,
            'ControlManager Config': (
                self.ai_core.control_manager.config 
                if hasattr(self.ai_core, 'control_manager') and 
                hasattr(self.ai_core.control_manager, 'config')
                else None
            ),
        }
        
        print(f"\nBase Config ID: {base_id}")
        print("\nComponent Verification:")
        
        for name, cfg in checks.items():
            if cfg is None:
                print(f"  [FAILED] {name}: NO CONFIG REFERENCE")
                all_match = False
            elif id(cfg) != base_id:
                print(f"  [FAILED] {name}: DIFFERENT instance ({id(cfg)})")
                all_match = False
            else:
                print(f"  {name}: Correct ({id(cfg)})")
        
        if all_match:
            print("[SUCCESS] SUCCESS: All components share same config instance")
            self.logger.system("[Config Check] All components verified")
        else:
            print("[FAILED] FAILURE: Config instances don't match!")
            raise RuntimeError("Config chain verification failed")

    def _print_config_summary(self):
        """Print initialization summary with config state"""
        print(f"Config Instance: {id(self.config)}")
        print(f"Logger Instance: {id(self.logger)}")
        print(f"Logger Config: {id(self.logger.config) if hasattr(self.logger, 'config') else 'NONE'}")
        
        logging_controls = [
            'LOG_TOOL_EXECUTION',
            'LOG_PROMPT_CONSTRUCTION', 
            'LOG_RESPONSE_PROCESSING',
            'SHOW_CHAT'
        ]
        
        print("\nLogging Controls:")
        for control in logging_controls:
            value = getattr(self.config, control, None)
            status = "[SUCCESS] ON" if value else "[FAILED] OFF"
            print(f"  {control}: {status}")

    def test_logging_controls(self):
        """Test that logging controls update immediately"""
        self.logger.system("TESTING LIVE LOGGING CONTROLS")
        
        initial = self.config.LOG_TOOL_EXECUTION
        self.logger.system(f"Initial LOG_TOOL_EXECUTION: {initial}")
        
        self.logger.tool("Test message 1 - should appear if enabled")
        
        self.logger.system("Toggling LOG_TOOL_EXECUTION...")
        self.ai_core.control_manager.toggle_feature('LOG_TOOL_EXECUTION')
        
        new_value = self.config.LOG_TOOL_EXECUTION
        logger_value = self.logger.config.LOG_TOOL_EXECUTION
        
        self.logger.system(f"After toggle:")
        self.logger.system(f"  Config value: {new_value}")
        self.logger.system(f"  Logger sees: {logger_value}")
        
        if new_value == (not initial) and logger_value == (not initial):
            self.logger.system("[SUCCESS] Toggle successful - logger sees new value immediately")
        else:
            self.logger.error("[FAILED] Toggle failed - stale config reference!")
            return False
        
        self.logger.tool("Test message 2 - should NOT appear if disabled")
        
        self.logger.system("Toggling back to original state...")
        self.ai_core.control_manager.toggle_feature('LOG_TOOL_EXECUTION')
        
        final = self.config.LOG_TOOL_EXECUTION
        if final == initial:
            self.logger.system(f"[SUCCESS] Restored to initial state: {initial}")
        else:
            self.logger.error("[FAILED] Failed to restore initial state!")
            return False
        
        self.logger.tool("Test message 3 - should match initial state")
        
        self.logger.system("[SUCCESS] LOGGING CONTROLS TEST PASSED")
        return True

    def _config_get(self, key: str, default=None):
        """Robust getter for Config keys"""
        try:
            if hasattr(self.config, "get") and callable(getattr(self.config, "get")):
                return self.config.get(key, default)
        except Exception:
            pass

        try:
            if hasattr(self.config, key):
                return getattr(self.config, key)
        except Exception:
            pass

        try:
            return self.config[key]
        except Exception:
            pass

        try:
            return getattr(self.config, key, default)
        except Exception:
            return default

    def _setup_tts_tool(self):
        """
        Setup TTS tool - FIXED to initialize even when disabled
        This allows runtime toggling without restart
        """
        try:
            from personality.bot_info import agentname
            from BASE.tools.internal.voice.tts_tool import TTSTool
            
            # CRITICAL FIX: Always initialize backends, just don't use them if disabled
            # This allows runtime toggling without restart
            
            use_custom = getattr(controls, 'USE_CUSTOM_VOICE', False)
            
            backend = None
            backend_type = None
            
            # Try to initialize the appropriate backend
            if use_custom:
                self.logger.speech("[VOICE] Attempting XTTS custom voice cloning")
                
                try:
                    import torch
                    self.logger.speech(f"[SUCCESS] PyTorch detected: {torch.__version__}")
                    if torch.cuda.is_available():
                        self.logger.speech(f"[SUCCESS] CUDA available: {torch.cuda.get_device_name(0)}")
                    
                    from BASE.tools.internal.voice.xtts_backend import XTTSBackend
                    
                    voice_path = f"./personality/voice/{agentname}_voice_sample.wav"
                    
                    if not Path(voice_path).exists():
                        raise FileNotFoundError(f"Voice sample not found: {voice_path}")
                    
                    backend = XTTSBackend(
                        voice_sample_path=voice_path,
                        language='en',
                        speed=1.0,
                        controls_module=controls,
                        precompute_embeddings=True  # Precompute for faster first use
                    )
                    
                    if not backend.is_available():
                        raise RuntimeError("XTTS backend initialization failed")
                    
                    backend_type = "XTTS"
                    self.logger.speech(f"[SUCCESS] XTTS backend initialized successfully")
                
                except Exception as e:
                    self.logger.error(f"XTTS initialization failed: {e}")
                    import traceback
                    traceback.print_exc()
                    self.logger.speech("[WARNING] Falling back to system voice (pyttsx3)")
                    backend = None
                    backend_type = None
                    setattr(controls, 'USE_CUSTOM_VOICE', False)
            
            # CRITICAL FIX: Always try to create system voice backend as fallback
            if backend is None:
                self.logger.speech("[SOUND] Initializing system voice (pyttsx3)")
                
                from BASE.tools.internal.voice.pyttsx3_backend import Pyttsx3Backend
                
                backend = Pyttsx3Backend(controls_module=controls)
                backend_type = "pyttsx3"
                
                if backend.is_available():
                    volume = getattr(controls, 'VOICE_VOLUME', 1.0)
                    self.logger.speech(f"[SUCCESS] pyttsx3 created with volume: {int(volume * 100)}%")
                else:
                    self.logger.error("[FAILED] pyttsx3 backend not available")
                    self.tts_tool = None
                    return
            
            # Create TTS tool
            tts_tool = TTSTool(backend, self.logger)
            
            # Inject into AI Core
            self.ai_core.setup_tts_tool(tts_tool)
            
            # Store reference
            self.tts_tool = tts_tool
            
            # Log status based on whether speech is enabled
            if controls.AVATAR_SPEECH:
                if tts_tool.is_available():
                    info = tts_tool.get_voice_info()
                    volume = getattr(controls, 'VOICE_VOLUME', 1.0)
                    self.logger.speech(
                        f"[SUCCESS] TTS ready: {info.get('name', 'Unknown')} "
                        f"({info.get('type', 'Unknown')}) - Volume: {int(volume * 100)}%"
                    )
                    
                    if backend_type == "XTTS" and info.get('device'):
                        self.logger.speech(f"  Device: {info['device']}")
                else:
                    self.logger.error("[FAILED] TTS not available after initialization")
                    self.tts_tool = None
            else:
                # TTS initialized but disabled
                self.logger.speech("[INFO] TTS initialized but disabled (toggle AVATAR_SPEECH to enable)")
        
        except Exception as e:
            self.logger.error(f"Critical TTS setup failure: {e}")
            import traceback
            traceback.print_exc()
            self.tts_tool = None

    def _gui_log_callback(self, message: str, msg_type: str, color: str):
        """Callback for logger to send messages to GUI with color information"""
        if not hasattr(self, 'system_log') or not self.system_log:
            if not hasattr(self, '_pending_log_messages'):
                self._pending_log_messages = []
            self._pending_log_messages.append((message, msg_type, color))
            return
        
        from datetime import datetime
        
        self.system_log.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = msg_type.upper()
        
        formatted_message = f"[{timestamp}] [{prefix}] {message}\n"
        self.system_log.insert(tk.END, formatted_message, msg_type)
        
        self.system_log.tag_configure(msg_type, foreground=color)
        
        self.system_log.config(state=tk.DISABLED)
        self.system_log.yview(tk.END)

    def flush_pending_log_messages(self):
        """Flush any messages that were logged before GUI was ready"""
        if hasattr(self, '_pending_log_messages'):
            for message, msg_type, color in self._pending_log_messages:
                self._gui_log_callback(message, msg_type, color)
            del self._pending_log_messages

    # def _setup_integrations(self):
        # """Initialize optional integrations - LEGACY (passive context)"""
        # from BASE.tools.internal.chat.twitch_chat_direct import TwitchIntegration
        # from BASE.tools.internal.chat.youtube_chat_direct import YouTubeIntegration

        # twitch_channel = self._config_get("TWITCH_CHANNEL")
        # twitch_token = self._config_get("TWITCH_OAUTH_TOKEN")
        # twitch_nick = self._config_get("agentname", getattr(self, 'agentname', None)) or getattr(self.config, 'agentname', None) or getattr(self, 'agentname', agentname)

        # if twitch_channel and twitch_token:
        #     try:
        #         self.twitch_chat = TwitchIntegration(
        #             channel=twitch_channel,
        #             oauth_token=twitch_token,
        #             nickname=twitch_nick,
        #             max_context_messages=10,
        #             gui_logger=self._gui_log_callback,
        #             ai_core=self.ai_core
        #         )
        #         self.logger.system("Twitch Integration Initialized")
        #     except Exception as e:
        #         self.logger.error(f"Failed initializing Twitch integration: {e}")

        # youtube_video_id = self._config_get("YOUTUBE_VIDEO_ID")
        # if youtube_video_id:
        #     try:
        #         self.youtube_chat = YouTubeIntegration(
        #             video_id=youtube_video_id,
        #             max_context_messages=10,
        #             ai_core=self.ai_core
        #         )
        #         self.logger.system("YouTube Integration Initialized")
        #     except Exception as e:
        #         self.logger.error(f"Failed initializing YouTube integration: {e}")

    # def _initialize_discord(self):
    #     """Initialize Discord integration"""
    #     try:
    #         if hasattr(self.ai_core, 'discord_integration') and self.ai_core.discord_integration:
    #             self.logger.discord("Discord already initialized in AI Core")
    #             return
            
    #         if not self.config.discord_enabled:
    #             self.logger.discord("Enabling Discord for initialization")
    #             self.config.discord_enabled = True
            
    #         self.ai_core._init_discord()
            
    #         if not hasattr(self.ai_core, 'discord_integration') or not self.ai_core.discord_integration:
    #             raise Exception("Discord integration not created by AI Core")
            
    #         if hasattr(self.ai_core, 'chat_handler') and self.ai_core.chat_handler:
    #             success = self.ai_core.chat_handler.register_platform(
    #                 platform_name="Discord",
    #                 integration_instance=self.ai_core.discord_integration,
    #                 auto_start=False
    #             )
    #             if success:
    #                 self.logger.discord("Discord registered with chat handler")
    #             else:
    #                 self.logger.error("Failed to register Discord with chat handler")
    #         else:
    #             self.logger.warning("Chat handler not available")
            
    #         self.logger.discord("Discord initialization complete")
            
    #     except Exception as e:
    #         self.logger.error(f"Failed to initialize Discord: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         raise

    def handle_autonomous_response(self, response: str):
        """Handle autonomous responses from cognitive loop"""
        if not response or not response.strip():
            return
        
        try:
            self.message_queue.put(("bot", self.agentname, response))
            
            import personality.controls as controls
            if controls.AVATAR_SPEECH and len(response) < 1000:
                self.message_processor._play_tts(response)
                
                if self.controls.LOG_RESPONSE_PROCESSING:
                    self.logger.system(f"[Autonomous] Speaking: {response[:50]}...")
            else:
                if self.controls.LOG_RESPONSE_PROCESSING:
                    self.logger.system(f"[Autonomous] Queued (no TTS): {response[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error handling autonomous response: {e}")
            import traceback
            traceback.print_exc()
        
    def start_queue_processor(self):
        self.process_queues()

    def process_queues(self):
        """Process message and input queues"""
        try:
            current_time = time.time()
            auto_prompt_interval = getattr(controls, 'AUTO_RESPOND_INTERVAL', 60)
            time_since_last_interaction = current_time - self.last_interaction
            time_since_last_auto_prompt = current_time - self.last_auto_prompt

            should_auto_prompt = (
                controls.AUTO_RESPOND and
                time_since_last_interaction >= auto_prompt_interval and
                time_since_last_auto_prompt >= auto_prompt_interval and
                not self.processing and
                self.input_queue.empty()
            )

            if should_auto_prompt:
                self.logger.system(f"Triggering auto-prompt ({auto_prompt_interval}s of inactivity)")
                self.input_queue.put("__AUTO_PROMPT__")
                self.last_auto_prompt = current_time

            while not self.message_queue.empty():
                try:
                    msg_type, sender, message = self.message_queue.get_nowait()

                    if msg_type == "processing_complete":
                        self.processing = False
                        if self.send_button:
                            self.send_button.config(state=tk.NORMAL)
                        if self.processing_label:
                            self.processing_label.config(text="")
                        self.current_message = None
                    elif msg_type == "voice_input":
                        ChatView.add_chat_message(self, sender, message, MessageType.SPEECH)
                    else:
                        if isinstance(msg_type, str):
                            msg_type = ChatView._convert_legacy_type(msg_type)
                        ChatView.add_chat_message(self, sender, message, msg_type)

                except queue.Empty:
                    break

            if not self.processing and not self.input_queue.empty():
                combined = []
                while not self.input_queue.empty():
                    combined.append(self.input_queue.get())
                combined_message = " ".join(combined).strip()

                is_auto_prompt = combined_message == "__AUTO_PROMPT__"

                if is_auto_prompt:
                    self.logger.system("🕐 Auto-prompt detected - checking for proactive response")
                    process_message = ""
                else:
                    if not combined_message:
                        self.logger.warning("Skipping empty user input")
                        return
                    process_message = combined_message
                    self.last_interaction = current_time

                self.current_message = process_message
                self.processing = True
                if self.send_button:
                    self.send_button.config(state=tk.DISABLED)
                if self.processing_label:
                    if is_auto_prompt:
                        self.processing_label.config(text="Checking...")
                    else:
                        self.processing_label.config(text="Processing...")

                threading.Thread(
                    target=self._process_message_with_handler,
                    args=(process_message, is_auto_prompt),
                    daemon=True
                ).start()

        except Exception as e:
            self.logger.error(f"Error processing queues: {e}")

        self.root.after(100, self.process_queues)

    def _process_message_with_handler(self, message: str, is_auto_prompt: bool):
        """Process message through chat_handler"""
        try:
            self.chat_handler.handle_user_message(message, is_auto_prompt=is_auto_prompt)
        except Exception as e:
            self.logger.error(f"Error in message handler: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if is_auto_prompt:
                self.logger.system("Auto-prompt check complete")

    def setup_chat_with_history(self):
        """Setup chat interface with loaded conversation history"""
        try:
            self.ai_core.start_integrations()
        except Exception as e:
            self.logger.error(f"Error starting integrations: {e}")

        try:
            self.chat_handler.load_conversation_history(messages_to_load=400)
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")

        callback_registered = False
        if hasattr(self.ai_core, 'processing_delegator'):
            if hasattr(self.ai_core.processing_delegator, 'thought_processor'):
                thought_processor = self.ai_core.processing_delegator.thought_processor
                
                import time
                for _ in range(10):
                    if hasattr(thought_processor, 'cognitive_loop') and thought_processor.cognitive_loop:
                        thought_processor.cognitive_loop.autonomous_response_callback = self.handle_autonomous_response
                        self.logger.system("Autonomous response callback registered")
                        callback_registered = True
                        break
                    time.sleep(0.1)
                
                if not callback_registered:
                    self.logger.system("Cognitive loop not ready - autonomous responses disabled")

        try:
            memory_manager = self.ai_core.get_memory_manager()
            stats = memory_manager.get_stats()

            summary_msg = f"Memory Status - Short: {stats['short_memory_entries']}, "
            summary_msg += f"Medium: {stats['medium_memory_entries']}, "
            summary_msg += f"Long: {stats['long_memory_summaries']}, "
            summary_msg += f"Base: {stats['base_knowledge_chunks']}"

            self.logger.memory(summary_msg)

            if stats['long_memory_summaries'] > 0:
                self.logger.memory(f"You have {stats['long_memory_summaries']} past day summaries available for context")

        except Exception as e:
            self.logger.error(f"Error checking memory stats: {e}")

    def on_closing(self):
        try:
            self.voice_manager.stop_voice_input()

            if hasattr(self, 'tts_tool') and self.tts_tool:
                self.tts_tool.stop()

            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.ai_core.shutdown()
                self.root.destroy()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.root.destroy()


def main():
    try:
        root = tk.Tk()
        app = OllamaGUI(root)
        app.setup_chat_with_history()
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()