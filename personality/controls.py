# Filename: personality/controls.py
"""
Dynamic control variables for AI functionality.
These variables can be modified at runtime to enable/disable features.
Control methods are available in BASE.core.control_methods
Change values in this file to set defaults at startup.

REFACTORED: Simplified continuous thinking configuration
"""

# === SYSTEM EXECUTIONS ===

# === MASTER CONTROLS ===

LIMIT_PROCESSING = False # Enable for slower agent processing and responses
DELAY_TIMER = 10  # Timeout for prompt processing (seconds)

# === EMERGENCY STOP ===
# Global kill switch to immediately halt all agent operations
# If encountered in input from any source, the agent will cease all actions
# This should be a string that is unlikely to be used in normal conversation,
# appear in search results, etc. Recommended: Something easy to speak when using voice input.
KILL_COMMAND = "shut down sleep now"

# === CONTINUOUS AUTONOMOUS THINKING ===
# Single system for all background cognitive processing
# Handles reactive (responding to events) and proactive (self-initiated) thinking

ENABLE_CONTINUOUS_THINKING = False  # Master toggle for autonomous cognitive loop

CHAT_ENGAGEMENT = False

# Thinking pace configuration
MIN_PROACTIVE_INTERVAL = 5.0   # Minimum seconds between self-initiated thoughts
MAX_PROACTIVE_INTERVAL = 15.0  # Force a thought after this much silence
MAX_CONSECUTIVE_PROACTIVE = 200 # Max autonomous thoughts before needing external input

# === AUTO-RESPONSE (GUI/CLI specific) ===
# Separate from continuous thinking - this is for explicit user-facing responses
AUTO_RESPOND = False              # Enable automatic responses when no user input detected
AUTO_RESPOND_INTERVAL = 60        # Time interval (seconds) to trigger auto-response

# === VOLUME CONTROLS ===
VOICE_VOLUME = 1.0              # Set TTS voice volume (1.0 = 100%)
SOUND_EFFECT_VOLUME = 1.0       # Set sound effects volume (1.0 = 100%)

# === CORE TOOLS ===
# USE_SEARCH = False              # Enable web search functionality
# MAX_SEARCH_RESULTS = 1          # Max web search results to include
# USE_VISION = False              # Enable computer vision/screenshot analysis
# USE_CODING = False              # Enable VS Code extension integration for code editing
# USE_GOALS = False               # Enable goal-oriented behavior
# AI_TOOLS = False                 # Enable AI tool usage (web search, vision, coding). False uses trigger words only.   

# === MEMORY CONTEXT ===
USE_BASE_MEMORY = False         # Use BASE memory system (document embeddings)
USE_LONG_MEMORY = False         # Use long-term memory context (embedded conversation summaries of past days)
USE_SHORT_MEMORY = False        # Use short-term memory context (No embeddings, today's conversation entries)

# === PROMPT COMPONENTS ===
USE_SYSTEM_PROMPT = False       # Include system/personality prompt

# === MEMORY MANAGEMENT ===
SAVE_MEMORY = False             # Save conversations to memory system
MEMORY_LENGTH = 25             # Number of recent interactions to keep
MAX_LONG_TERM_MEMORIES = 1
MAX_BASE_MEMORIES = 1

# Reminder System
# USE_REMINDERS = False           # Enable reminder/timer functionality
# REMINDER_CHECK_INTERVAL = 600  # Seconds between reminder checks
# REMINDER_PROACTIVE_MENTION = False  # Mention upcoming reminders naturally


# === AVATAR ABILITIES ===
# AVATAR_ANIMATIONS = False       # Trigger avatar animations from responses
AVATAR_SPEECH = False           # Enable text-to-speech output
USE_CUSTOM_VOICE = False       # Use custom voice model instead of standard system TTS (requires AVATAR_SPEECH enabled)

# # Sound Effects
# USE_SOUND_EFFECTS = False
# SOUND_EFFECTS_DIR = "./BASE/tools/sounds/effects"  # Path to your .mp3 files

# === GROUP CHAT CONTEXT ===
IN_DISCORD_CHAT = False        # Enable Discord chat integration
IN_YOUTUBE_CHAT = False        # Include YouTube chat context
IN_TWITCH_CHAT = False         # Include Twitch chat context

# === TWITCH SPECIFIC ===
TWITCH_CHANNEL = ""            # Twitch channel to monitor (e.g., "shroud")
TWITCH_OAUTH_TOKEN = ""        # OAuth token for authenticated mode (optional)
TWITCH_NICKNAME = ""           # Bot nickname for Twitch (optional, uses justinfan if empty)
TWITCH_SEND_MESSAGES = False   # Enable sending messages to Twitch chat
TWITCH_MESSAGE_COOLDOWN = 3    # Cooldown between messages (seconds)
TWITCH_LOG_MESSAGES = False     # Log Twitch chat messages for debugging

# === DISCORD SPECIFIC ===
DISCORD_RESPOND_TO_MENTIONS = False    # Respond when bot is mentioned
DISCORD_RESPOND_TO_REPLIES = False     # Respond when messages reply to bot
DISCORD_RESPOND_TO_DMS = False         # Respond to direct messages
DISCORD_RESPOND_IN_THREADS = False     # Respond in thread conversations
DISCORD_AUTO_REACT = False            # Automatically react to messages
DISCORD_TYPING_INDICATOR = False       # Show typing indicator while generating response
DISCORD_MESSAGE_HISTORY_LIMIT = 10    # Number of previous messages to include as context
DISCORD_MAX_MESSAGE_LENGTH = 2000     # Maximum message length (Discord limit)
DISCORD_SPLIT_LONG_MESSAGES = False    # Split messages longer than max length
DISCORD_INCLUDE_EMBEDS = False        # Include embed content in context
DISCORD_INCLUDE_ATTACHMENTS = False    # Process message attachments (images, files)
DISCORD_COMMAND_COOLDOWN = 3          # Cooldown between commands (seconds)
DISCORD_LOG_MESSAGES = False           # Log Discord messages for debugging

# === CODING SPECIFIC ===
CODING_SERVER_URL = "http://localhost:3000"  # VS Code extension server URL
CODING_TIMEOUT = 30            # Timeout for coding requests (seconds)

# === OUTPUT ACTIONS ===
ENABLE_CONTENT_FILTER = False  # Enable content filtering for responses
USE_AI_CONTENT_FILTER = False  # Use AI model for semantic content analysis

# Game State - Master Control (automatically managed by control system)
PLAYING_GAME = False  # Auto-set to True when ANY game is selected

# Individual Game Controls (only one can be True at a time)
PLAYING_MINECRAFT = False
PLAYING_LEAGUE = False
# PLAYING_VALORANT = False  # Future games

# === INTELLIGENT TOOL USE ===
INTELLIGENT_TOOL_SELECTION = False
USE_AI_TOOL_VERIFICATION = False
TOOL_SELECTION_THRESHOLD = 0.3

# Content Filtering
ENABLE_CONTENT_FILTER = False  # Master toggle
USE_AI_CONTENT_FILTER = False  # AI semantic check (slower)
CONTENT_FILTER_INCOMING = False  # Filter all incoming data
CONTENT_FILTER_OUTGOING = False  # Filter all outgoing responses
CONTENT_FILTER_CONTEXT = False  # Filter context in prompts

# === DEBUGGING AND LOGGING ===
LOG_TOOL_EXECUTION = False      # Log tool usage details and all tool returns
LOG_PROMPT_CONSTRUCTION = False  # Log complete constructed user prompts
LOG_RESPONSE_PROCESSING = False  # Log complete agent responses (entire response, before extracting direct response)
LOG_SYSTEM_INFORMATION = False # Log all default system information not included in a different category
SHOW_CHAT = False              # Choose if chat messages from live chat are printed to output

LOG_CODING_EXECUTION = False     # Log coding tool operations
LOG_DISCORD_EXECUTION = False    # Log Discord-specific operations

LOG_MINECRAFT_EXECUTION = False  # Log Minecraft-specific operations
# Note: Control methods (toggle_feature, set_feature, etc.) are available in:
# from BASE.core.control_methods import ControlManager