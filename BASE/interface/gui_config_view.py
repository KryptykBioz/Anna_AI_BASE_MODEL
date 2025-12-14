# Filename: BASE/interface/gui_config_view.py
"""
Configuration editor view for bot_info.py and personality_prompt_parts.py
Allows live editing and saving of configuration files
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import re
from BASE.interface.gui_themes import DarkTheme

class ConfigView:
    """Displays and allows editing of configuration files"""
    
    def __init__(self, parent, project_root):
        self.parent = parent
        self.project_root = Path(project_root)
        self.bot_info_path = self.project_root / "personality" / "bot_info.py"
        self.personality_path = self.project_root / "personality" / "prompts" / "personality_prompt_parts.py"
        
    def create_config_view(self):
        """Create the configuration editor view"""
        config_frame = self.parent.config_view
        
        # Create header
        header_frame = tk.Frame(config_frame, bg=DarkTheme.BG_DARKER, height=50)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="⚙️ Configuration Editor",
            font=("Segoe UI", 14, "bold"),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Warning label
        warning_label = tk.Label(
            header_frame,
            text="⚠️ Restart required after saving changes",
            font=("Segoe UI", 9, "italic"),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.ACCENT_ORANGE
        )
        warning_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Create main container with two sections using PanedWindow for responsive resizing
        main_container = ttk.PanedWindow(config_frame, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for bot_info
        left_panel = tk.Frame(main_container, bg=DarkTheme.BG_DARK)
        main_container.add(left_panel, weight=1)
        
        # Right panel for personality
        right_panel = tk.Frame(main_container, bg=DarkTheme.BG_DARK)
        main_container.add(right_panel, weight=1)
        
        # Create bot info editor (left side)
        self.create_bot_info_editor(left_panel)
        
        # Create personality editor (right side)
        self.create_personality_editor(right_panel)
        
    def create_bot_info_editor(self, parent):
        """Create editor for bot_info.py"""
        # Section header
        header_frame = tk.Frame(parent, bg=DarkTheme.BG_DARKER, height=40)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="🤖 Bot Information (bot_info.py)",
            font=("Segoe UI", 12, "bold"),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.ACCENT_BLUE
        )
        title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Button frame
        btn_frame = tk.Frame(header_frame, bg=DarkTheme.BG_DARKER)
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Reload",
            command=self.load_bot_info,
            width=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        save_btn = ttk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_bot_info,
            width=10
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Text editor
        editor_frame = tk.Frame(parent, bg=DarkTheme.BG_DARK)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.bot_info_text = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,  # No wrapping for code
            font=("Consolas", 10),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.ACCENT_GREEN,
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0,
            undo=True,
            maxundo=-1
        )
        self.bot_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting
        self.configure_python_syntax(self.bot_info_text)
        
        # Load initial content
        self.load_bot_info()
        
    def create_personality_editor(self, parent):
        """Create editor for personality_prompt_parts.py"""
        # Section header
        header_frame = tk.Frame(parent, bg=DarkTheme.BG_DARKER, height=40)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame,
            text="💬 Personality Prompt (personality_prompt_parts.py)",
            font=("Segoe UI", 12, "bold"),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.ACCENT_PURPLE
        )
        title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Button frame
        btn_frame = tk.Frame(header_frame, bg=DarkTheme.BG_DARKER)
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Reload",
            command=self.load_personality,
            width=10
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        save_btn = ttk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_personality,
            width=10
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Text editor
        editor_frame = tk.Frame(parent, bg=DarkTheme.BG_DARK)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.personality_text = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,  # No wrapping for code
            font=("Consolas", 10),
            bg=DarkTheme.BG_DARKER,
            fg=DarkTheme.FG_PRIMARY,
            insertbackground=DarkTheme.ACCENT_GREEN,
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=0,
            undo=True,
            maxundo=-1
        )
        self.personality_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure syntax highlighting
        self.configure_python_syntax(self.personality_text)
        
        # Load initial content
        self.load_personality()
        
    def configure_python_syntax(self, text_widget):
        """Configure basic Python syntax highlighting"""
        # Keywords
        text_widget.tag_configure(
            "keyword",
            foreground=DarkTheme.ACCENT_PURPLE,
            font=("Consolas", 10, "bold")
        )
        
        # Strings
        text_widget.tag_configure(
            "string",
            foreground=DarkTheme.ACCENT_GREEN
        )
        
        # Comments
        text_widget.tag_configure(
            "comment",
            foreground=DarkTheme.FG_MUTED,
            font=("Consolas", 10, "italic")
        )
        
        # Numbers
        text_widget.tag_configure(
            "number",
            foreground=DarkTheme.ACCENT_ORANGE
        )
        
        # Functions
        text_widget.tag_configure(
            "function",
            foreground=DarkTheme.ACCENT_BLUE
        )
        
    def apply_syntax_highlighting(self, text_widget):
        """Apply syntax highlighting to the text widget content"""
        content = text_widget.get(1.0, tk.END)
        
        # Remove existing tags
        for tag in ["keyword", "string", "comment", "number", "function"]:
            text_widget.tag_remove(tag, 1.0, tk.END)
        
        # Python keywords
        keywords = [
            "def", "class", "import", "from", "return", "if", "else", "elif",
            "for", "while", "in", "is", "not", "and", "or", "True", "False",
            "None", "try", "except", "finally", "with", "as", "raise", "pass",
            "break", "continue", "lambda", "yield", "global", "nonlocal"
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Comments
            if '#' in line:
                comment_start = line.index('#')
                start_idx = f"{i}.{comment_start}"
                end_idx = f"{i}.{len(line)}"
                text_widget.tag_add("comment", start_idx, end_idx)
            
            # Keywords
            for keyword in keywords:
                pattern = r'\b' + keyword + r'\b'
                for match in re.finditer(pattern, line):
                    start_idx = f"{i}.{match.start()}"
                    end_idx = f"{i}.{match.end()}"
                    text_widget.tag_add("keyword", start_idx, end_idx)
            
            # Strings (simple detection)
            for match in re.finditer(r'["\'].*?["\']', line):
                start_idx = f"{i}.{match.start()}"
                end_idx = f"{i}.{match.end()}"
                text_widget.tag_add("string", start_idx, end_idx)
            
            # Triple-quoted strings
            for match in re.finditer(r'""".*?"""', line, re.DOTALL):
                start_idx = f"{i}.{match.start()}"
                end_idx = f"{i}.{match.end()}"
                text_widget.tag_add("string", start_idx, end_idx)
            
            # Numbers
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start_idx = f"{i}.{match.start()}"
                end_idx = f"{i}.{match.end()}"
                text_widget.tag_add("number", start_idx, end_idx)
            
            # Function definitions
            for match in re.finditer(r'def\s+(\w+)', line):
                start_idx = f"{i}.{match.start(1)}"
                end_idx = f"{i}.{match.end(1)}"
                text_widget.tag_add("function", start_idx, end_idx)
        
    def load_bot_info(self):
        """Load bot_info.py content"""
        try:
            if not self.bot_info_path.exists():
                self.show_error(
                    self.bot_info_text,
                    f"File not found:\n{self.bot_info_path}"
                )
                return
            
            with open(self.bot_info_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.bot_info_text.delete(1.0, tk.END)
            self.bot_info_text.insert(1.0, content)
            
            # Apply syntax highlighting
            self.apply_syntax_highlighting(self.bot_info_text)
            
            self.parent.logger.system("Loaded bot_info.py")
            
        except Exception as e:
            self.show_error(
                self.bot_info_text,
                f"Error loading bot_info.py:\n{str(e)}"
            )
            self.parent.logger.error(f"Error loading bot_info.py: {e}")
    
    def load_personality(self):
        """Load personality_prompt_parts.py content"""
        try:
            if not self.personality_path.exists():
                self.show_error(
                    self.personality_text,
                    f"File not found:\n{self.personality_path}"
                )
                return
            
            with open(self.personality_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.personality_text.delete(1.0, tk.END)
            self.personality_text.insert(1.0, content)
            
            # Apply syntax highlighting
            self.apply_syntax_highlighting(self.personality_text)
            
            self.parent.logger.system("Loaded personality_prompt_parts.py")
            
        except Exception as e:
            self.show_error(
                self.personality_text,
                f"Error loading personality_prompt_parts.py:\n{str(e)}"
            )
            self.parent.logger.error(f"Error loading personality_prompt_parts.py: {e}")
    
    def save_bot_info(self):
        """Save bot_info.py content"""
        try:
            # Confirm save
            result = messagebox.askyesno(
                "Save Bot Info",
                "Save changes to bot_info.py?\n\n"
                "⚠️ Application restart required for changes to take effect.",
                icon='warning'
            )
            
            if not result:
                return
            
            content = self.bot_info_text.get(1.0, tk.END)
            
            # Validate Python syntax
            try:
                compile(content, self.bot_info_path.name, 'exec')
            except SyntaxError as e:
                messagebox.showerror(
                    "Syntax Error",
                    f"Python syntax error on line {e.lineno}:\n{e.msg}\n\n"
                    "Please fix the error before saving."
                )
                return
            
            # Create backup
            backup_path = self.bot_info_path.with_suffix('.py.bak')
            if self.bot_info_path.exists():
                import shutil
                shutil.copy2(self.bot_info_path, backup_path)
                self.parent.logger.system(f"Created backup: {backup_path.name}")
            
            # Save file
            with open(self.bot_info_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.parent.logger.system("✅ Saved bot_info.py")
            
            messagebox.showinfo(
                "Saved",
                "bot_info.py saved successfully!\n\n"
                "🔄 Please restart the application for changes to take effect."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save bot_info.py:\n{str(e)}"
            )
            self.parent.logger.error(f"Error saving bot_info.py: {e}")
    
    def save_personality(self):
        """Save personality_prompt_parts.py content"""
        try:
            # Confirm save
            result = messagebox.askyesno(
                "Save Personality",
                "Save changes to personality_prompt_parts.py?\n\n"
                "⚠️ Application restart required for changes to take effect.",
                icon='warning'
            )
            
            if not result:
                return
            
            content = self.personality_text.get(1.0, tk.END)
            
            # Validate Python syntax
            try:
                compile(content, self.personality_path.name, 'exec')
            except SyntaxError as e:
                messagebox.showerror(
                    "Syntax Error",
                    f"Python syntax error on line {e.lineno}:\n{e.msg}\n\n"
                    "Please fix the error before saving."
                )
                return
            
            # Create backup
            backup_path = self.personality_path.with_suffix('.py.bak')
            if self.personality_path.exists():
                import shutil
                shutil.copy2(self.personality_path, backup_path)
                self.parent.logger.system(f"Created backup: {backup_path.name}")
            
            # Save file
            with open(self.personality_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.parent.logger.system("✅ Saved personality_prompt_parts.py")
            
            messagebox.showinfo(
                "Saved",
                "personality_prompt_parts.py saved successfully!\n\n"
                "🔄 Please restart the application for changes to take effect."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save personality_prompt_parts.py:\n{str(e)}"
            )
            self.parent.logger.error(f"Error saving personality_prompt_parts.py: {e}")
    
    def show_error(self, text_widget, message):
        """Display error message in the text widget"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, f"❌ ERROR\n\n{message}")
        text_widget.tag_add("comment", 1.0, tk.END)