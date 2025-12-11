# Filename: BASE/interface/gui_themes.py
"""
Theme and color definitions for the GUI application.
"""

class DarkTheme:
    """Dark theme color definitions - Purple/Black modern theme"""
    LABEL = "#ffffff"
    BG_DARK = "#1e1e1e"          # Main dark background
    BG_DARKER = "#141414"        # Darker sections (panels)
    BG_LIGHTER = "#2a2a2a"       # Lighter sections (inputs)
    FG_PRIMARY = "#d4d4d4"       # Light gray text
    FG_SECONDARY = "#9a9a9a"     # Muted gray text
    FG_MUTED = "#6a6a6a"         # Very muted gray
    ACCENT_PURPLE = "#8b5cf6"    # Primary purple accent
    ACCENT_PURPLE_LIGHT = "#a78bfa"  # Lighter purple
    ACCENT_PURPLE_DARK = "#6d28d9"   # Darker purple
    ACCENT_BLUE = "#3b82f6"      # Blue accent for highlights
    ACCENT_GREEN = "#10b981"     # Green for ON states
    ACCENT_ORANGE = "#f59e0b"    # Orange/amber
    ACCENT_RED = "#ef4444"       # Red for errors/OFF
    ACCENT_YELLOW = "#fbbf24"    # Yellow warnings
    BORDER = "#2a2a2a"           # Border color
    BORDER_ACCENT = "#8b5cf6"    # Purple border for highlights
    BUTTON_BG = "#2a2a2a"        # Button background
    BUTTON_HOVER = "#3a3a3a"     # Button hover state

class LightTheme:
    """Light theme color definitions (for future use)"""
    LABEL = "#000000"
    BG_DARK = "#f8f9fa"
    BG_DARKER = "#e9ecef"
    BG_LIGHTER = "#ffffff"
    FG_PRIMARY = "#000000"
    FG_SECONDARY = "#6c757d"
    FG_MUTED = "#dc3545"
    ACCENT_BLUE = "#0d6efd"
    ACCENT_GREEN = "#198754"
    ACCENT_ORANGE = "#fd7e14"
    ACCENT_RED = "#dc3545"
    ACCENT_YELLOW = "#ffc107"
    BORDER = "#dee2e6"