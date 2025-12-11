"""
voice_to_text.py - RTX 5060 Ti GPU-Accelerated Speech Recognition
Location: Anna_AI/BASE/tools/internal/voice/voice_to_text.py

Optimized for RTX 5060 Ti with 16GB VRAM
Uses Faster-Whisper with int8 compute (bypasses cuDNN compiled engines requirement)
"""
import os
import sys
import numpy as np
import json
import threading
import sounddevice as sd
import queue
import time
from pathlib import Path

# ============================================================================
# CRITICAL: Add CUDA libraries to PATH before importing faster_whisper
# ============================================================================
def setup_cuda_path():
    """Add nvidia CUDA libraries to system PATH"""
    try:
        # Find site-packages directory
        site_packages = None
        for path in sys.path:
            if 'site-packages' in path and os.path.exists(path):
                site_packages = Path(path)
                break
        
        if site_packages:
            # Look for nvidia cuda libraries
            nvidia_dirs = [
                site_packages / "nvidia" / "cublas" / "bin",
                site_packages / "nvidia" / "cudnn" / "bin",
                site_packages / "nvidia" / "cuda_runtime" / "bin",
            ]
            
            for cuda_dir in nvidia_dirs:
                if cuda_dir.exists():
                    cuda_dir_str = str(cuda_dir)
                    if cuda_dir_str not in os.environ.get('PATH', ''):
                        os.environ['PATH'] = cuda_dir_str + os.pathsep + os.environ.get('PATH', '')
                        print(f"[Voice] Added to PATH: {cuda_dir}")
    except Exception as e:
        print(f"[Voice] Warning: Could not setup CUDA path: {e}")

# Call before any CUDA imports
setup_cuda_path()

# Color output
try:
    from colorama import Fore, init
    init()
    toolTColor = Fore.CYAN
    resetTColor = Fore.RESET
    errorTColor = Fore.RED
except ImportError:
    toolTColor = "\033[96m"
    resetTColor = "\033[0m"
    errorTColor = "\033[91m"

# Bot name filter
try:
    from personality.bot_info import agentname
except ImportError:
    agentname = "Anna"

# Audio settings
samplerate = 16000
AUDIO_BLOCKSIZE = 16384
QUEUE_MAX_SIZE = 50
AUDIO_CHUNK_DURATION = 4.0

# ============================================================================
# RTX 5060 Ti Configuration
# ============================================================================
GPU_CONFIG = {
    'model_size': 'small',
    'compute_type': 'int8',
    'device': 'cuda',
    'beam_size': 5,
}

# ============================================================================
# Model Loading
# ============================================================================

def load_whisper_model():
    """Load Faster-Whisper optimized for RTX 5060 Ti"""
    from faster_whisper import WhisperModel
    
    print(toolTColor + "[Voice] Loading Faster-Whisper (SMALL, int8) for RTX 5060 Ti..." + resetTColor)
    
    try:
        model = WhisperModel(
            GPU_CONFIG['model_size'],
            device=GPU_CONFIG['device'],
            compute_type=GPU_CONFIG['compute_type'],
            cpu_threads=0,
            num_workers=1,
        )
        
        print(toolTColor + "[Voice] Warming up GPU..." + resetTColor)
        dummy = np.zeros(16000, dtype=np.float32)
        _ = list(model.transcribe(dummy, language="en"))
        print(toolTColor + "[Voice] [SUCCESS] RTX 5060 Ti ready!" + resetTColor)
        
        return model
    except Exception as e:
        print(errorTColor + f"[Voice] GPU initialization failed: {e}" + resetTColor)
        if "cudnn" in str(e).lower():
            print(errorTColor + "[Voice] cuDNN error detected" + resetTColor)
        raise

def load_vosk_model():
    """Load Vosk model from fixed path"""
    from vosk import Model
    
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    model_path = project_root / "models" / "vosk-model-en-us-0.42-gigaspeech"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Vosk model not found: {model_path}")
    
    print(toolTColor + f"[Voice] Loading Vosk from: {model_path}" + resetTColor)
    return Model(str(model_path))

def list_audio_devices():
    """List all available audio input devices"""
    
    print(toolTColor + "AVAILABLE AUDIO DEVICES:" + resetTColor)
    
    
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']} (IN: {device['max_input_channels']} channels)")
    
    
    return devices

# ============================================================================
# Audio Initialization
# ============================================================================

def init_audio(self):
    """Initialize audio system - try GPU, fallback to CPU"""
    
    print(toolTColor + "VOICE INPUT - RTX 5060 Ti" + resetTColor)
    
    
    use_gpu = True
    
    if use_gpu:
        try:
            import torch
            if torch.cuda.is_available():
                print(toolTColor + f"[Voice] GPU: {torch.cuda.get_device_name(0)}" + resetTColor)
                self.whisper_model = load_whisper_model()
                self.recognition_backend = "whisper"
                self.recognition_device = "cuda"
            else:
                raise RuntimeError("CUDA not available")
        except Exception as e:
            print(errorTColor + f"[Voice] GPU failed: {e}" + resetTColor)
            print(toolTColor + "[Voice] Falling back to Vosk (CPU)..." + resetTColor)
            self.vosk_model = load_vosk_model()
            self.recognition_backend = "vosk"
            self.recognition_device = "cpu"
    else:
        print(toolTColor + "[Voice] Using Vosk (CPU)" + resetTColor)
        self.vosk_model = load_vosk_model()
        self.recognition_backend = "vosk"
        self.recognition_device = "cpu"
    
    # Queues
    self.raw_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)
    self.text_queue = queue.Queue(maxsize=20)
    
    # Stats
    self.overflow_count = 0
    self.last_overflow_log = 0
    self.transcription_times = []
    
    print(toolTColor + f"[Voice] Backend: {self.recognition_backend.upper()} on {self.recognition_device.upper()}" + resetTColor)
    

# ============================================================================
# Recognition Workers - WITH ENHANCED DEBUG
# ============================================================================

def recognition_worker_whisper(self):
    """GPU recognition worker using Faster-Whisper - ENHANCED DEBUG"""
    print(toolTColor + "[Whisper] GPU worker started (RTX 5060 Ti, int8)" + resetTColor)
    
    audio_buffer = []
    samples_per_chunk = int(samplerate * AUDIO_CHUNK_DURATION)
    
    # Test inference immediately
    try:
        print(toolTColor + "[Whisper] Testing GPU inference..." + resetTColor)
        test_audio = np.zeros(16000, dtype=np.float32)
        _ = list(self.whisper_model.transcribe(test_audio, language="en"))
        print(toolTColor + "[Whisper] [SUCCESS] GPU inference working" + resetTColor)
    except Exception as e:
        print(errorTColor + f"[Whisper] GPU inference test FAILED: {e}" + resetTColor)
        return
    
    chunk_count = 0
    data_received_count = 0
    last_buffer_log = 0
    
    print(toolTColor + f"[Whisper] Waiting for audio data (need {samples_per_chunk} samples = {AUDIO_CHUNK_DURATION}s)..." + resetTColor)
    
    while True:
        try:
            data = self.raw_queue.get(timeout=0.1)
            
            if data == b"__EXIT__":
                if self.transcription_times:
                    avg = sum(self.transcription_times) / len(self.transcription_times)
                    rtf = avg / AUDIO_CHUNK_DURATION
                    print(toolTColor + f"[Whisper] Avg: {avg:.3f}s, RTF: {rtf:.3f}x" + resetTColor)
                break
            
            data_received_count += 1
            audio_array = np.frombuffer(data, dtype=np.int16)
            audio_buffer.extend(audio_array)
            
            # ENHANCED DEBUG: Log every data packet received
            if data_received_count <= 5:
                print(toolTColor + f"[Whisper] Data packet #{data_received_count}: {len(audio_array)} samples, buffer now: {len(audio_buffer)} samples ({len(audio_buffer)/samplerate:.1f}s)" + resetTColor)
            
            # ENHANCED DEBUG: Log buffer growth every 1 second
            current_buffer_seconds = len(audio_buffer) / samplerate
            if int(current_buffer_seconds) > last_buffer_log:
                print(toolTColor + f"[Whisper] Buffer: {current_buffer_seconds:.1f}s of audio ({len(audio_buffer)} samples)" + resetTColor)
                last_buffer_log = int(current_buffer_seconds)
            
            if len(audio_buffer) >= samples_per_chunk:
                chunk_count += 1
                start = time.time()
                
                print(toolTColor + f"[Whisper] [SUCCESS] Reached 4s threshold! Processing chunk #{chunk_count}..." + resetTColor)
                
                audio_chunk = np.array(audio_buffer[:samples_per_chunk], dtype=np.float32) / 32768.0
                audio_buffer = audio_buffer[samples_per_chunk:]
                
                print(toolTColor + f"[Whisper] Transcribing {len(audio_chunk)} samples..." + resetTColor)
                
                segments, info = self.whisper_model.transcribe(
                    audio_chunk,
                    language="en",
                    beam_size=GPU_CONFIG['beam_size'],
                    vad_filter=True,
                    vad_parameters=dict(
                        threshold=0.5,
                        min_speech_duration_ms=250,
                        min_silence_duration_ms=500
                    ),
                    without_timestamps=True,
                )
                
                elapsed = time.time() - start
                self.transcription_times.append(elapsed)
                if len(self.transcription_times) > 100:
                    self.transcription_times.pop(0)
                
                text = " ".join([s.text.strip() for s in segments])
                
                # ENHANCED DEBUG: Always log results (even empty)
                if text and text.strip():
                    print(toolTColor + f"[Whisper] Detected: '{text}' ({len(text)} chars)" + resetTColor)
                else:
                    print(toolTColor + f"[Whisper] No speech in chunk #{chunk_count}" + resetTColor)
                
                if len(text) >= 5 and agentname.lower() not in text.lower():
                    try:
                        self.text_queue.put_nowait(text)
                        rtf = elapsed / AUDIO_CHUNK_DURATION
                        print(toolTColor + f"[Whisper] [SUCCESS] QUEUED: '{text}' ({elapsed:.2f}s, {rtf:.2f}x)" + resetTColor)
                    except queue.Full:
                        try:
                            self.text_queue.get_nowait()
                            self.text_queue.put_nowait(text)
                            print(toolTColor + f"[Whisper] Queue was full, replaced oldest" + resetTColor)
                        except:
                            pass
                            
        except queue.Empty:
            # CRITICAL FIX: Only process partial buffer on explicit timeout, NOT every empty queue
            # This was causing premature buffer clearing
            continue
                    
        except Exception as e:
            print(errorTColor + f"[Whisper] Error: {e}" + resetTColor)
            if "cudnn" in str(e).lower():
                print(errorTColor + "[Whisper] cuDNN error - worker stopping" + resetTColor)
                break

def recognition_worker_vosk(self):
    """CPU recognition worker using Vosk"""
    from vosk import KaldiRecognizer
    
    print(toolTColor + "[Vosk] CPU worker started" + resetTColor)
    rec = KaldiRecognizer(self.vosk_model, samplerate)
    
    while True:
        try:
            data = self.raw_queue.get(timeout=0.1)
            
            if data == b"__EXIT__":
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                
                if len(text) >= 5 and agentname.lower() not in text.lower():
                    try:
                        self.text_queue.put_nowait(text)
                        print(toolTColor + f"[Vosk] {text}" + resetTColor)
                    except queue.Full:
                        try:
                            self.text_queue.get_nowait()
                            self.text_queue.put_nowait(text)
                        except:
                            pass
                    
        except queue.Empty:
            continue
        except Exception as e:
            print(errorTColor + f"[Vosk] Error: {e}" + resetTColor)

# ============================================================================
# Stream Starter - WITH ENHANCED DEBUG
# ============================================================================

def start_vosk_stream(self):
    """Start recognition worker and audio stream"""
    
    # Try devices that are likely your headset mic
    PREFERRED_DEVICES = [1, 12, 29, 35]
    audio_device = None
    
    print(toolTColor + "[Voice] Testing audio devices..." + resetTColor)
    
    for device_idx in PREFERRED_DEVICES:
        try:
            device_info = sd.query_devices(device_idx)
            device_name = device_info['name']
            
            if 'cable' in device_name.lower() or 'vb-audio' in device_name.lower():
                continue
            
            print(toolTColor + f"[Voice] Testing device {device_idx}: {device_name}..." + resetTColor)
            test_stream = sd.RawInputStream(
                samplerate=samplerate,
                blocksize=2048,
                dtype="int16",
                channels=1,
                device=device_idx
            )
            test_stream.close()
            
            audio_device = device_idx
            print(toolTColor + f"[Voice] [SUCCESS] Device {audio_device} works: {device_name}" + resetTColor)
            break
            
        except Exception as e:
            print(errorTColor + f"[Voice] Device {device_idx} failed: {e}" + resetTColor)
            continue
    
    if audio_device is None:
        print(errorTColor + f"[Voice] No working microphone found!" + resetTColor)
        list_audio_devices()
        raise RuntimeError("No functional audio input device available")
    
    # Start appropriate worker
    if self.recognition_backend == "whisper":
        worker = threading.Thread(
            target=lambda: recognition_worker_whisper(self),
            daemon=True,
            name="WhisperGPU-RTX5060Ti"
        )
    else:
        worker = threading.Thread(
            target=lambda: recognition_worker_vosk(self),
            daemon=True,
            name="VoskCPU"
        )
    worker.start()
    print(toolTColor + f"[Voice] Recognition worker started ({self.recognition_backend})" + resetTColor)
    
    # Audio callback with ENHANCED debugging
    def audio_callback(indata, frames, time_info, status):
        if status:
            if 'overflow' in str(status).lower():
                self.overflow_count += 1
                current_time = time.time()
                if current_time - self.last_overflow_log > 5.0:
                    print(toolTColor + f"[Audio] Overflow #{self.overflow_count}" + resetTColor)
                    self.last_overflow_log = current_time
            else:
                print(toolTColor + f"[Audio] Status: {status}" + resetTColor)
        
        # Check audio level
        audio_data = np.frombuffer(indata, dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_data))
        
        # ENHANCED DEBUG: More frequent logging
        if not hasattr(self, '_audio_debug_counter'):
            self._audio_debug_counter = 0
            self._last_nonzero_audio = 0
        
        self._audio_debug_counter += 1
        
        # Log every 2 seconds
        if self._audio_debug_counter % 30 == 0:
            print(toolTColor + f"[Audio] Level: {max_amplitude} (queue size: {self.raw_queue.qsize()})" + resetTColor)
        
        # Alert when audio detected
        if max_amplitude > 500:
            if time.time() - self._last_nonzero_audio > 2.0:
                print(toolTColor + f"[Audio] 🎤 SOUND DETECTED! Level: {max_amplitude}" + resetTColor)
            self._last_nonzero_audio = time.time()
        
        try:
            self.raw_queue.put_nowait(bytes(indata))
        except queue.Full:
            print(errorTColor + "[Audio] Queue full!" + resetTColor)
    
    # Start audio stream
    print(toolTColor + f"[Voice] Starting audio stream (device={audio_device}, blocksize={AUDIO_BLOCKSIZE})..." + resetTColor)
    
    self.stream = sd.RawInputStream(
        samplerate=samplerate,
        blocksize=AUDIO_BLOCKSIZE,
        dtype="int16",
        channels=1,
        device=audio_device,
        callback=audio_callback,
        latency='high'
    )
    self.stream.start()
    
    print(toolTColor + f"[Voice] [SUCCESS] Audio stream active" + resetTColor)
    print(toolTColor + f"[Voice] [SUCCESS] Listening for speech..." + resetTColor)

# Audio callback method for class (legacy compatibility)
def audio_callback(self, indata, frames, time_info, status):
    """Audio callback for VTuberAI class"""
    if status:
        print(toolTColor + f"[Audio] {status}" + resetTColor)
    self.raw_queue.put(bytes(indata))