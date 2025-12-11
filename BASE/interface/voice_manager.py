"""
Voice input management component with volume controls.
Fixed to use GPU-accelerated voice recognition
Location: BASE/interface/voice_manager.py
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import json
import sounddevice as sd
import numpy as np
import sys
from pathlib import Path

# Path setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from BASE.interface.gui_themes import DarkTheme

# Import GPU-accelerated voice module
try:
    from BASE.tools.internal.voice.voice_to_text import init_audio, start_vosk_stream
    GPU_VOICE_AVAILABLE = True
except ImportError:
    GPU_VOICE_AVAILABLE = False
    print("[Voice] GPU voice module not found, using legacy")

try:
    from personality.bot_info import agentname, username
except ImportError:
    agentname = "Anna"
    username = "User"


class VoiceManager:
    """Manages GPU-accelerated voice input and volume controls"""

    def __init__(self, message_queue, input_queue, logger):
        """Initialize voice manager"""
        self.message_queue = message_queue
        self.input_queue = input_queue
        self.logger = logger

        self.voice_enabled = False
        self.audio_started = False
        
        # GPU voice recognition components
        self.recognition_backend = None
        self.recognition_device = None
        self.whisper_model = None
        self.vosk_model = None
        self.stream = None
        self.raw_queue = None
        self.text_queue = None
        
        # Voice thread
        self.voice_thread = None
        self.voice_worker_thread = None

        # GUI components
        self.voice_button = None
        self.voice_status = None
        self.voice_volume_slider = None
        self.voice_volume_label = None
        self.sound_volume_slider = None
        self.sound_volume_label = None

    def create_voice_panel(self, parent_frame):
        """Create voice control panel with volume controls"""
        voice_frame = ttk.LabelFrame(
            parent_frame, text="Voice & Audio Control", style="Dark.TLabelframe"
        )
        voice_frame.pack(fill=tk.X, pady=(0, 5))

        # Voice Input Controls
        voice_controls = ttk.Frame(voice_frame)
        voice_controls.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.voice_button = ttk.Button(
            voice_controls,
            text="Start Voice Input",
            command=self.toggle_voice_input,
            width=20,
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 10))

        self.voice_status = tk.Label(
            voice_controls,
            text="Voice: Disabled",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
        )
        self.voice_status.pack(side=tk.LEFT)
        
        # Volume Controls
        self._create_volume_controls(voice_frame)

    def _create_volume_controls(self, parent_frame):
        """Create volume slider controls"""
        import personality.controls as controls
        
        volume_container = ttk.Frame(parent_frame)
        volume_container.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        # TTS Voice Volume
        voice_vol_frame = ttk.Frame(volume_container)
        voice_vol_frame.pack(fill=tk.X, pady=(0, 8))
        
        voice_label_frame = ttk.Frame(voice_vol_frame)
        voice_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        voice_icon = tk.Label(
            voice_label_frame,
            text="",
            font=("Segoe UI", 12),
            background=DarkTheme.BG_DARKER,
            width=2
        )
        voice_icon.pack(side=tk.LEFT)
        
        voice_text = tk.Label(
            voice_label_frame,
            text="Voice",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=8,
            anchor="w"
        )
        voice_text.pack(side=tk.LEFT, padx=(5, 0))
        
        voice_slider_frame = ttk.Frame(voice_vol_frame)
        voice_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_slider = tk.Scale(
            voice_slider_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_voice_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_PURPLE,
            highlightthickness=0,
            showvalue=0,
            length=150
        )
        self.voice_volume_slider.set(int(controls.VOICE_VOLUME * 100))
        self.voice_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_label = tk.Label(
            voice_slider_frame,
            text=f"{int(controls.VOICE_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.voice_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Sound Effects Volume
        sound_vol_frame = ttk.Frame(volume_container)
        sound_vol_frame.pack(fill=tk.X)
        
        sound_label_frame = ttk.Frame(sound_vol_frame)
        sound_label_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        sound_icon = tk.Label(
            sound_label_frame,
            text="",
            font=("Segoe UI", 12),
            background=DarkTheme.BG_DARKER,
            width=2
        )
        sound_icon.pack(side=tk.LEFT)
        
        sound_text = tk.Label(
            sound_label_frame,
            text="Sounds",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=8,
            anchor="w"
        )
        sound_text.pack(side=tk.LEFT, padx=(5, 0))
        
        sound_slider_frame = ttk.Frame(sound_vol_frame)
        sound_slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_slider = tk.Scale(
            sound_slider_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_sound_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_BLUE,
            highlightthickness=0,
            showvalue=0,
            length=150
        )
        self.sound_volume_slider.set(int(controls.SOUND_EFFECT_VOLUME * 100))
        self.sound_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_label = tk.Label(
            sound_slider_frame,
            text=f"{int(controls.SOUND_EFFECT_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_BLUE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.sound_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        hint_label = tk.Label(
            volume_container,
            text="Volumes apply immediately to all audio output",
            font=("Segoe UI", 8, "italic"),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER
        )
        hint_label.pack(pady=(5, 0))
    
    def _on_voice_volume_change(self, value):
        """Handle TTS voice volume slider change"""
        import personality.controls as controls
        volume = int(value) / 100.0
        controls.VOICE_VOLUME = volume
        if self.voice_volume_label:
            self.voice_volume_label.config(text=f"{int(value)}%")
        self.logger.speech(f"Voice volume: {int(value)}%")
    
    def _on_sound_volume_change(self, value):
        """Handle sound effects volume slider change"""
        import personality.controls as controls
        volume = int(value) / 100.0
        controls.SOUND_EFFECT_VOLUME = volume
        if self.sound_volume_label:
            self.sound_volume_label.config(text=f"{int(value)}%")
        self.logger.system(f"Sound effects volume: {int(value)}%")

    def toggle_voice_input(self):
        """Toggle GPU-accelerated voice input on/off"""
        if not self.voice_enabled:
            try:
                self.logger.system("Initializing GPU voice input...")
                
                if not GPU_VOICE_AVAILABLE:
                    self.logger.error("GPU voice module not available")
                    return
                
                # Initialize GPU voice recognition
                import queue
                self.raw_queue = queue.Queue(maxsize=50)
                self.text_queue = queue.Queue(maxsize=20)
                
                # Initialize audio system (tries GPU, falls back to CPU)
                init_audio(self)
                
                # Log backend
                backend_name = f"{self.recognition_backend.upper()} on {self.recognition_device.upper()}"
                self.logger.success(f"Voice backend: {backend_name}")
                
                self.voice_enabled = True
                if self.voice_button:
                    self.voice_button.config(text="Stop Voice Input")
                if self.voice_status:
                    self.voice_status.config(
                        text=f"Voice: {backend_name}", 
                        foreground=DarkTheme.ACCENT_GREEN
                    )

                # Start recognition stream
                start_vosk_stream(self)
                
                # Start text processing thread
                self.voice_thread = threading.Thread(
                    target=self.voice_processing_loop, daemon=True
                )
                self.voice_thread.start()
                
                self.logger.success("Voice input started successfully")

            except Exception as e:
                self.logger.error(f"Voice initialization error: {str(e)}")
                import traceback
                traceback.print_exc()
                self.voice_enabled = False
        else:
            self.stop_voice_input()

    def stop_voice_input(self):
        """Stop voice input and cleanup"""
        try:
            self.voice_enabled = False
            
            if self.voice_button:
                self.voice_button.config(text="Start Voice Input")
            if self.voice_status:
                self.voice_status.config(
                    text="Voice: Disabled", 
                    foreground=DarkTheme.FG_MUTED
                )
            
            # Stop audio stream
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception as e:
                    self.logger.error(f"Error stopping stream: {str(e)}")
                self.stream = None
            
            # Signal worker to stop
            if self.raw_queue:
                try:
                    self.raw_queue.put(b"__EXIT__")
                except:
                    pass
            
            # Wait for threads
            if self.voice_thread and self.voice_thread.is_alive():
                self.voice_thread.join(timeout=2.0)
            
            self.logger.system("Voice input stopped")

        except Exception as e:
            self.logger.error(f"Error in stop_voice_input: {str(e)}")

    def voice_processing_loop(self):
        """Process recognized text from text_queue"""
        try:
            self.logger.system("Voice processing loop started")
            self.logger.system(f"Backend: {self.recognition_backend}, Device: {self.recognition_device}")
            
            while self.voice_enabled:
                try:
                    # Get recognized text from queue (non-blocking with timeout)
                    text = self.text_queue.get(timeout=0.1)
                    
                    if text and len(text) >= 3:
                        # Queue for AI processing
                        self.message_queue.put(("voice_input", username, text))
                        self.input_queue.put(text)
                        self.logger.speech(f"Voice recognized: {text}")
                        
                except Exception:
                    # Timeout or queue empty - continue loop
                    continue
                    
        except Exception as e:
            self.logger.error(f"Voice processing loop error: {str(e)}")
            import traceback
            traceback.print_exc()


class VolumeControlPanel:
    """Standalone volume control panel"""
    
    def __init__(self, parent, logger, controls_module):
        self.parent = parent
        self.logger = logger
        self.controls = controls_module
        self.voice_volume_slider = None
        self.voice_volume_label = None
        self.sound_volume_slider = None
        self.sound_volume_label = None
    
    def create_panel(self, show_title=True):
        """Create volume control panel"""
        if show_title:
            container = ttk.LabelFrame(
                self.parent,
                text="Audio Volume",
                style="Dark.TLabelframe"
            )
        else:
            container = ttk.Frame(self.parent)
        
        container.pack(fill=tk.X, pady=5)
        
        # Voice Volume
        voice_frame = ttk.Frame(container)
        voice_frame.pack(fill=tk.X, padx=5, pady=(5, 8))
        
        tk.Label(
            voice_frame,
            text="Voice",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.voice_volume_slider = tk.Scale(
            voice_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_voice_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_PURPLE,
            highlightthickness=0,
            showvalue=0
        )
        self.voice_volume_slider.set(int(self.controls.VOICE_VOLUME * 100))
        self.voice_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_volume_label = tk.Label(
            voice_frame,
            text=f"{int(self.controls.VOICE_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_PURPLE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.voice_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Sound Effects Volume
        sound_frame = ttk.Frame(container)
        sound_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Label(
            sound_frame,
            text="Sounds",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
            width=10,
            anchor="w"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.sound_volume_slider = tk.Scale(
            sound_frame,
            from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_sound_volume_change,
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            troughcolor=DarkTheme.BG_LIGHTER,
            activebackground=DarkTheme.ACCENT_BLUE,
            highlightthickness=0,
            showvalue=0
        )
        self.sound_volume_slider.set(int(self.controls.SOUND_EFFECT_VOLUME * 100))
        self.sound_volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.sound_volume_label = tk.Label(
            sound_frame,
            text=f"{int(self.controls.SOUND_EFFECT_VOLUME * 100)}%",
            font=("Segoe UI", 9, "bold"),
            foreground=DarkTheme.ACCENT_BLUE,
            background=DarkTheme.BG_DARKER,
            width=5
        )
        self.sound_volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        return container
    
    def _on_voice_volume_change(self, value):
        volume = int(value) / 100.0
        self.controls.VOICE_VOLUME = volume
        if self.voice_volume_label:
            self.voice_volume_label.config(text=f"{int(value)}%")
        self.logger.speech(f"Voice volume: {int(value)}%")
    
    def _on_sound_volume_change(self, value):
        volume = int(value) / 100.0
        self.controls.SOUND_EFFECT_VOLUME = volume
        if self.sound_volume_label:
            self.sound_volume_label.config(text=f"{int(value)}%")
        self.logger.system(f"Sound effects volume: {int(value)}%")