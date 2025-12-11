# Filename: BASE/interface/coding_panel_manager.py
"""
Coding Panel Manager - FIXED for new tool system
REMOVED: tool_orchestrator references (old system)
UPDATED: Uses tool_execution_manager to check coding tool availability
"""
import tkinter as tk
from tkinter import ttk
from BASE.interface.gui_themes import DarkTheme
from typing import Optional


class CodingPanelManager:
    """Manages the coding integration panel in the GUI"""
    
    def __init__(self, ai_core, logger):
        """
        Initialize coding panel manager
        
        Args:
            ai_core: AI Core instance
            logger: Logger instance
        """
        self.ai_core = ai_core
        self.logger = logger
        
        # self.tool_orch = ai_core.tool_orchestrator (old system)
        
        # GUI components
        self.coding_status_label = None
        self.test_button = None
        self.connect_button = None
        self.manual_edit_frame = None
        self.instruction_entry = None
        self.send_instruction_button = None
    
    def create_coding_panel(self, parent_frame):
        """Create coding tool control panel"""
        coding_frame = ttk.LabelFrame(
            parent_frame, text="Coding Tool (VS Code)", style="Accent.TLabelframe"
        )
        coding_frame.pack(fill=tk.X, pady=(5, 0))

        # Status display
        status_frame = ttk.Frame(coding_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.coding_status_label = tk.Label(
            status_frame,
            text="Status: Unknown",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_MUTED,
            background=DarkTheme.BG_DARKER,
            anchor="w",
        )
        self.coding_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Control buttons
        button_frame = ttk.Frame(coding_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.test_button = ttk.Button(
            button_frame, text="Test", command=self.test_connection, width=10
        )
        self.test_button.pack(side=tk.LEFT, padx=(0, 5))

        refresh_button = ttk.Button(
            button_frame, text="Refresh", command=self.check_status, width=10
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))

        # Manual edit section (collapsible)
        manual_frame = ttk.LabelFrame(
            coding_frame, text="Manual Edit", style="Dark.TLabelframe"
        )
        manual_frame.pack(fill=tk.X, padx=5, pady=(5, 5))

        instruction_label = tk.Label(
            manual_frame,
            text="Instruction:",
            font=("Segoe UI", 9),
            foreground=DarkTheme.FG_PRIMARY,
            background=DarkTheme.BG_DARKER,
        )
        instruction_label.pack(anchor="w", padx=5, pady=(5, 2))

        self.instruction_entry = tk.Text(
            manual_frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg=DarkTheme.BG_LIGHTER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.FG_PRIMARY,
            borderwidth=0,
            highlightthickness=0
        )
        self.instruction_entry.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.send_instruction_button = ttk.Button(
            manual_frame,
            text="Send to VS Code",
            command=self.send_manual_instruction,
            width=15,
        )
        self.send_instruction_button.pack(pady=(0, 5))

        # Initial status check
        self.check_status()
    
    def check_status(self):
        """Check and update coding tool status - UPDATED for new system"""
        try:
            # Check if coding tool is enabled via controls
            if not getattr(self.ai_core.controls, 'USE_CODING', False):
                if self.coding_status_label:
                    self.coding_status_label.config(
                        text="Status: Not initialized (enable USE_CODING)",
                        foreground=DarkTheme.FG_MUTED,
                    )
                self._disable_controls()
                return

            # Check via tool_execution_manager
            if not hasattr(self.ai_core, 'tool_execution_manager'):
                if self.coding_status_label:
                    self.coding_status_label.config(
                        text="Status: Tool system not ready",
                        foreground=DarkTheme.FG_MUTED,
                    )
                self._disable_controls()
                return
            
            tool_manager = self.ai_core.tool_execution_manager
            
            # Check if coding tool is registered and enabled
            if not tool_manager.is_tool_enabled('coding'):
                if self.coding_status_label:
                    self.coding_status_label.config(
                        text="Status: Not enabled",
                        foreground=DarkTheme.FG_MUTED,
                    )
                self._disable_controls()
                return
            
            # Try to get tool status
            status = tool_manager.get_tool_status('coding')
            
            if status and status.get('available', False):
                if self.coding_status_label:
                    self.coding_status_label.config(
                        text="Status: Connected to VS Code",
                        foreground=DarkTheme.ACCENT_GREEN,
                    )
                self._enable_controls()
                self.logger.tool("[SUCCESS] Coding tool: Connected to VS Code extension")
            else:
                if self.coding_status_label:
                    self.coding_status_label.config(
                        text="Status: VS Code not responding",
                        foreground=DarkTheme.ACCENT_RED,
                    )
                self._enable_controls()  # Still enable for testing
                self.logger.warning("[WARNING] Coding tool: VS Code extension not responding")

        except Exception as e:
            if self.coding_status_label:
                self.coding_status_label.config(
                    text=f"Status: Error - {str(e)}",
                    foreground=DarkTheme.ACCENT_RED,
                )
            self._disable_controls()
            self.logger.error(f"Coding tool error: {e}")

    def test_connection(self):
        """Test the coding tool connection - UPDATED for new system"""
        try:
            if not hasattr(self.ai_core, 'tool_execution_manager'):
                self.logger.warning("Tool execution manager not available")
                return
            
            tool_manager = self.ai_core.tool_execution_manager
            
            if not tool_manager.is_tool_enabled('coding'):
                self.logger.warning("Coding tool not enabled")
                return

            self.logger.tool("Testing VS Code extension connection...")
            if self.test_button:
                self.test_button.config(state=tk.DISABLED)

            # Test availability via tool manager
            status = tool_manager.get_tool_status('coding')
            
            if status and status.get('available', False):
                self.logger.success("[SUCCESS] Connection test successful!")
                self.check_status()
            else:
                self.logger.error("Connection test failed - server not responding")

        except Exception as e:
            self.logger.error(f"Connection test error: {e}")
        finally:
            if self.test_button:
                self.test_button.config(state=tk.NORMAL)

    def send_manual_instruction(self):
        """Send a manual coding instruction to VS Code - UPDATED for new system"""
        try:
            if not hasattr(self.ai_core, 'tool_execution_manager'):
                self.logger.warning("Tool execution manager not available")
                return
            
            tool_manager = self.ai_core.tool_execution_manager
            
            if not tool_manager.is_tool_enabled('coding'):
                self.logger.warning("Coding tool not enabled")
                return

            if not self.instruction_entry:
                self.logger.error("Instruction entry not available")
                return

            instruction = self.instruction_entry.get("1.0", tk.END).strip()

            if not instruction:
                return

            self.logger.tool(f"📤 Sending instruction to VS Code: {instruction}")
            if self.send_instruction_button:
                self.send_instruction_button.config(state=tk.DISABLED)

            # NOTE: Direct instruction sending would need to be implemented
            # via the coding tool interface. For now, this is a placeholder.
            # The actual implementation depends on your coding tool's interface.
            
            # TODO: Implement direct instruction sending via tool_execution_manager
            # This might require adding a method to get the tool instance directly
            # or implementing a send_instruction method in the tool manager
            
            self.logger.warning("Direct instruction sending not yet implemented in new system")
            self.logger.info("Use the agent's natural language interface instead")

        except Exception as e:
            self.logger.error(f"Error sending instruction: {e}")
        finally:
            if self.send_instruction_button:
                self.send_instruction_button.config(state=tk.NORMAL)

    def _enable_controls(self):
        """Enable all control buttons"""
        if self.test_button:
            self.test_button.config(state=tk.NORMAL)
        if self.send_instruction_button:
            self.send_instruction_button.config(state=tk.NORMAL)

    def _disable_controls(self):
        """Disable all control buttons"""
        if self.test_button:
            self.test_button.config(state=tk.DISABLED)
        if self.send_instruction_button:
            self.send_instruction_button.config(state=tk.DISABLED)