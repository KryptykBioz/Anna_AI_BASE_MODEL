# ============================================================================
# Filename: BASE/tools/internal/voice/voice_utils.py
# ============================================================================
"""
Shared voice utilities for TTS backends

Common functions used by both XTTS and pyttsx3 backends:
- VB-Cable device detection
- Text cleaning and normalization
- Audio device queries
"""
import re
import sounddevice as sd
from typing import Optional, List, Tuple


def find_vb_cable_device() -> Optional[int]:
    """
    Find VB-Cable or similar virtual audio device
    
    Searches for common virtual audio cable patterns:
    - CABLE Input
    - VB-Audio Virtual Cable
    - VoiceMeeter Input
    
    Returns:
        Optional[int]: Device index if found, None otherwise
    """
    devices = sd.query_devices()
    
    cable_patterns = [
        "CABLE Input",
        "VB-Audio Virtual Cable", 
        "Virtual Cable",
        "CABLE-A Input",
        "CABLE-B Input",
        "VoiceMeeter Input",
        "VoiceMeeter Aux Input"
    ]
    
    for i, device in enumerate(devices):
        device_name = device['name']
        # Only consider output devices
        if device['max_output_channels'] > 0:
            for pattern in cable_patterns:
                if pattern.lower() in device_name.lower():
                    print(f"[VoiceUtils] Found VB-Cable: [{i}] {device_name}")
                    return i
    
    print("[VoiceUtils] VB-Cable not found")
    return None


def list_audio_devices() -> List[dict]:
    """
    List all available audio devices
    
    Returns:
        List of device info dictionaries
    """
    devices = sd.query_devices()
    device_list = []
    
    for i, device in enumerate(devices):
        device_info = {
            'index': i,
            'name': device['name'],
            'max_output_channels': device['max_output_channels'],
            'max_input_channels': device['max_input_channels']
        }
        device_list.append(device_info)
    
    return device_list


def print_audio_devices():
    """Print all audio devices for debugging"""
    devices = list_audio_devices()
    print("\n=== Available Audio Devices ===")
    for device in devices:
        device_str = f"[{device['index']}] {device['name']}"
        if device['max_output_channels'] > 0:
            device_str += " (Output)"
        if device['max_input_channels'] > 0:
            device_str += " (Input)"
        print(device_str)
    print("===============================\n")


def remove_emoji(text: str) -> str:
    """
    Remove emoji characters from text
    
    Args:
        text: Input text potentially containing emojis
        
    Returns:
        Text with emojis removed
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)


def remove_action_text(text: str) -> str:
    """
    Remove text enclosed in asterisks (*smiles*, *waves*, etc.)
    
    Args:
        text: Input text potentially containing action text
        
    Returns:
        Text with action text removed
    """
    return re.sub(r'\*[^*]*\*', '', text)


def normalize_names(text: str) -> str:
    """
    Normalize name variants to consistent format
    
    Args:
        text: Input text with potential name variations
        
    Returns:
        Text with normalized names
    """
    # Add name normalizations as needed
    text = text.replace('kryptyk', 'Cryptic')
    text = text.replace('Kryptyk', 'Cryptic')
    text = text.replace('KRYPTYK', 'Cryptic')
    return text


def clean_text_for_tts(text: str) -> str:
    """
    Clean and normalize text for TTS processing
    
    Performs:
    - Emoji removal
    - Action text removal (*action*)
    - Name normalization
    - Whitespace cleanup
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text ready for TTS
    """
    # Remove emojis
    text = remove_emoji(text)
    
    # Remove action text
    text = remove_action_text(text)
    
    # Normalize names
    text = normalize_names(text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove underscores
    text = re.sub(r'_', ' ', text)
    
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for streaming TTS
    
    Splits on .!? followed by space, newline, or end of string
    Preserves punctuation with sentences
    
    Args:
        text: Text to split
        
    Returns:
        List of sentence strings
    """
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # If no sentences detected (no punctuation), treat entire text as one sentence
    if not sentences:
        sentences = [text]
    
    return sentences


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate that an audio file exists and is readable
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Tuple of (is_valid, message)
    """
    from pathlib import Path
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    if not path.is_file():
        return False, f"Not a file: {file_path}"
    
    # Check file extension
    valid_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
    if path.suffix.lower() not in valid_extensions:
        return False, f"Invalid audio format: {path.suffix}"
    
    return True, "Valid audio file"


# Diagnostic function
def diagnose_audio_setup() -> dict:
    """
    Run diagnostic checks on audio setup
    
    Returns:
        Dict with diagnostic results
    """
    results = {
        'vb_cable_found': False,
        'vb_cable_index': None,
        'total_devices': 0,
        'output_devices': 0,
        'input_devices': 0
    }
    
    # Check VB-Cable
    vb_cable_index = find_vb_cable_device()
    results['vb_cable_found'] = vb_cable_index is not None
    results['vb_cable_index'] = vb_cable_index
    
    # Count devices
    devices = list_audio_devices()
    results['total_devices'] = len(devices)
    results['output_devices'] = sum(1 for d in devices if d['max_output_channels'] > 0)
    results['input_devices'] = sum(1 for d in devices if d['max_input_channels'] > 0)
    
    return results