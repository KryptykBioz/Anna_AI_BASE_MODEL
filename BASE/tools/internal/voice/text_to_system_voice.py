# ============================================================================
# Filename: BASE/tools/internal/voice/text_to_system_voice.py
# FIXED V2: Volume control via audio data multiplication (more reliable)
# ============================================================================
"""
System Voice (pyttsx3) Implementation

Pure implementation file - no interface coupling.
Used by Pyttsx3Backend to generate and play speech.

CRITICAL: Never call engine.stop() - it breaks subsequent calls.
The engine must stay running between speech operations.

FIXED V2: Volume applied to audio data for cross-platform reliability
pyttsx3's engine.setProperty('volume') is unreliable on some systems,
so we generate at full volume then scale the audio data.
"""
import os
import tempfile
import pyttsx3
import sounddevice as sd
import soundfile as sf
import threading
import numpy as np
from pathlib import Path

from personality.bot_info import voiceIndex
from BASE.core.logger import get_logger
from BASE.tools.internal.voice.voice_utils import (
    clean_text_for_tts,
    find_vb_cable_device,
    list_audio_devices
)

# Initialize logger
logger = get_logger()

# Global temp file tracking to prevent conflicts
_current_temp_file = None
_temp_file_lock = threading.Lock()


def _get_temp_wav():
    """Create and track a unique temp WAV file"""
    global _current_temp_file
    with _temp_file_lock:
        if _current_temp_file and os.path.exists(_current_temp_file):
            try:
                os.remove(_current_temp_file)
            except:
                pass
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="tts_")
        os.close(fd)
        _current_temp_file = path
        return path


def _cleanup_temp_file(path):
    """Safely delete temp file"""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.warning(f"Failed to delete temp file {path}: {e}")


def speak_system_voice(text: str, engine, stop_event=None, volume: float = 1.0) -> str:
    """
    Generate and play speech using system voice with volume control
    
    CRITICAL: This function does NOT call engine.stop()
    The engine must remain running for subsequent calls.
    
    FIXED V2: Volume applied directly to audio data for reliability
    Some pyttsx3 backends don't respect the volume property, so we:
    1. Generate audio at full volume
    2. Load the WAV file
    3. Multiply audio data by volume (0.0 to 1.0)
    4. Play the scaled audio
    
    Args:
        text: Text to speak (will be cleaned automatically)
        engine: pyttsx3 engine instance (should be fresh per call)
        stop_event: Optional threading.Event to interrupt speech
        volume: Volume level (0.0 to 1.0, default 1.0)
        
    Returns:
        "Speech completed", "Interrupted", or "Error: <message>"
    """
    # Clean text using shared utility
    text = clean_text_for_tts(text)
    if not text:
        return "Error: No text after cleaning"

    temp_wav = None
    try:
        temp_wav = _get_temp_wav()
        volume_percent = int(volume * 100)
        logger.speech(f"Generating: {text[:70]}{'...' if len(text) > 70 else ''} (volume: {volume_percent}%)")

        # Generate WAV in a separate thread for interruptibility
        generation_done = threading.Event()
        generation_error = None

        def generate_wav(engine_to_use):
            """Generate WAV file using pyttsx3 at full volume"""
            nonlocal generation_error
            try:
                # Configure engine
                voices = engine_to_use.getProperty('voices')
                if 0 <= voiceIndex < len(voices):
                    engine_to_use.setProperty('voice', voices[voiceIndex].id)
                engine_to_use.setProperty('rate', 200)
                
                # Set engine to full volume for generation
                # (we'll scale the audio data afterward for reliable volume control)
                engine_to_use.setProperty('volume', 1.0)

                # Generate audio file at full volume
                engine_to_use.save_to_file(text, temp_wav)
                engine_to_use.runAndWait()
                
                # CRITICAL: DO NOT call engine.stop()!
                # The engine must stay running for the next call
                
                generation_done.set()
                
            except Exception as e_thread:
                generation_error = e_thread
                generation_done.set()

        # Start generation thread
        thread = threading.Thread(target=generate_wav, args=(engine,), daemon=True)
        thread.start()

        # Wait for generation with interruption support
        while not generation_done.is_set():
            if stop_event and stop_event.is_set():
                logger.speech("Generation interrupted")
                _cleanup_temp_file(temp_wav)
                return "Interrupted"
            generation_done.wait(0.1)

        if generation_error:
            raise generation_error

        if not os.path.exists(temp_wav):
            raise RuntimeError("WAV file was not created")

        # Check for interruption before playback
        if stop_event and stop_event.is_set():
            _cleanup_temp_file(temp_wav)
            return "Interrupted"

        # Load audio data
        data, samplerate = sf.read(temp_wav, dtype='float32')
        
        # CRITICAL FIX: Apply volume to audio data
        # This is more reliable than pyttsx3's volume property
        # Clamp volume to valid range (0.0 to 1.0)
        clamped_volume = max(0.0, min(1.0, volume))
        
        if clamped_volume < 1.0:
            # Scale audio data by volume
            data = data * clamped_volume
            
            # Ensure we don't clip
            data = np.clip(data, -1.0, 1.0)
            
            logger.audio(f"Audio scaled to {volume_percent}% volume")
        else:
            logger.audio(f"Playing at full volume")
        
        # Find VB-Cable using shared utility
        device = find_vb_cable_device()
        
        if device is None:
            logger.audio("VB-Cable not found, using default output")

        # Start playback with volume-adjusted audio
        sd.play(data, samplerate, device=device)
        logger.audio(f"Playing via {'VB-Cable' if device else 'default'}")

        # Wait for playback with interruption support
        while sd.get_stream().active:
            if stop_event and stop_event.is_set():
                logger.speech("Playback interrupted")
                sd.stop()
                return "Interrupted"
            sd.sleep(100)

        logger.speech("Speech completed")
        return "Speech completed"

    except Exception as e_main:
        logger.error(f"System TTS failed: {e_main}")
        return f"Error: {e_main}"
        
    finally:
        if temp_wav:
            _cleanup_temp_file(temp_wav)


def test_audio_setup():
    """
    Test and diagnose audio setup
    
    Returns:
        bool: True if VB-Cable found, False otherwise
    """
    logger.audio("=== Audio Setup Diagnosis ===")
    
    # List all devices using shared utility
    from BASE.tools.internal.voice.voice_utils import print_audio_devices
    print_audio_devices()
    
    # Try to find VB-Cable
    cable_index = find_vb_cable_device()
    
    if cable_index is not None:
        logger.success(f"[SUCCESS] VB-Cable found at index {cable_index}")
    else:
        logger.error("[FAILED] VB-Cable not found")
        logger.audio("\nTo fix this:")
        logger.audio("1. Install VB-Cable from: https://vb-audio.com/Cable/")
        logger.audio("2. Or install VoiceMeeter which includes virtual cables")
        logger.audio("3. Restart your application after installation")
    
    # Test pyttsx3
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        logger.success(f"[SUCCESS] pyttsx3 initialized with {len(voices)} voices")
        
        if voiceIndex < len(voices):
            logger.success(f"[SUCCESS] Voice index {voiceIndex} valid: {voices[voiceIndex].name}")
        else:
            logger.error(f"[FAILED] Voice index {voiceIndex} out of range (max: {len(voices)-1})")
        
        # Test volume property support
        try:
            current_vol = engine.getProperty('volume')
            engine.setProperty('volume', 0.5)
            test_vol = engine.getProperty('volume')
            logger.audio(f"Volume property test: {current_vol} -> {test_vol}")
            if abs(test_vol - 0.5) < 0.01:
                logger.success("[SUCCESS] Engine volume property works")
            else:
                logger.warning("[WARNING] Engine volume property unreliable, using audio data scaling")
        except:
            logger.warning("[WARNING] Engine volume property not supported, using audio data scaling")
        
        # Don't call engine.stop() - let it be garbage collected
        del engine
            
    except Exception as e:
        logger.error(f"[FAILED] pyttsx3 error: {e}")
    
    return cable_index is not None


# Example usage and testing
if __name__ == "__main__":
    # Run diagnosis
    test_audio_setup()
    
    # Test TTS with different volumes
    test_text = "Testing system voice volume control at different levels."
    logger.audio(f"\nTesting TTS with: '{test_text}'")
    
    for volume in [0.3, 0.5, 0.7, 1.0]:
        logger.audio(f"Testing at {int(volume * 100)}% volume")
        
        engine = pyttsx3.init()
        result = speak_system_voice(test_text, engine, volume=volume)
        logger.audio(f"Result: {result}")
        del engine
        
        import time
        time.sleep(2)  # Pause between tests