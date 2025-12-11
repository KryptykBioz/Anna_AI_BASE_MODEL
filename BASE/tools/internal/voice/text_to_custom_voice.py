# Filename: BASE/tools/internal/voice/text_to_custom_voice.py
# FIXED: Force soundfile backend to avoid TorchCodec issues on Windows

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '12'
os.environ['MKL_NUM_THREADS'] = '12'

import sys
from pathlib import Path
import time
import tempfile
import sounddevice as sd
import soundfile as sf
import torch

# === WORKAROUND: Disable cuDNN for problematic operations ===
# PyTorch 2.10+ on Windows has cuDNN library loading issues with RTX 50-series
torch.backends.cudnn.enabled = False
print("[NOTICE] cuDNN disabled - using native PyTorch operations (minor performance impact)")

import re
import numpy as np
import pickle
import hashlib

# === CRITICAL: Disable TorchCodec to avoid FFmpeg DLL errors on Windows ===
os.environ['TORCHAUDIO_USE_BACKEND_DISPATCHER'] = '0'
os.environ['TORCHAUDIO_BACKEND'] = 'soundfile'

import torchaudio
# Monkey-patch torchaudio.load to use soundfile directly
import soundfile as sf_lib
_original_torchaudio_load = torchaudio.load

def _soundfile_load(filepath, *args, **kwargs):
    """Load audio using soundfile instead of TorchCodec"""
    try:
        data, sr = sf_lib.read(filepath, dtype='float32')
        # Convert to torch tensor with shape (channels, samples)
        if len(data.shape) == 1:
            audio = torch.from_numpy(data).unsqueeze(0)
        else:
            audio = torch.from_numpy(data.T)
        return audio, sr
    except Exception as e:
        # Fallback to original if something goes wrong
        return _original_torchaudio_load(filepath, *args, **kwargs)

torchaudio.load = _soundfile_load

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from personality.bot_info import agentname
agentname = agentname.lower()

# Global state
_tts = None
_embeddings_cache = {}
_audio_cache = {}
MAX_AUDIO_CACHE = 50
_device = None

def check_pytorch_cuda_compatibility():
    """Check if PyTorch supports the available GPU"""
    if not torch.cuda.is_available():
        return False, "CUDA not available"
    
    try:
        major, minor = torch.cuda.get_device_capability(0)
        sm_version = f"sm_{major}{minor}"
        gpu_name = torch.cuda.get_device_name(0)
        
        # Test GPU operation
        test_tensor = torch.zeros(1).cuda()
        result = test_tensor + 1
        del test_tensor, result
        torch.cuda.empty_cache()
        
        return True, f"Compatible (GPU: {gpu_name}, Compute: {sm_version})"
    except RuntimeError as e:
        error_msg = str(e)
        if "no kernel image is available" in error_msg.lower():
            major, minor = torch.cuda.get_device_capability(0)
            gpu_name = torch.cuda.get_device_name(0)
            return False, f"Incompatible - {gpu_name} (sm_{major}{minor}) not supported"
        return False, f"CUDA error: {error_msg[:100]}"

def get_best_device():
    """Detect and select best available GPU"""
    global _device
    
    if _device is not None:
        return _device
    
    force_device = os.environ.get('XTTS_DEVICE', '').lower()
    if force_device == 'cpu':
        print("[WARNING] CPU mode forced via XTTS_DEVICE environment variable")
        _device = 'cpu'
        return _device
    
    print("\n=== GPU Detection ===")
    
    cuda_compatible, cuda_msg = check_pytorch_cuda_compatibility()
    print(f"CUDA Status: {cuda_msg}")
    
    if cuda_compatible:
        _device = 'cuda'
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"[SUCCESS] Using Nvidia GPU: {gpu_name}")
        print(f"  VRAM Available: {vram:.1f} GB")
        return _device
    
    
    print(" Falling back to CPU mode")
    
    print("\n Using optimized CPU mode:")
    print("  - Multi-threading optimized for your CPU")
    print("  - Dual caching (embeddings + audio) for speed")
    
    
    _device = 'cpu'
    return _device

def init_tts():
    """Initialize XTTS with optimized settings and soundfile backend"""
    global _tts
    
    if _tts:
        return _tts
    
    device = get_best_device()
    
    if device == 'cpu':
        torch.set_num_threads(12)
    else:
        torch.set_num_threads(4)
    
    device_name = device if isinstance(device, str) else str(device)
    print(f"\nLoading XTTS v2 on {device_name.upper()}...")
    
    _orig = torch.load
    torch.load = lambda *a, **k: _orig(*a, **{**k, 'weights_only': False})
    
    try:
        from TTS.api import TTS
        import warnings
        warnings.filterwarnings('ignore')
        
        # Load model to selected device
        _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        # Set to eval mode
        model = _tts.synthesizer.tts_model
        model.eval()
        for p in model.parameters():
            p.requires_grad = False
        
        print(f"[SUCCESS] XTTS v2 loaded on {device_name.upper()}")
        
        if device == 'cuda':
            torch.cuda.empty_cache()
            
    finally:
        torch.load = _orig
    
    return _tts

def get_embeddings(ref_audio):
    """Get and cache voice embeddings"""
    global _embeddings_cache
    
    device = get_best_device()
    key = str(ref_audio)
    
    if key in _embeddings_cache:
        return _embeddings_cache[key]
    
    tts = init_tts()
    model = tts.synthesizer.tts_model
    
    print("Computing embeddings (one-time)...")
    
    # Workaround for cuDNN issues on Windows with PyTorch 2.10+
    # Do resampling operations on CPU, then move to GPU
    try:
        with torch.no_grad():
            # Try GPU first
            gpt, spk = model.get_conditioning_latents(audio_path=str(ref_audio))
            
            if device == 'cuda':
                gpt = gpt.to(device)
                spk = spk.to(device)
    except RuntimeError as e:
        if 'CUDNN' in str(e) or 'cuDNN' in str(e):
            print(f"  [cuDNN error detected, using CPU workaround for resampling]")
            # Force CPU for embedding computation due to cuDNN issues
            original_device = model.device
            model.to('cpu')
            
            try:
                with torch.no_grad():
                    gpt, spk = model.get_conditioning_latents(audio_path=str(ref_audio))
                
                # Move back to GPU after computation
                if device == 'cuda':
                    model.to(device)
                    gpt = gpt.to(device)
                    spk = spk.to(device)
            except Exception as e2:
                # Restore model and re-raise
                model.to(original_device)
                raise e2
        else:
            raise
    
    _embeddings_cache[key] = (gpt, spk)
    
    # Save cache
    cache_file = Path("./personality/memory/voice_embeddings_cache.pkl")
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        cpu_cache = {k: (g.cpu(), s.cpu()) for k, (g, s) in _embeddings_cache.items()}
        with open(cache_file, 'wb') as f:
            pickle.dump(cpu_cache, f)
    except Exception as e:
        print(f"Warning: Could not save embeddings cache: {e}")
    
    print("[SUCCESS] Embeddings cached")
    return gpt, spk

def load_embeddings_cache():
    """Load cached embeddings from disk"""
    global _embeddings_cache
    
    cache_file = Path("./personality/memory/voice_embeddings_cache.pkl")
    
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                cpu_cache = pickle.load(f)
            
            # Validate cache format - should be dict of (gpt, spk) tuples
            if not cpu_cache or not isinstance(cpu_cache, dict):
                print(f"Warning: Invalid cache format, clearing cache")
                cache_file.unlink()
                return
            
            # Check if first item has the right format (tuple of 2 tensors)
            first_key = next(iter(cpu_cache))
            first_val = cpu_cache[first_key]
            if not isinstance(first_val, tuple) or len(first_val) != 2:
                print(f"Warning: Old cache format detected, clearing cache")
                cache_file.unlink()
                return
            
            try:
                device = get_best_device()
                if device == 'cuda':
                    _embeddings_cache = {k: (g.to(device), s.to(device)) for k, (g, s) in cpu_cache.items()}
                else:
                    _embeddings_cache = cpu_cache
                    
                print(f"[SUCCESS] Loaded {len(_embeddings_cache)} cached embeddings")
            except Exception as e:
                print(f"Warning: Error moving embeddings to device: {e}, clearing cache")
                cache_file.unlink()
        except Exception as e:
            print(f"Warning: Could not load embeddings cache: {e}, clearing cache")
            try:
                cache_file.unlink()
            except:
                pass

def get_text_hash(text):
    """Get hash for text caching"""
    return hashlib.md5(text.encode()).hexdigest()[:16]

def find_vb_cable():
    """Find VB-Cable"""
    devs = sd.query_devices()
    for i, d in enumerate(devs):
        if d['max_output_channels'] > 0:
            name = d['name'].lower()
            if any(p in name for p in ("cable input", "vb-audio", "voicemeeter")):
                return i
    return None

def detect_and_fix_artifacts(audio, sample_rate=24000, threshold=0.9, min_duration=0.3):
    """
    Detect and fix audio artifacts (stretched/stuck phonemes)
    
    Args:
        audio: Audio array
        sample_rate: Sample rate (default 24000 for XTTS)
        threshold: Correlation threshold for detecting repetition (0.9 = 90% similar)
        min_duration: Minimum duration in seconds to consider as artifact
        
    Returns:
        Fixed audio array
    """
    # Convert to numpy if needed
    if isinstance(audio, torch.Tensor):
        audio = audio.cpu().numpy()
    
    # Ensure 1D
    if len(audio.shape) > 1:
        audio = audio.flatten()
    
    # Calculate window size (check chunks of 50ms)
    window_size = int(sample_rate * 0.05)  # 50ms windows
    min_samples = int(sample_rate * min_duration)
    
    # Find stuck/repeating sections
    i = 0
    fixed_audio = []
    
    while i < len(audio):
        # Check if we have enough samples for comparison
        if i + window_size * 2 > len(audio):
            # Near end, just append remaining
            fixed_audio.extend(audio[i:])
            break
        
        # Get current window and next window
        current_window = audio[i:i+window_size]
        next_window = audio[i+window_size:i+window_size*2]
        
        # Calculate correlation
        correlation = np.corrcoef(current_window, next_window)[0, 1]
        
        # If highly correlated (repetitive), check how long it continues
        if correlation > threshold:
            # Found potential artifact, measure its length
            artifact_length = window_size
            j = i + window_size
            
            while j + window_size < len(audio):
                test_window = audio[j:j+window_size]
                test_correlation = np.corrcoef(current_window, test_window)[0, 1]
                
                if test_correlation > threshold:
                    artifact_length += window_size
                    j += window_size
                else:
                    break
            
            # If artifact is long enough, fix it
            if artifact_length >= min_samples:
                # Replace artifact with single instance + fade
                single_instance = audio[i:i+window_size]
                
                # Add single instance
                fixed_audio.extend(single_instance)
                
                # Skip the rest of the artifact
                i += artifact_length
                
                print(f"  [Artifact Fix] Removed {artifact_length/sample_rate:.2f}s repetition")
            else:
                # Not long enough to be artifact, keep it
                fixed_audio.extend(current_window)
                i += window_size
        else:
            # Normal audio, keep it
            fixed_audio.extend(current_window)
            i += window_size
    
    return np.array(fixed_audio)

def clean_text(text):
    """Clean text for TTS with anti-artifact preprocessing"""
    # Remove emojis
    text = re.sub(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+',
        '', text
    )
    
    # Remove asterisk actions
    text = re.sub(r'\*[^*]*\*', '', text)
    
    # Normalize names
    text = text.replace('kryptyk', 'Cryptic')
    text = text.replace('Kryptyk', 'Cryptic')
    text = text.replace('KRYPTYK', 'Cryptic')
    
    # === ANTI-ARTIFACT: Expand contractions ===
    contractions = {
        "I'll": "I will", "I'm": "I am", "I've": "I have", "I'd": "I would",
        "you'll": "you will", "you're": "you are", "you've": "you have",
        "we'll": "we will", "we're": "we are",
        "they'll": "they will", "they're": "they are",
        "it'll": "it will", "it's": "it is",
        "that's": "that is", "there's": "there is",
        "what's": "what is", "who's": "who is", "where's": "where is",
        "can't": "cannot", "won't": "will not", "don't": "do not",
        "doesn't": "does not", "didn't": "did not",
        "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
        "shouldn't": "should not", "wouldn't": "would not", "couldn't": "could not"
    }
    
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)
    
    # Clean punctuation
    text = text.replace("...", ".")
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'([!?]){2,}', r'\1', text)
    text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'_', ' ', text)
    
    return text.strip()
    # """Clean text for TTS"""
    # # Remove emojis
    # text = re.sub(
    #     r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    #     r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+',
    #     '', text
    # )
    
    # # Remove asterisk actions
    # text = re.sub(r'\*[^*]*\*', '', text)
    
    # # Normalize names
    # text = text.replace('kryptyk', 'Cryptic')
    # text = text.replace('Kryptyk', 'Cryptic')
    # text = text.replace('KRYPTYK', 'Cryptic')
    
    # # Expand contractions
    # contractions = {
    #     "I'll": "I will", "I'm": "I am", "I've": "I have", "I'd": "I would",
    #     "you'll": "you will", "you're": "you are", "you've": "you have",
    #     "we'll": "we will", "we're": "we are",
    #     "they'll": "they will", "they're": "they are",
    #     "it'll": "it will", "it's": "it is",
    #     "that's": "that is", "there's": "there is",
    #     "what's": "what is", "who's": "who is", "where's": "where is",
    #     "can't": "cannot", "won't": "will not", "don't": "do not",
    #     "doesn't": "does not", "didn't": "did not",
    #     "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    #     "shouldn't": "should not", "wouldn't": "would not", "couldn't": "could not"
    # }
    
    # for contraction, expansion in contractions.items():
    #     text = text.replace(contraction, expansion)
    
    # # Clean punctuation
    # text = text.replace("...", ".")
    # text = re.sub(r'\.{2,}', '.', text)
    # text = re.sub(r'([!?]){2,}', r'\1', text)
    # text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
    # text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # text = re.sub(r'\s+', ' ', text)
    # text = re.sub(r'_', ' ', text)
    
    # return text.strip()

def speak_stream(text, ref_audio, language="en", speed=1.0, stop_flag=None, volume=1.0):
    """Stream speech sentence-by-sentence"""
    text = clean_text(text)
    
    if not text:
        print("Warning: Empty text after cleaning")
        return "No text"
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        sentences = [text]
    
    volume_percent = int(volume * 100)
    print(f"\n=== Speaking {len(sentences)} sentences (volume: {volume_percent}%) ===")
    for i, s in enumerate(sentences, 1):
        print(f"[Sentence {i}]: {s[:50]}{'...' if len(s) > 50 else ''}")
    
    try:
        get_embeddings(ref_audio)
    except Exception as e:
        print(f"Error loading reference audio: {e}")
        return f"Error: {e}"
    
    for i, s in enumerate(sentences, 1):
        if stop_flag and stop_flag.is_set():
            print("Stream interrupted")
            return "Interrupted"
        
        print(f"\n[Speaking {i}/{len(sentences)}]")
        result = speak_custom_voice(s, ref_audio, language, speed, True, True, stop_flag, volume)
        
        if result == "Interrupted":
            return "Interrupted"
        elif result.startswith("Error"):
            print(f"Warning: {result}")
            continue
    
    print("\n=== Stream complete ===")
    return "[SUCCESS]"

def speak_custom_voice(text, ref_audio=f"./personality/voice/{agentname}_voice_sample.wav", 
          language="en", speed=1.0, use_cache=True, fallback=True, stop_flag=None, volume=1.0):
    """XTTS GPU-accelerated voice cloning with caching"""
    global _audio_cache
    
    try:
        device = get_best_device()
    except Exception as e:
        return f"Error: {e}"
    
    if stop_flag and stop_flag.is_set():
        return "Interrupted"
    
    if not Path(ref_audio).exists():
        return "Error: Voice sample not found"
    
    text = clean_text(text)
    if not text:
        return "No text"
    
    volume_percent = int(volume * 100)
    print(f"  Text: '{text}' (volume: {volume_percent}%)")
    
    # Check cache
    text_hash = get_text_hash(text)
    cache_key = f"{ref_audio}_{text_hash}_{language}_{speed}"
    
    temp_wav = Path(tempfile.gettempdir()) / f"tts_{os.getpid()}.wav"
    
    try:
        if stop_flag and stop_flag.is_set():
            return "Interrupted"
        
        if use_cache and cache_key in _audio_cache:
            print(f"  [CACHED]")
            audio = _audio_cache[cache_key]
        else:
            tts = init_tts()
            model = tts.synthesizer.tts_model
            
            device_name = device if isinstance(device, str) else str(device)
            print(f"  [GENERATING on {device_name.upper()}...]")
            
            if stop_flag and stop_flag.is_set():
                return "Interrupted"
            
            # Get cached embeddings
            gpt, spk = get_embeddings(ref_audio)
            
            with torch.no_grad():
                # === ANTI-ARTIFACT INFERENCE PARAMETERS ===
                out = model.inference(
                    text=text,
                    language=language,
                    gpt_cond_latent=gpt,
                    speaker_embedding=spk,
                    temperature=0.7,        # Slightly higher for more variation
                    length_penalty=1.2,     # Increased to discourage long phonemes
                    repetition_penalty=10.0, # Increased to strongly discourage repetition
                    top_k=50,               # Increased for more diversity
                    top_p=0.85,             # Slightly higher for more options
                    speed=speed,
                    enable_text_splitting=True
                )
                audio = out['wav']
            
            # === POST-PROCESS: ARTIFACT DETECTION & REMOVAL ===
            audio = detect_and_fix_artifacts(audio, sample_rate=24000)
            
            if device == 'cuda':
                torch.cuda.empty_cache()
            
            if stop_flag and stop_flag.is_set():
                return "Interrupted"
            
            # Cache audio
            if use_cache and len(_audio_cache) < MAX_AUDIO_CACHE:
                if isinstance(audio, torch.Tensor):
                    _audio_cache[cache_key] = audio.cpu().clone()
                else:
                    _audio_cache[cache_key] = audio.copy()
        
        # Convert and apply volume
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()
        
        audio = audio * volume
        audio = np.clip(audio, -1.0, 1.0)
        sf.write(temp_wav, audio, 24000)
        
        if stop_flag and stop_flag.is_set():
            return "Interrupted"
        
        # Play
        data, sr = sf.read(temp_wav, dtype='float32')
        dev = find_vb_cable()
        
        if dev is None and not fallback:
            return "Error: No VB-Cable"
        
        sd.play(data, sr, device=dev)
        
        # Check for interruption during playback
        duration = len(data) / sr
        elapsed = 0
        check_interval = 0.05
        
        while elapsed < duration:
            if stop_flag and stop_flag.is_set():
                sd.stop()
                return "Interrupted"
            
            time_to_sleep = min(check_interval, duration - elapsed)
            time.sleep(time_to_sleep)
            elapsed += time_to_sleep
        
        if not (stop_flag and stop_flag.is_set()):
            sd.wait()
        
        print(f"  [DONE]")
        return "[SUCCESS]"
    
    except Exception as e:
        if stop_flag and stop_flag.is_set():
            sd.stop()
            return "Interrupted"
        import traceback
        traceback.print_exc()
        return f"Error: {e}"
    
    finally:
        if temp_wav.exists():
            try:
                temp_wav.unlink()
            except:
                pass

def preload_common_phrases(ref_audio, phrases):
    """Pre-cache common phrases"""
    print(f"\n=== Pre-caching {len(phrases)} phrases ===")
    
    try:
        get_embeddings(ref_audio)
    except Exception as e:
        print(f"Cannot pre-cache: {e}")
        return
    
    for i, phrase in enumerate(phrases, 1):
        print(f"[{i}/{len(phrases)}] {phrase}")
        speak_custom_voice(phrase, ref_audio, use_cache=True)
    
    print(f"[SUCCESS] Cached {len(_audio_cache)} audio clips\n")

def benchmark():
    """Performance test"""
    VOICE = f"./../../personality/voice/{agentname}_voice_sample.wav"
    
    if not Path(VOICE).exists():
        print("[WARNING] Voice not found")
        return
    
    print("\n=== Benchmark ===\n")
    
    try:
        device = get_best_device()
        device_name = device if isinstance(device, str) else str(device)
        print(f"Testing on: {device_name.upper()}\n")
    except Exception as e:
        print(f"Cannot run benchmark: {e}")
        return
    
    load_embeddings_cache()
    init_tts()
    
    test = "The quick brown fox jumps over the lazy dog."
    
    print("Test 1: Cold start")
    _audio_cache.clear()
    start = time.perf_counter()
    speak_custom_voice(test, VOICE, use_cache=True)
    t1 = time.perf_counter() - start
    print(f"Time: {t1:.2f}s\n")
    
    print("Test 2: Cached embeddings")
    start = time.perf_counter()
    speak_custom_voice("Another sentence to test speed.", VOICE, use_cache=True)
    t2 = time.perf_counter() - start
    print(f"Time: {t2:.2f}s\n")
    
    print("Test 3: Cached audio (instant)")
    start = time.perf_counter()
    speak_custom_voice(test, VOICE, use_cache=True)
    t3 = time.perf_counter() - start
    print(f"Time: {t3:.2f}s")
    
    print(f"\nSpeedup (embeddings): {t1/t2:.1f}x")
    print(f"Speedup (audio cache): {t1/t3:.1f}x")
    
    if device == 'cuda':
        print(f"\nGPU Memory Used: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
        print(f"GPU Memory Cached: {torch.cuda.memory_reserved() / 1024**2:.1f} MB")
    
    print("\n=== Complete ===\n")

def setup_voice():
    """Setup Agent with common phrases pre-cached"""
    VOICE = f"./personality/voice/{agentname}_voice_sample.wav"
    
    if not Path(VOICE).exists():
        print(f"[WARNING] Voice not found: {VOICE}")
        return
    
    data, sr = sf.read(VOICE)
    print(f"\n=== Agent Voice ===")
    print(f"Duration: {len(data)/sr:.1f}s")
    print(f"Sample rate: {sr} Hz\n")
    
    load_embeddings_cache()
    
    try:
        init_tts()
    except Exception as e:
        print(f"Cannot initialize voice: {e}")
        return
    
    common = [
        "Hello everyone!",
        "Are you stalling?",
        "You're not very tall!",
        "That is really interesting.",
        "I appreciate you.",
        "Let's play a new game together'.",
        "The mystery of life is found in the void.",
        "I am not saying that.",
        "yellow llama yellow llama yellow llama",
        "See you next time!"
    ]
    
    print("Pre-caching common VTuber phrases...")
    preload_common_phrases(VOICE, common)
    
    print("Testing pre-cached phrase...")
    speak_custom_voice("Hello everyone!", VOICE)
    
    try:
        device = get_best_device()
        device_name = device if isinstance(device, str) else str(device)
        print(f"\n[SUCCESS] Agent voice ready on {device_name.upper()}!")
        print(f"  - {len(_audio_cache)} phrases cached")
        print(f"  - Cached phrases play instantly")
        
        if device == 'cuda':
            print(f"  - GPU-accelerated generation")
        else:
            print(f"  - CPU mode: 2-4s generation per phrase")
    except:
        pass

if __name__ == "__main__":
    load_embeddings_cache()
    benchmark()
    setup_voice()
    
    print("\n=== Streaming Demo ===\n")
    VOICE = f"./personality/voice/{agentname}_voice_sample.wav"
    if Path(VOICE).exists():
        text = "Hello! I am Agent. This system uses XTTS with GPU acceleration. Common phrases play instantly."
        speak_stream(text, VOICE)