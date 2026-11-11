"""
Markdown Viewer Module for n8n Control Center Pro.
Provides an integrated in-app reading experience for course guides
and a styled HTML browser viewer that bypasses default OS associations like Calibre.
"""

from __future__ import annotations

import html
import re
import webbrowser
from pathlib import Path
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

try:
    import markdown
except ImportError:
    markdown = None

# Styling constants matching main app
COLOR_BG = "#0f111a"
COLOR_SIDEBAR = "#161824"
COLOR_CARD = "#1c1e2e"
COLOR_CARD_BORDER = "#2b2e44"
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_ACCENT = "#ea580c"
COLOR_ACCENT_HOVER = "#c2410c"
COLOR_PRIMARY_BLUE = "#3b82f6"
COLOR_PRIMARY_BLUE_HOVER = "#2563eb"
COLOR_SUCCESS = "#10b981"


def render_markdown_to_html(md_content: str, title: str = "Guía de Estudio") -> str:
    """Renders markdown into a self-contained, beautifully styled dark HTML document."""
    body_html = ""
    if markdown:
        body_html = markdown.markdown(
            md_content,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
    else:
        # Fallback simple converter if markdown package is absent
        escaped = html.escape(md_content)
        body_html = f"<pre style='white-space: pre-wrap;'>{escaped}</pre>"

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - n8n Academia</title>
    <style>
        :root {{
            --bg: #0f111a;
            --card-bg: #161824;
            --border: #2b2e44;
            --text-primary: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #ea580c;
            --blue: #38bdf8;
            --code-bg: #0b0c13;
            --quote-border: #f59e0b;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.65;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 40px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        h1, h2, h3, h4 {{
            color: var(--text-primary);
            font-weight: 700;
            margin-top: 1.5em;
            margin-bottom: 0.6em;
            line-height: 1.3;
        }}
        h1 {{
            font-size: 2rem;
            color: var(--blue);
            border-bottom: 2px solid var(--border);
            padding-bottom: 12px;
            margin-top: 0;
        }}
        h2 {{
            font-size: 1.5rem;
            color: #60a5fa;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}
        h3 {{
            font-size: 1.25rem;
            color: #93c5fd;
        }}
        p {{
            margin-bottom: 1.2em;
            color: #e2e8f0;
        }}
        a {{
            color: var(--blue);
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul, ol {{
            margin-bottom: 1.2em;
            padding-left: 28px;
            color: #e2e8f0;
        }}
        li {{
            margin-bottom: 0.4em;
        }}
        pre {{
            background: var(--code-bg);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 1.4em;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 0.92rem;
            color: #38bdf8;
        }}
        code {{
            background: #1e2235;
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 0.9em;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}
        blockquote {{
            border-left: 4px solid var(--quote-border);
            padding: 12px 18px;
            background: rgba(245, 158, 11, 0.08);
            border-radius: 0 8px 8px 0;
            margin-bottom: 1.4em;
            color: #fde68a;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5em;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #1e2235;
            color: var(--blue);
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background: rgba(255, 255, 255, 0.02);
        }}
        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 2em 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            font-size: 0.85rem;
            color: var(--text-muted);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
        <div class="footer">
            n8n Control Center Pro • Academia Vibe Coding • Documentación Local
        </div>
    </div>
</body>
</html>
"""
    return full_html


def open_markdown_in_browser(file_path: Path, title: str = "") -> None:
    """Compiles markdown file to styled HTML and opens it directly in the default web browser."""
    if not file_path.exists():
        return

    content = file_path.read_text(encoding="utf-8")
    display_title = title or file_path.stem.replace("_", " ")

    cache_dir = file_path.parent / ".html_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    html_file = cache_dir / f"{file_path.stem}.html"
    rendered = render_markdown_to_html(content, title=display_title)
    html_file.write_text(rendered, encoding="utf-8")

    webbrowser.open(html_file.as_uri())


class MarkdownViewerWindow(ctk.CTkToplevel):
    """Integrated in-app popup window for reading Markdown course guides."""

    def __init__(self, parent: ctk.CTk, file_path: Path, title: str = ""):
        super().__init__(parent)

        self.file_path = file_path
        self.doc_title = title or file_path.stem.replace("_", " ")

        self.title(f"🎓 Academia: {self.doc_title}")
        self.geometry("940x740")
        self.minsize(750, 520)
        self.configure(fg_color=COLOR_BG)

        # Ensure top window focus
        self.after(100, self.lift)
        self.after(150, self.focus_force)

        self._build_ui()
        self._load_and_display_markdown()

    def _build_ui(self):
        # Header toolbar
        toolbar = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=0, height=60)
        toolbar.pack(fill="x", side="top")

        left_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_frame.pack(side="left", padx=16, pady=10)

        icon_lbl = ctk.CTkLabel(
            left_frame,
            text="🎓",
            font=ctk.CTkFont(size=20),
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = ctk.CTkLabel(
            left_frame,
            text=self.doc_title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left")

        # Action Buttons on right
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=16, pady=10)

        btn_browser = ctk.CTkButton(
            right_frame,
            text="🌐 Ver en Navegador (HTML)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_BLUE_HOVER,
            width=180,
            height=32,
            corner_radius=8,
            command=self._open_in_browser,
        )
        btn_browser.pack(side="left", padx=6)

        btn_copy = ctk.CTkButton(
            right_frame,
            text="📋 Copiar",
            font=ctk.CTkFont(size=12),
            fg_color="#2b2f44",
            hover_color="#373c57",
            width=80,
            height=32,
            corner_radius=8,
            command=self._copy_content,
        )
        btn_copy.pack(side="left", padx=6)

        btn_close = ctk.CTkButton(
            right_frame,
            text="Cerrar",
            font=ctk.CTkFont(size=12),
            fg_color="#374151",
            hover_color="#4b5563",
            width=75,
            height=32,
            corner_radius=8,
            command=self.destroy,
        )
        btn_close.pack(side="left", padx=(6, 0))

        # Main text viewer
        content_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        content_frame.pack(fill="both", expand=True, padx=16, pady=14)

        self.txt_view = ctk.CTkTextbox(
            content_frame,
            fg_color=COLOR_CARD,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            wrap="word",
            corner_radius=10,
            border_color=COLOR_CARD_BORDER,
            border_width=1,
        )
        self.txt_view.pack(fill="both", expand=True)

        # Configure custom tags in underlying Tkinter Text widget
        self._setup_text_tags()

    def _setup_text_tags(self):
        """Configures fonts and colors for markdown elements."""
        tk_txt = self.txt_view._textbox

        tk_txt.tag_config("h1", font=("Segoe UI", 18, "bold"), foreground="#38bdf8", spacing1=12, spacing3=6)
        tk_txt.tag_config("h2", font=("Segoe UI", 15, "bold"), foreground="#60a5fa", spacing1=10, spacing3=4)
        tk_txt.tag_config("h3", font=("Segoe UI", 13, "bold"), foreground="#93c5fd", spacing1=8, spacing3=2)
        tk_txt.tag_config("code_block", font=("Consolas", 11), background="#0b0c13", foreground="#38bdf8", lmargin1=20, lmargin2=20)
        tk_txt.tag_config("inline_code", font=("Consolas", 11), background="#1e2235", foreground="#38bdf8")
        tk_txt.tag_config("quote", font=("Segoe UI", 12, "italic"), foreground="#fde68a", lmargin1=25, lmargin2=25)
        tk_txt.tag_config("bullet", font=("Segoe UI", 13), foreground="#f8fafc", lmargin1=20, lmargin2=35)
        tk_txt.tag_config("bold", font=("Segoe UI", 13, "bold"), foreground="#ffffff")
        tk_txt.tag_config("separator", font=("Segoe UI", 8), foreground="#2b2e44")

    def _load_and_display_markdown(self):
        if not self.file_path.exists():
            self.txt_view.insert("end", f"No se encontró el archivo: {self.file_path}")
            return

        raw_text = self.file_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        self.txt_view.configure(state="normal")
        self.txt_view.delete("1.0", "end")

        in_code_block = False

        for line in lines:
            # Code block toggle
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                self.txt_view.insert("end", f"  {line}\n", "code_block")
                continue

            if in_code_block:
                self.txt_view.insert("end", f"    {line}\n", "code_block")
                continue

            # Headings
            if line.startswith("# "):
                self.txt_view.insert("end", f"{line[2:].strip()}\n", "h1")
            elif line.startswith("## "):
                self.txt_view.insert("end", f"{line[3:].strip()}\n", "h2")
            elif line.startswith("### "):
                self.txt_view.insert("end", f"{line[4:].strip()}\n", "h3")
            elif line.startswith("> "):
                self.txt_view.insert("end", f"▎ {line[2:].strip()}\n", "quote")
            elif line.startswith("- ") or line.startswith("* "):
                self.txt_view.insert("end", f"• {line[2:].strip()}\n", "bullet")
            elif line.strip() in ("---", "***", "___"):
                self.txt_view.insert("end", "────────────────────────────────────────────────────────────\n", "separator")
            else:
                self.txt_view.insert("end", f"{line}\n")

        self.txt_view.configure(state="disabled")

    def _open_in_browser(self):
        open_markdown_in_browser(self.file_path, title=self.doc_title)

    def _copy_content(self):
        if self.file_path.exists():
            text = self.file_path.read_text(encoding="utf-8")
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Copiado", "Contenido de la guía copiado al portapapeles.")
