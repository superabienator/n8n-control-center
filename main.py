"""
n8n Control Center Pro
Modern cross-platform desktop application (Windows, Linux, macOS) for managing n8n,
PGVector (RAG), Ollama (Local AI), Cloudflare Tunnels, and Git Workflows.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Dict, Optional

import customtkinter as ctk

from autostart_manager import AutostartManager
from core_manager import CoreManager

# Appearance settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Design Palette
COLOR_BG = "#0f111a"
COLOR_SIDEBAR = "#161824"
COLOR_CARD = "#1c1e2e"
COLOR_CARD_BORDER = "#2b2e44"
COLOR_CARD_HOVER = "#23263b"
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_ACCENT = "#ea580c"        # n8n orange
COLOR_ACCENT_HOVER = "#c2410c"
COLOR_SUCCESS = "#10b981"       # emerald
COLOR_SUCCESS_HOVER = "#059669"
COLOR_WARNING = "#f59e0b"       # amber
COLOR_WARNING_HOVER = "#d97706"
COLOR_DANGER = "#ef4444"        # rose / red
COLOR_DANGER_HOVER = "#dc2626"
COLOR_PRIMARY_BLUE = "#3b82f6"  # blue
COLOR_PRIMARY_BLUE_HOVER = "#2563eb"
COLOR_ACADEMY = "#6366f1"       # indigo for course buttons
COLOR_ACADEMY_HOVER = "#4f46e5"


class N8NControlCenterApp(ctk.CTk):
    """Main Application Window for n8n Control Center Pro."""

    def __init__(self):
        super().__init__()

        self.title("n8n Control Center Pro - DevOps, Local AI & Cloudflare Tunnel")
        self.geometry("1100x820")
        self.minsize(980, 720)
        self.configure(fg_color=COLOR_BG)

        # Initialize Core Manager and Autostart Manager
        self.core = CoreManager(log_callback=self.thread_safe_log)
        self.autostart = AutostartManager()

        # Variables for dynamic states
        self.current_webhook_url = tk.StringVar(value="http://localhost:5678/")
        self.auto_backup_var = tk.BooleanVar(value=self.core.settings.get("auto_backup_on_stop", False))
        self.autostart_var = tk.BooleanVar(value=self.autostart.is_autostart_enabled())
        self.is_busy = False

        # Build UI
        self._setup_layout()
        self._build_header()
        self._build_tabs()
        self._build_console()

        # Update initial states
        self._refresh_workflow_count()
        self._load_current_env_webhook()

        # Start live monitoring loop (every 3 seconds)
        self._schedule_status_check()

    # =========================================================================
    # Layout Setup
    # =========================================================================
    def _setup_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=0, height=75)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)

        # Brand / Title
        brand_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        title_label = ctk.CTkLabel(
            brand_frame,
            text="⚡ n8n Control Center Pro",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            brand_frame,
            text="DevOps Modular • RAG Local (PGVector + Ollama) • Cloudflare Quick Tunnel • GitOps",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(anchor="w")

        # Header Right Controls (Docker status & Open Web UI)
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=20, pady=12, sticky="e")

        self.docker_status_badge = ctk.CTkLabel(
            right_frame,
            text="Docker: Verificando...",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#232738",
            corner_radius=8,
            padx=12,
            pady=4,
            text_color=COLOR_TEXT_MUTED,
        )
        self.docker_status_badge.pack(side="left", padx=10)

        open_web_btn = ctk.CTkButton(
            right_frame,
            text="🌐 Abrir n8n (:5678)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            corner_radius=8,
            command=self.core.open_n8n_browser,
        )
        open_web_btn.pack(side="left", padx=5)

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLOR_SIDEBAR,
            segmented_button_fg_color="#1f2233",
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_hover_color="#2b2e44",
            text_color=COLOR_TEXT_PRIMARY,
            corner_radius=12,
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=18, pady=(10, 8))

        # Add tabs
        self.tab_main = self.tabview.add("📊 Panel Principal")
        self.tab_ia = self.tabview.add("🧠 IA Local & RAG")
        self.tab_git = self.tabview.add("🐙 GitHub Sync")
        self.tab_clean = self.tabview.add("🧹 Limpiador")
        self.tab_academy = self.tabview.add("🎓 Configurar Academia")

        # Build contents of each tab
        self._populate_tab_main()
        self._populate_tab_ia()
        self._populate_tab_git()
        self._populate_tab_clean()
        self._populate_tab_academy()

    # =========================================================================
    # TAB 1: Panel Principal
    # =========================================================================
    def _populate_tab_main(self):
        tab = self.tab_main
        tab.grid_columnconfigure(0, weight=1)

        # 1. Semáforo en Vivo (Card 1)
        sem_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        sem_card.pack(fill="x", padx=12, pady=(10, 10))

        sem_header = ctk.CTkFrame(sem_card, fg_color="transparent")
        sem_header.pack(fill="x", padx=16, pady=(12, 6))

        sem_title = ctk.CTkLabel(
            sem_header,
            text="🚦 Semáforo en Vivo del Stack (Actualización cada 3s)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        sem_title.pack(side="left")

        # 4 Indicators in a grid
        indicators_frame = ctk.CTkFrame(sem_card, fg_color="transparent")
        indicators_frame.pack(fill="x", padx=16, pady=(4, 14))
        for i in range(4):
            indicators_frame.grid_columnconfigure(i, weight=1)

        # Helper to create indicator item
        def make_indicator(parent, col, title, subtitle):
            box = ctk.CTkFrame(parent, fg_color="#131522", corner_radius=8, border_color=COLOR_CARD_BORDER, border_width=1)
            box.grid(row=0, column=col, padx=6, pady=4, sticky="ew")

            top = ctk.CTkFrame(box, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(8, 2))

            dot = ctk.CTkLabel(top, text="●", font=ctk.CTkFont(size=18), text_color="#64748b", width=16)
            dot.pack(side="left")

            name = ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT_PRIMARY)
            name.pack(side="left", padx=6)

            status_lbl = ctk.CTkLabel(box, text=subtitle, font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED)
            status_lbl.pack(anchor="w", padx=12, pady=(0, 8))
            return dot, status_lbl

        self.dot_n8n, self.lbl_n8n = make_indicator(indicators_frame, 0, "n8n Core", "Comprobando...")
        self.dot_pg, self.lbl_pg = make_indicator(indicators_frame, 1, "Postgres + RAG", "Comprobando...")
        self.dot_ollama, self.lbl_ollama = make_indicator(indicators_frame, 2, "Ollama IA", "Comprobando...")
        self.dot_tunnel, self.lbl_tunnel = make_indicator(indicators_frame, 3, "Túnel Webhook", "Comprobando...")

        # 2. Control del Stack Base (Card 2)
        stack_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        stack_card.pack(fill="x", padx=12, pady=8)

        stack_head = ctk.CTkFrame(stack_card, fg_color="transparent")
        stack_head.pack(fill="x", padx=16, pady=(12, 6))

        st_title = ctk.CTkLabel(
            stack_head,
            text="🚀 Orquestación del Stack Base (n8n + PostgreSQL PGVector)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        st_title.pack(side="left")

        # Micro-button [🎓 Curso]
        btn_curso_gen = ctk.CTkButton(
            stack_head,
            text="🎓 Curso Stack",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=110,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("general"),
        )
        btn_curso_gen.pack(side="right")

        st_desc = ctk.CTkLabel(
            stack_card,
            text="Inicia o detiene los servicios centrales. PostgreSQL cuenta con PGVector activado y n8n con modo binario en disco.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        st_desc.pack(anchor="w", padx=16, pady=(0, 10))

        btn_row1 = ctk.CTkFrame(stack_card, fg_color="transparent")
        btn_row1.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_start_base = ctk.CTkButton(
            btn_row1,
            text="▶️ Iniciar Stack Base (n8n + RAG)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_start_base,
        )
        self.btn_start_base.pack(side="left", padx=(0, 10))

        self.btn_stop_all = ctk.CTkButton(
            btn_row1,
            text="⏹️ Detener Todo",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_stop_all,
        )
        self.btn_stop_all.pack(side="left", padx=10)

        self.btn_open_n8n = ctk.CTkButton(
            btn_row1,
            text="🌐 Abrir n8n en el Navegador",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_BLUE_HOVER,
            height=36,
            corner_radius=8,
            command=self.core.open_n8n_browser,
        )
        self.btn_open_n8n.pack(side="left", padx=10)

        # 3. Túnel Webhook Gratis (Card 3)
        tunnel_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        tunnel_card.pack(fill="x", padx=12, pady=8)

        tunnel_head = ctk.CTkFrame(tunnel_card, fg_color="transparent")
        tunnel_head.pack(fill="x", padx=16, pady=(12, 6))

        tun_title = ctk.CTkLabel(
            tunnel_head,
            text="🌐 Túnel Webhook Gratuito (Cloudflare Quick Tunnel)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        tun_title.pack(side="left")

        # Micro-button [🎓 Curso Webhooks]
        btn_curso_wh = ctk.CTkButton(
            tunnel_head,
            text="🎓 Curso Webhooks",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=130,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("webhooks"),
        )
        btn_curso_wh.pack(side="right")

        tun_desc = ctk.CTkLabel(
            tunnel_card,
            text="Genera un enlace HTTPS público temporal (*.trycloudflare.com), actualiza WEBHOOK_URL en .env y recarga n8n.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        tun_desc.pack(anchor="w", padx=16, pady=(0, 8))

        # URL display box
        url_box = ctk.CTkFrame(tunnel_card, fg_color="#131522", corner_radius=8, border_color=COLOR_CARD_BORDER, border_width=1)
        url_box.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(url_box, text="URL Activa para Webhooks:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=12, pady=8)

        self.entry_webhook_url = ctk.CTkEntry(
            url_box,
            textvariable=self.current_webhook_url,
            font=ctk.CTkFont(size=12),
            fg_color="#1a1c29",
            border_color="#2e3247",
            height=30,
            state="readonly",
        )
        self.entry_webhook_url.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        btn_copy_url = ctk.CTkButton(
            url_box,
            text="📋 Copiar URL",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=100,
            height=30,
            fg_color="#2b2f44",
            hover_color="#373c57",
            command=self._copy_webhook_to_clipboard,
        )
        btn_copy_url.pack(side="left", padx=(0, 10), pady=8)

        btn_row2 = ctk.CTkFrame(tunnel_card, fg_color="transparent")
        btn_row2.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_start_tunnel = ctk.CTkButton(
            btn_row2,
            text="⚡ Iniciar Túnel Cloudflare",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_WARNING,
            hover_color=COLOR_WARNING_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_start_tunnel,
        )
        self.btn_start_tunnel.pack(side="left", padx=(0, 10))

        self.btn_stop_tunnel = ctk.CTkButton(
            btn_row2,
            text="🛑 Detener Túnel",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#374151",
            hover_color="#4b5563",
            height=36,
            corner_radius=8,
            command=self._cmd_stop_tunnel,
        )
        self.btn_stop_tunnel.pack(side="left", padx=10)

    # =========================================================================
    # TAB 2: IA Local & RAG (Ollama)
    # =========================================================================
    def _populate_tab_ia(self):
        tab = self.tab_ia
        tab.grid_columnconfigure(0, weight=1)

        # Card 1: Ollama Engine Controls
        ollama_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        ollama_card.pack(fill="x", padx=12, pady=(10, 10))

        ol_head = ctk.CTkFrame(ollama_card, fg_color="transparent")
        ol_head.pack(fill="x", padx=16, pady=(12, 6))

        ol_title = ctk.CTkLabel(
            ol_head,
            text="🧠 Servidor de IA Local (Ollama)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        ol_title.pack(side="left")

        # Micro-button [🎓 Curso IA Local]
        btn_curso_ia = ctk.CTkButton(
            ol_head,
            text="🎓 Curso IA Local",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=120,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("ia_local"),
        )
        btn_curso_ia.pack(side="right")

        ol_desc = ctk.CTkLabel(
            ollama_card,
            text="Ejecuta modelos LLM y embeddings localmente dentro de la red Docker sin consumir cuotas de API de pago.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        ol_desc.pack(anchor="w", padx=16, pady=(0, 10))

        ol_btn_row = ctk.CTkFrame(ollama_card, fg_color="transparent")
        ol_btn_row.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_toggle_ollama = ctk.CTkButton(
            ol_btn_row,
            text="⚡ Encender / Apagar Ollama Local",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_BLUE_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_toggle_ollama,
        )
        self.btn_toggle_ollama.pack(side="left", padx=(0, 10))

        self.btn_install_kit = ctk.CTkButton(
            ol_btn_row,
            text="📦 Instalar Kit IA Ligero (1 Clic)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_install_ai_kit,
        )
        self.btn_install_kit.pack(side="left", padx=10)

        kit_info = ctk.CTkLabel(
            ollama_card,
            text="* Kit Ligero: Descarga 'llama3.2:3b' (Chat & Agentes rápidos) y 'nomic-embed-text' (Vectores RAG de alta fidelidad).",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#38bdf8",
        )
        kit_info.pack(anchor="w", padx=16, pady=(0, 10))

        # Card 2: Credenciales e Integración con n8n
        creds_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        creds_card.pack(fill="x", padx=12, pady=8)

        cr_head = ctk.CTkFrame(creds_card, fg_color="transparent")
        cr_head.pack(fill="x", padx=16, pady=(12, 6))

        cr_title = ctk.CTkLabel(
            cr_head,
            text="📋 Credenciales Listas para Pegar en n8n",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        cr_title.pack(side="left")

        # Micro-button [🎓 Curso RAG & Memoria]
        btn_curso_rag = ctk.CTkButton(
            cr_head,
            text="🎓 Curso RAG & Memoria",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=160,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("rag"),
        )
        btn_curso_rag.pack(side="right")

        cr_desc = ctk.CTkLabel(
            creds_card,
            text="Usa estos valores exactos al configurar credenciales en los nodos de n8n para comunicarse por la red interna:",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        cr_desc.pack(anchor="w", padx=16, pady=(0, 10))

        # Credential rows
        grid_creds = ctk.CTkFrame(creds_card, fg_color="#131522", corner_radius=8, border_color=COLOR_CARD_BORDER, border_width=1)
        grid_creds.pack(fill="x", padx=16, pady=(0, 14))

        creds_data = [
            ("Host Ollama (Base URL):", "http://ollama:11434"),
            ("Host Postgres (Base de Datos):", "postgres"),
            ("Puerto Postgres:", "5432"),
            ("Usuario Postgres:", "n8n"),
            ("Contraseña Postgres:", "n8n_password"),
            ("Nombre Base de Datos:", "n8n"),
            ("Modelo Chat Sugerido:", "llama3.2:3b"),
            ("Modelo Embeddings Sugerido:", "nomic-embed-text"),
        ]

        for i, (label_txt, val_txt) in enumerate(creds_data):
            row = ctk.CTkFrame(grid_creds, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            lbl = ctk.CTkLabel(row, text=label_txt, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_PRIMARY, width=220, anchor="w")
            lbl.pack(side="left")

            val_entry = ctk.CTkEntry(row, font=ctk.CTkFont(size=12), fg_color="#1a1c29", border_color="#2e3247", height=28)
            val_entry.insert(0, val_txt)
            val_entry.configure(state="readonly")
            val_entry.pack(side="left", fill="x", expand=True, padx=8)

            btn_copy = ctk.CTkButton(
                row,
                text="Copiar",
                font=ctk.CTkFont(size=11),
                width=65,
                height=26,
                fg_color="#2b2f44",
                hover_color="#373c57",
                command=lambda v=val_txt: self._copy_to_clipboard(v),
            )
            btn_copy.pack(side="right")

    # =========================================================================
    # TAB 3: GitHub Sync (Backups)
    # =========================================================================
    def _populate_tab_git(self):
        tab = self.tab_git
        tab.grid_columnconfigure(0, weight=1)

        git_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        git_card.pack(fill="x", padx=12, pady=(10, 10))

        git_head = ctk.CTkFrame(git_card, fg_color="transparent")
        git_head.pack(fill="x", padx=16, pady=(12, 6))

        git_title = ctk.CTkLabel(
            git_head,
            text="🐙 Sincronización y Respaldo GitOps con GitHub",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        git_title.pack(side="left")

        # Micro-button [🎓 Curso Git Sync]
        btn_curso_git = ctk.CTkButton(
            git_head,
            text="🎓 Curso Git Sync",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=130,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("git_sync"),
        )
        btn_curso_git.pack(side="right")

        git_desc = ctk.CTkLabel(
            git_card,
            text="Exporta flujos en JSON individuales para control de versiones en Git y permite restaurarlos en cualquier momento.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        git_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # Workflow count badge & Folder button
        info_row = ctk.CTkFrame(git_card, fg_color="#131522", corner_radius=8, border_color=COLOR_CARD_BORDER, border_width=1)
        info_row.pack(fill="x", padx=16, pady=(0, 14))

        self.lbl_wf_count = ctk.CTkLabel(
            info_row,
            text="📁 Flujos respaldados en disco: 0 archivos JSON",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8",
        )
        self.lbl_wf_count.pack(side="left", padx=14, pady=10)

        btn_open_folder = ctk.CTkButton(
            info_row,
            text="📂 Abrir Carpeta Backups",
            font=ctk.CTkFont(size=12),
            width=170,
            height=28,
            fg_color="#2b2f44",
            hover_color="#373c57",
            command=self._open_backups_folder,
        )
        btn_open_folder.pack(side="right", padx=14, pady=8)

        # Action Buttons
        git_btn_row = ctk.CTkFrame(git_card, fg_color="transparent")
        git_btn_row.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_export_git = ctk.CTkButton(
            git_btn_row,
            text="📤 Exportar y Subir Flujos a GitHub",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_export_git,
        )
        self.btn_export_git.pack(side="left", padx=(0, 10))

        self.btn_restore_git = ctk.CTkButton(
            git_btn_row,
            text="📥 Restaurar / Importar Flujos desde GitHub",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_BLUE_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_restore_git,
        )
        self.btn_restore_git.pack(side="left", padx=10)

        # Switches row
        switch_row = ctk.CTkFrame(git_card, fg_color="transparent")
        switch_row.pack(fill="x", padx=16, pady=(0, 14))

        self.switch_auto_backup = ctk.CTkSwitch(
            switch_row,
            text="⚡ Auto-guardar y exportar a GitHub automáticamente al detener n8n",
            variable=self.auto_backup_var,
            font=ctk.CTkFont(size=12),
            progress_color=COLOR_SUCCESS,
            command=self._on_toggle_auto_backup,
        )
        self.switch_auto_backup.pack(side="left")

        self.switch_autostart = ctk.CTkSwitch(
            switch_row,
            text="🚀 Autoarranque con el sistema operativo",
            variable=self.autostart_var,
            font=ctk.CTkFont(size=12),
            progress_color=COLOR_PRIMARY_BLUE,
            command=self._on_toggle_autostart,
        )
        self.switch_autostart.pack(side="left", padx=(30, 0))

    # =========================================================================
    # TAB 4: Limpiador (Mantenimiento)
    # =========================================================================
    def _populate_tab_clean(self):
        tab = self.tab_clean
        tab.grid_columnconfigure(0, weight=1)

        # Header card
        clean_header_card = ctk.CTkFrame(tab, fg_color="transparent")
        clean_header_card.pack(fill="x", padx=12, pady=(10, 4))

        cl_title = ctk.CTkLabel(
            clean_header_card,
            text="🧹 Herramientas de Mantenimiento y Optimización del Almacenamiento",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        cl_title.pack(side="left")

        # Micro-button [🎓 Curso Mantenimiento]
        btn_curso_maint = ctk.CTkButton(
            clean_header_card,
            text="🎓 Curso Mantenimiento",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLOR_ACADEMY,
            hover_color=COLOR_ACADEMY_HOVER,
            width=150,
            height=26,
            corner_radius=6,
            command=lambda: self.core.open_course("mantenimiento"),
        )
        btn_curso_maint.pack(side="right")

        # Nivel 1: Azul
        card_l1 = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color="#2563eb", border_width=1, corner_radius=10)
        card_l1.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(card_l1, text="🔹 Nivel 1 - Purga de Basura & Compactación DB", font=ctk.CTkFont(size=14, weight="bold"), text_color="#60a5fa").pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(
            card_l1,
            text="Ejecuta 'docker system prune -f' para eliminar imágenes huérfanas y lanza 'VACUUM FULL;' en PostgreSQL para compactar espacio en disco sin borrar datos.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        btn_l1 = ctk.CTkButton(
            card_l1,
            text="🧹 Ejecutar Purga Nivel 1 (Azul)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=32,
            corner_radius=8,
            command=self._cmd_clean_l1,
        )
        btn_l1.pack(anchor="w", padx=16, pady=(0, 12))

        # Nivel 2: Naranja
        card_l2 = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color="#d97706", border_width=1, corner_radius=10)
        card_l2.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(card_l2, text="🔸 Nivel 2 - Vaciar Taller de Archivos Temporales", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fbbf24").pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(
            card_l2,
            text="Limpia completamente el contenido de 'stack/local-files/' (archivos generados por flujos, descargas intermedias de n8n) y calcula el espacio liberado.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        btn_l2 = ctk.CTkButton(
            card_l2,
            text="🗑️ Vaciar Taller Temporal (Naranja)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#d97706",
            hover_color="#b45309",
            height=32,
            corner_radius=8,
            command=self._cmd_clean_l2,
        )
        btn_l2.pack(anchor="w", padx=16, pady=(0, 12))

        # Nivel 3: Rojo
        card_l3 = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color="#dc2626", border_width=1, corner_radius=10)
        card_l3.pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(card_l3, text="💥 Nivel 3 - Reset Nuclear / Desinstalación Completa", font=ctk.CTkFont(size=14, weight="bold"), text_color="#f87171").pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(
            card_l3,
            text="⚠️ ACCIÓN DESTRUCTIVA: Ejecuta 'docker compose down -v --rmi all', detiene y borra todos los volúmenes de datos y restaura el stack a estado inicial.",
            font=ctk.CTkFont(size=12),
            text_color="#fca5a5",
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 8))

        btn_l3 = ctk.CTkButton(
            card_l3,
            text="⚠️ Ejecutar Reset Nuclear (Rojo - Requiere Confirmación)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            height=32,
            corner_radius=8,
            command=self._cmd_clean_l3,
        )
        btn_l3.pack(anchor="w", padx=16, pady=(0, 12))

    # =========================================================================
    # TAB 5: Configurar Academia
    # =========================================================================
    def _populate_tab_academy(self):
        tab = self.tab_academy
        tab.grid_columnconfigure(0, weight=1)

        acad_card = ctk.CTkFrame(tab, fg_color=COLOR_CARD, border_color=COLOR_CARD_BORDER, border_width=1, corner_radius=10)
        acad_card.pack(fill="x", padx=12, pady=(10, 10))

        ac_head = ctk.CTkFrame(acad_card, fg_color="transparent")
        ac_head.pack(fill="x", padx=16, pady=(12, 6))

        ac_title = ctk.CTkLabel(
            ac_head,
            text="🎓 Configuración de Cuadernos y Enlaces de la Academia",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        ac_title.pack(side="left")

        btn_open_acad_folder = ctk.CTkButton(
            ac_head,
            text="📁 Carpeta Guías Locales (academia/)",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2b2f44",
            hover_color="#373c57",
            width=210,
            height=26,
            corner_radius=6,
            command=self._open_academia_folder,
        )
        btn_open_acad_folder.pack(side="right")

        ac_desc = ctk.CTkLabel(
            acad_card,
            text="Pega aquí los enlaces públicos a tus cuadernos de Google NotebookLM o Google Docs para cada módulo.\nSi dejas una URL en blanco, el micro-botón [🎓 Curso] abrirá automáticamente la guía local en Markdown de la carpeta 'academia/'.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left",
        )
        ac_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # Dynamic entries for modules
        courses = self.core.get_course_data()
        self.course_entries: Dict[str, ctk.CTkEntry] = {}

        module_labels = {
            "general": "Módulo 1: n8n desde Cero y Webhooks (01_Curso_Express)",
            "rag": "Módulo 2: RAG y Memoria de IA con PGVector (02_Curso_Acelerado)",
            "ia_local": "Módulo 3: IA Local y Modelos con Ollama (03_Curso_IA_Local)",
            "git_sync": "Módulo 4: GitHub Sync y Máquina del Tiempo (04_Guia_GitHub)",
            "mantenimiento": "Módulo 5: Limpiador y Mantenimiento Seguro (04_Guia_Limpiador)",
        }

        form_frame = ctk.CTkFrame(acad_card, fg_color="#131522", corner_radius=8, border_color=COLOR_CARD_BORDER, border_width=1)
        form_frame.pack(fill="x", padx=16, pady=(0, 14))

        for key, display_name in module_labels.items():
            entry_data = courses.get(key, {})
            current_url = entry_data.get("url", "")

            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=6)

            lbl = ctk.CTkLabel(row, text=display_name, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT_PRIMARY, width=280, anchor="w")
            lbl.pack(side="left")

            entry = ctk.CTkEntry(
                row,
                placeholder_text="https://notebooklm.google.com/... o https://docs.google.com/...",
                font=ctk.CTkFont(size=12),
                fg_color="#1a1c29",
                border_color="#2e3247",
                height=30,
            )
            entry.insert(0, current_url)
            entry.pack(side="left", fill="x", expand=True, padx=8)
            self.course_entries[key] = entry

            btn_test = ctk.CTkButton(
                row,
                text="Abrir",
                font=ctk.CTkFont(size=11),
                width=60,
                height=28,
                fg_color=COLOR_ACADEMY,
                hover_color=COLOR_ACADEMY_HOVER,
                command=lambda k=key: self.core.open_course(k),
            )
            btn_test.pack(side="right")

        # Save all button
        btn_save_courses = ctk.CTkButton(
            acad_card,
            text="💾 Guardar Todos los Enlaces de la Academia",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            height=36,
            corner_radius=8,
            command=self._cmd_save_courses,
        )
        btn_save_courses.pack(anchor="w", padx=16, pady=(0, 14))

    # =========================================================================
    # Real-Time Console Panel
    # =========================================================================
    def _build_console(self):
        console_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=10, height=210)
        console_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 14))
        console_frame.grid_columnconfigure(0, weight=1)

        head = ctk.CTkFrame(console_frame, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(8, 4))

        con_title = ctk.CTkLabel(
            head,
            text="📟 Consola de Operaciones en Tiempo Real",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        con_title.pack(side="left")

        # Console controls
        btn_copy_log = ctk.CTkButton(
            head,
            text="Copiar Log",
            font=ctk.CTkFont(size=11),
            width=80,
            height=24,
            fg_color="#2b2f44",
            hover_color="#373c57",
            command=self._copy_console_log,
        )
        btn_copy_log.pack(side="right", padx=(6, 0))

        btn_clear = ctk.CTkButton(
            head,
            text="Limpiar",
            font=ctk.CTkFont(size=11),
            width=70,
            height=24,
            fg_color="#2b2f44",
            hover_color="#373c57",
            command=self._clear_console,
        )
        btn_clear.pack(side="right")

        self.txt_console = ctk.CTkTextbox(
            console_frame,
            fg_color="#0b0c13",
            text_color="#e2e8f0",
            font=ctk.CTkFont(family="Consolas" if platform.system() == "Windows" else "Courier", size=11),
            wrap="word",
            corner_radius=6,
            height=140,
        )
        self.txt_console.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    # =========================================================================
    # Thread-Safe Logging & UI Feedback
    # =========================================================================
    def thread_safe_log(self, text: str, level: str = "info") -> None:
        """Appends text to the GUI console safely from any thread."""
        def append():
            self.txt_console.configure(state="normal")
            prefix = ""
            if level == "error":
                prefix = "❌ "
            elif level == "warning":
                prefix = "⚠️ "
            elif level == "success":
                prefix = "✅ "
            elif level == "command":
                prefix = "💻 "

            self.txt_console.insert("end", f"{prefix}{text}\n")
            self.txt_console.see("end")
            self.txt_console.configure(state="disabled")

        self.after(0, append)

    def _clear_console(self):
        self.txt_console.configure(state="normal")
        self.txt_console.delete("1.0", "end")
        self.txt_console.configure(state="disabled")

    def _copy_console_log(self):
        text = self.txt_console.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.thread_safe_log("Log completo copiado al portapapeles.", "success")

    def _copy_to_clipboard(self, val: str):
        self.clipboard_clear()
        self.clipboard_append(val)
        self.thread_safe_log(f"Copiado al portapapeles: {val}", "success")

    def _copy_webhook_to_clipboard(self):
        val = self.current_webhook_url.get()
        self._copy_to_clipboard(val)

    # =========================================================================
    # Status Monitoring (Live Semáforo cada 3s)
    # =========================================================================
    def _schedule_status_check(self):
        def worker():
            docker_ok = self.core.check_docker_available()
            statuses = self.core.get_service_statuses()

            def update_ui():
                # Docker Engine badge
                if docker_ok:
                    self.docker_status_badge.configure(text="Docker: Activo ✅", text_color=COLOR_SUCCESS, fg_color="#122a22")
                else:
                    self.docker_status_badge.configure(text="Docker: Inactivo ❌", text_color=COLOR_DANGER, fg_color="#2a1215")

                # Helper to set colors
                def set_badge(dot, lbl, state):
                    if state == "running":
                        dot.configure(text_color=COLOR_SUCCESS)
                        lbl.configure(text="En ejecución", text_color=COLOR_SUCCESS)
                    elif state == "starting":
                        dot.configure(text_color=COLOR_WARNING)
                        lbl.configure(text="Iniciando...", text_color=COLOR_WARNING)
                    elif state == "error":
                        dot.configure(text_color=COLOR_DANGER)
                        lbl.configure(text="Error / Degradado", text_color=COLOR_DANGER)
                    else:
                        dot.configure(text_color="#64748b")
                        lbl.configure(text="Detenido", text_color=COLOR_TEXT_MUTED)

                set_badge(self.dot_n8n, self.lbl_n8n, statuses.get("n8n", "stopped"))
                set_badge(self.dot_pg, self.lbl_pg, statuses.get("postgres", "stopped"))
                set_badge(self.dot_ollama, self.lbl_ollama, statuses.get("ollama", "stopped"))
                set_badge(self.dot_tunnel, self.lbl_tunnel, statuses.get("tunnel", "stopped"))

                self._refresh_workflow_count()

            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()
        # Schedule next check in 3000ms
        self.after(3000, self._schedule_status_check)

    def _refresh_workflow_count(self):
        count = 0
        if self.core.backups_dir.exists():
            count = len(list(self.core.backups_dir.glob("*.json")))
        self.lbl_wf_count.configure(text=f"📁 Flujos respaldados en disco: {count} archivo(s) JSON")

    def _load_current_env_webhook(self):
        if self.core.env_file.exists():
            for line in self.core.env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("WEBHOOK_URL="):
                    val = line.split("=", 1)[1].strip()
                    self.current_webhook_url.set(val)
                    break

    # =========================================================================
    # Action Handlers
    # =========================================================================
    def _cmd_start_base(self):
        self.btn_start_base.configure(state="disabled")
        self.core.start_base_stack_async(
            on_finish=lambda ok: self.after(0, lambda: self.btn_start_base.configure(state="normal"))
        )

    def _cmd_stop_all(self):
        self.btn_stop_all.configure(state="disabled")
        self.core.stop_all_async(
            on_finish=lambda ok: self.after(0, lambda: self.btn_stop_all.configure(state="normal"))
        )

    def _cmd_start_tunnel(self):
        self.btn_start_tunnel.configure(state="disabled")

        def on_url_captured(url: str):
            def ui_update():
                self.current_webhook_url.set(f"{url}/")
                self._copy_to_clipboard(f"{url}/")
            self.after(0, ui_update)

        def on_finish(ok, url):
            def ui_update():
                self.btn_start_tunnel.configure(state="normal")
                if ok and url:
                    messagebox.showinfo(
                        "Túnel Activo",
                        f"¡Túnel Cloudflare iniciado con éxito!\n\nURL Pública:\n{url}\n\nHa sido copiada al portapapeles y n8n ha sido recargado.",
                    )
            self.after(0, ui_update)

        self.core.start_tunnel_async(on_url_captured=on_url_captured, on_finish=on_finish)

    def _cmd_stop_tunnel(self):
        self.btn_stop_tunnel.configure(state="disabled")
        self.core.stop_tunnel_async(
            on_finish=lambda ok: self.after(0, lambda: (
                self.btn_stop_tunnel.configure(state="normal"),
                self.current_webhook_url.set("http://localhost:5678/")
            ))
        )

    def _cmd_toggle_ollama(self):
        statuses = self.core.get_service_statuses()
        is_running = statuses.get("ollama") == "running"
        new_state = not is_running
        self.btn_toggle_ollama.configure(state="disabled")
        self.core.toggle_ollama_async(
            start=new_state,
            on_finish=lambda ok: self.after(0, lambda: self.btn_toggle_ollama.configure(state="normal"))
        )

    def _cmd_install_ai_kit(self):
        self.btn_install_kit.configure(state="disabled")
        self.core.install_ai_kit_async(
            on_finish=lambda ok: self.after(0, lambda: (
                self.btn_install_kit.configure(state="normal"),
                messagebox.showinfo("Kit IA Ligero", "Descarga e instalación de modelos completada. Revisa la consola.") if ok else None
            ))
        )

    def _cmd_export_git(self):
        self.btn_export_git.configure(state="disabled")
        self.core.export_and_push_async(
            on_finish=lambda ok: self.after(0, lambda: (
                self.btn_export_git.configure(state="normal"),
                self._refresh_workflow_count()
            ))
        )

    def _cmd_restore_git(self):
        self.btn_restore_git.configure(state="disabled")
        self.core.restore_and_import_async(
            on_finish=lambda ok: self.after(0, lambda: (
                self.btn_restore_git.configure(state="normal"),
                self._refresh_workflow_count()
            ))
        )

    def _on_toggle_auto_backup(self):
        val = self.auto_backup_var.get()
        self.core.settings["auto_backup_on_stop"] = val
        self.core.save_settings()
        self.core.log(f"Configuración: Auto-backup al detener n8n = {val}", "info")

    def _on_toggle_autostart(self):
        val = self.autostart_var.get()
        if val:
            success = self.autostart.enable_autostart()
            if success:
                self.core.log("🚀 Autoarranque con el sistema operativo ACTIVADO.", "success")
            else:
                self.core.log("⚠️ No se pudo activar el autoarranque en este sistema.", "warning")
                self.autostart_var.set(False)
        else:
            success = self.autostart.disable_autostart()
            if success:
                self.core.log("🛑 Autoarranque con el sistema operativo DESACTIVADO.", "info")
            else:
                self.core.log("⚠️ No se pudo desactivar el autoarranque.", "warning")

    def _open_backups_folder(self):
        p = self.core.backups_dir
        p.mkdir(parents=True, exist_ok=True)
        try:
            if platform.system() == "Windows":
                os.startfile(str(p))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(p)], check=False)
            else:
                subprocess.run(["xdg-open", str(p)], check=False)
        except Exception as e:
            self.core.log(f"No se pudo abrir la carpeta de backups: {e}", "warning")

    def _open_academia_folder(self):
        p = self.core.academia_dir
        p.mkdir(parents=True, exist_ok=True)
        try:
            if platform.system() == "Windows":
                os.startfile(str(p))
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(p)], check=False)
            else:
                subprocess.run(["xdg-open", str(p)], check=False)
        except Exception as e:
            self.core.log(f"No se pudo abrir la carpeta academia: {e}", "warning")

    def _cmd_clean_l1(self):
        self.core.clean_level_1_async(
            on_finish=lambda ok: self.after(0, lambda: messagebox.showinfo("Limpieza Nivel 1", "Purga de Docker y VACUUM FULL completados."))
        )

    def _cmd_clean_l2(self):
        def on_done(ok, msg):
            def ui():
                messagebox.showinfo("Limpieza Nivel 2", f"Taller temporal vaciado:\n{msg}")
            self.after(0, ui)
        self.core.clean_level_2_async(on_finish=on_done)

    def _cmd_clean_l3(self):
        confirm = messagebox.askyesno(
            "⚠️ Confirmación de Reset Nuclear",
            "¿Estás seguro de que deseas ejecutar el Reset Nuclear?\n\n"
            "• Se destruirán todos los contenedores e imágenes asociadas.\n"
            "• Se eliminarán los volúmenes de PostgreSQL y credenciales locales de n8n.\n"
            "• La configuración se reiniciará al estado de fábrica.\n\n"
            "¿Deseas continuar?",
            icon="warning",
        )
        if not confirm:
            return

        self.core.clean_level_3_async(
            on_finish=lambda ok: self.after(0, lambda: (
                self._load_current_env_webhook(),
                self._refresh_workflow_count(),
                messagebox.showinfo("Reset Nuclear", "El stack ha sido restablecido a su estado inicial limpio.")
            ))
        )

    def _cmd_save_courses(self):
        for key, entry in self.course_entries.items():
            val = entry.get().strip()
            self.core.update_course_link(key, val)
        messagebox.showinfo("Academia", "Todos los enlaces de la academia han sido guardados correctamente.")


def main():
    app = N8NControlCenterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
