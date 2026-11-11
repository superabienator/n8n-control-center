"""
Core Manager for n8n Control Center Pro.
Asynchronous controller for Docker stack, Ollama, Git Sync, Cloudflare Tunnel, and maintenance.
Cross-platform support: Windows, Linux, and macOS.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple


class CoreManager:
    """Manages Docker Compose stack, background threads, and integrations."""

    def __init__(self, base_dir: Optional[Path] = None, log_callback: Optional[Callable[[str, str], None]] = None):
        self.base_dir = (base_dir or Path(__file__).parent).resolve()
        self.stack_dir = self.base_dir / "stack"
        self.compose_file = self.stack_dir / "docker-compose.yml"
        self.env_file = self.stack_dir / ".env"
        self.init_sql_file = self.stack_dir / "init.sql"
        self.backups_dir = self.stack_dir / "backups" / "workflows"
        self.local_files_dir = self.stack_dir / "local-files"
        self.course_links_file = self.base_dir / "course_links.json"
        self.academia_dir = self.base_dir / "academia"
        self.settings_file = self.base_dir / "app_settings.json"

        self.log_callback = log_callback or (lambda text, level="info": print(f"[{level.upper()}] {text}"))
        self._lock = threading.Lock()
        self._tunnel_thread: Optional[threading.Thread] = None
        self._active_tunnel_url: Optional[str] = None

        # Settings defaults
        self.settings = {
            "auto_backup_on_stop": False,
            "theme": "dark",
        }
        self.load_settings()

        # Initialize environment and template files
        self.init_stack_files()

    # =========================================================================
    # Logging & Process Utilities
    # =========================================================================
    def log(self, text: str, level: str = "info") -> None:
        """Send formatted message to log callback."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {text}"
        try:
            self.log_callback(formatted, level)
        except Exception:
            pass

    def run_command_stream(
        self,
        cmd: list[str],
        cwd: Optional[Path] = None,
        on_line: Optional[Callable[[str], None]] = None,
    ) -> Tuple[int, str]:
        """
        Executes a shell command streaming stdout/stderr in real time.
        Returns (exit_code, full_output).
        """
        work_dir = str(cwd or self.stack_dir)
        full_output = []

        is_win = platform.system() == "Windows"
        creationflags = subprocess.CREATE_NO_WINDOW if is_win else 0

        try:
            self.log(f"Ejecutando: {' '.join(cmd)}", "command")
            proc = subprocess.Popen(
                cmd,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creationflags,
                encoding="utf-8",
                errors="replace",
            )

            if proc.stdout:
                for line in iter(proc.stdout.readline, ""):
                    clean_line = line.rstrip()
                    if clean_line:
                        full_output.append(clean_line)
                        if on_line:
                            on_line(clean_line)
                        else:
                            self.log(clean_line, "output")
                proc.stdout.close()

            proc.wait()
            return proc.returncode, "\n".join(full_output)
        except Exception as e:
            err_msg = f"Error ejecutando {' '.join(cmd)}: {e}"
            self.log(err_msg, "error")
            return 1, err_msg

    def get_docker_command(self) -> list[str]:
        """Detect whether 'docker compose' or 'docker-compose' is available."""
        try:
            res = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True, check=False)
            if res.returncode == 0:
                return ["docker", "compose"]
        except Exception:
            pass
        return ["docker-compose"]

    # =========================================================================
    # Hardware & System Detection
    # =========================================================================
    def check_nvidia_gpu(self) -> bool:
        """Detects if an NVIDIA GPU is available on the host system."""
        try:
            res = subprocess.run(["nvidia-smi"], capture_output=True, text=True, check=False)
            return res.returncode == 0
        except Exception:
            return False

    def check_docker_available(self) -> bool:
        """Checks if Docker engine is running."""
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, text=True, check=False)
            return res.returncode == 0
        except Exception:
            return False

    # =========================================================================
    # Stack Templates & Setup
    # =========================================================================
    def init_stack_files(self) -> None:
        """Auto-create stack directories, docker-compose.yml, .env and init.sql if missing."""
        self.stack_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.local_files_dir.mkdir(parents=True, exist_ok=True)
        self.academia_dir.mkdir(parents=True, exist_ok=True)

        gitkeep = self.local_files_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

        # 1. stack/init.sql for PGVector
        if not self.init_sql_file.exists():
            self.init_sql_file.write_text("CREATE EXTENSION IF NOT EXISTS vector;\n", encoding="utf-8")

        # 2. stack/.env
        if not self.env_file.exists():
            default_env = (
                "# n8n Control Center Pro - Stack Environment Variables\n"
                "POSTGRES_USER=n8n\n"
                "POSTGRES_PASSWORD=n8n_password\n"
                "POSTGRES_DB=n8n\n"
                "N8N_DEFAULT_BINARY_DATA_MODE=filesystem\n"
                "EXECUTIONS_DATA_PRUNE=true\n"
                "EXECUTIONS_DATA_MAX_AGE=72\n"
                "WEBHOOK_URL=http://localhost:5678/\n"
            )
            self.env_file.write_text(default_env, encoding="utf-8")

        # 3. stack/docker-compose.yml
        if not self.compose_file.exists():
            self.generate_docker_compose()

    def generate_docker_compose(self) -> None:
        """Generates modular docker-compose.yml with GPU detection for Ollama."""
        has_gpu = self.check_nvidia_gpu()

        gpu_section = ""
        if has_gpu:
            gpu_section = (
                "    deploy:\n"
                "      resources:\n"
                "        reservations:\n"
                "          devices:\n"
                "            - driver: nvidia\n"
                "              count: all\n"
                "              capabilities: [gpu]\n"
            )

        compose_content = f"""version: '3.8'

networks:
  n8n_network:
    name: n8n_network
    driver: bridge

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${{POSTGRES_USER:-n8n}}
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD:-n8n_password}}
      - POSTGRES_DB=${{POSTGRES_DB:-n8n}}
    volumes:
      - postgres_storage:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    networks:
      - n8n_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -U ${{POSTGRES_USER:-n8n}} -d ${{POSTGRES_DB:-n8n}}"]
      interval: 5s
      timeout: 5s
      retries: 5

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${{POSTGRES_DB:-n8n}}
      - DB_POSTGRESDB_USER=${{POSTGRES_USER:-n8n}}
      - DB_POSTGRESDB_PASSWORD=${{POSTGRES_PASSWORD:-n8n_password}}
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=72
      - WEBHOOK_URL=${{WEBHOOK_URL:-http://localhost:5678/}}
    ports:
      - "5678:5678"
    volumes:
      - n8n_storage:/home/node/.n8n
      - ./local-files:/files
      - ./backups:/backups
    networks:
      - n8n_network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    profiles: ["ollama"]
    ports:
      - "11434:11434"
    volumes:
      - ollama_storage:/root/.ollama
    networks:
      - n8n_network
{gpu_section}
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: n8n_tunnel
    restart: unless-stopped
    profiles: ["tunnel"]
    command: tunnel --no-autoupdate --url http://n8n:5678
    networks:
      - n8n_network

volumes:
  postgres_storage:
  n8n_storage:
  ollama_storage:
"""
        self.compose_file.write_text(compose_content, encoding="utf-8")
        self.log(f"docker-compose.yml generado (Modo GPU: {'Activado' if has_gpu else 'Desactivado (CPU)'}).")

    # =========================================================================
    # Status Monitoring (Live Semáforo cada 3s)
    # =========================================================================
    def get_service_statuses(self) -> Dict[str, str]:
        """
        Inspects running Docker containers.
        Returns dict with keys: 'n8n', 'postgres', 'ollama', 'tunnel'.
        Values: 'running', 'starting', 'stopped', 'error'.
        """
        statuses = {
            "n8n": "stopped",
            "postgres": "stopped",
            "ollama": "stopped",
            "tunnel": "stopped",
        }

        try:
            # Query docker ps formatted JSON
            cmd = ["docker", "ps", "-a", "--format", "{{.Names}}:::{{.State}}:::{{.Status}}"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode != 0:
                return statuses

            for line in res.stdout.strip().splitlines():
                parts = line.split(":::")
                if len(parts) >= 2:
                    name, state = parts[0].strip(), parts[1].strip()
                    status_text = parts[2].strip() if len(parts) > 2 else ""

                    if name == "n8n":
                        statuses["n8n"] = state
                    elif name == "postgres":
                        if "healthy" in status_text:
                            statuses["postgres"] = "running"
                        elif "unhealthy" in status_text:
                            statuses["postgres"] = "error"
                        elif state == "running":
                            statuses["postgres"] = "starting"
                        else:
                            statuses["postgres"] = state
                    elif name == "ollama":
                        statuses["ollama"] = state
                    elif name == "n8n_tunnel":
                        statuses["tunnel"] = state
        except Exception:
            pass

        return statuses

    # =========================================================================
    # Core Actions (Asynchronous Threads)
    # =========================================================================
    def start_base_stack_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Starts Postgres and n8n asynchronously."""
        def worker():
            self.init_stack_files()
            self.log("Levantando Stack Base (n8n + Postgres/PGVector)...")
            docker_cmd = self.get_docker_command()
            code, _ = self.run_command_stream(docker_cmd + ["up", "-d", "postgres", "n8n"])
            success = code == 0
            if success:
                self.log("✅ Stack Base iniciado correctamente.", "success")
            else:
                self.log("❌ Error al iniciar el Stack Base.", "error")
            if on_finish:
                on_finish(success)

        threading.Thread(target=worker, daemon=True).start()

    def stop_all_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Stops all running containers, optionally running auto-backup first."""
        def worker():
            if self.settings.get("auto_backup_on_stop", False):
                self.log("⚡ Auto-backup activado: exportando flujos antes de detener...")
                self._export_workflows_sync()
                self._push_to_git_sync()

            self.log("Deteniendo todos los servicios del stack...")
            docker_cmd = self.get_docker_command()
            code, _ = self.run_command_stream(
                docker_cmd + ["--profile", "ollama", "--profile", "tunnel", "stop"]
            )
            success = code == 0
            if success:
                self.log("🛑 Todos los servicios han sido detenidos.", "success")
            else:
                self.log("❌ Hubo un error al detener los servicios.", "error")
            if on_finish:
                on_finish(success)

        threading.Thread(target=worker, daemon=True).start()

    def open_n8n_browser(self) -> None:
        """Opens n8n Web UI in default browser."""
        url = "http://localhost:5678"
        self.log(f"Abriendo n8n en el navegador: {url}")
        webbrowser.open(url)

    # =========================================================================
    # Cloudflare Tunnel Feature
    # =========================================================================
    def start_tunnel_async(
        self,
        on_url_captured: Optional[Callable[[str], None]] = None,
        on_finish: Optional[Callable[[bool, Optional[str]], None]] = None,
    ) -> None:
        """
        Starts Cloudflare tunnel container, parses public URL,
        updates WEBHOOK_URL in .env, restarts n8n container.
        """
        def worker():
            docker_cmd = self.get_docker_command()
            self.log("Iniciando contenedor Cloudflare Quick Tunnel...")
            code, _ = self.run_command_stream(docker_cmd + ["--profile", "tunnel", "up", "-d", "cloudflared"])
            if code != 0:
                self.log("❌ Falló el inicio de cloudflared.", "error")
                if on_finish:
                    on_finish(False, None)
                return

            self.log("Esperando asignación de URL pública en Cloudflare...")
            tunnel_url = None
            url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

            # Poll container logs for up to 30 seconds
            start_time = time.time()
            while time.time() - start_time < 30:
                log_proc = subprocess.run(
                    ["docker", "logs", "--tail", "50", "n8n_tunnel"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                output = (log_proc.stdout or "") + (log_proc.stderr or "")
                match = url_pattern.search(output)
                if match:
                    tunnel_url = match.group(0)
                    break
                time.sleep(1.5)

            if not tunnel_url:
                self.log("⚠️ No se pudo extraer la URL del túnel a tiempo.", "warning")
                if on_finish:
                    on_finish(False, None)
                return

            self._active_tunnel_url = tunnel_url
            self.log(f"🌐 Túnel establecido con éxito: {tunnel_url}", "success")

            # Update WEBHOOK_URL in .env
            self.update_env_var("WEBHOOK_URL", f"{tunnel_url}/")
            self.log("Recargando n8n con la nueva WEBHOOK_URL...")
            self.run_command_stream(docker_cmd + ["restart", "n8n"])
            self.log("✅ n8n recargado. Webhooks listos para recibir eventos externos.", "success")

            if on_url_captured:
                on_url_captured(tunnel_url)
            if on_finish:
                on_finish(True, tunnel_url)

        threading.Thread(target=worker, daemon=True).start()

    def stop_tunnel_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Stops Cloudflare tunnel."""
        def worker():
            docker_cmd = self.get_docker_command()
            self.log("Deteniendo contenedor de túnel...")
            code, _ = self.run_command_stream(docker_cmd + ["--profile", "tunnel", "stop", "cloudflared"])
            self.update_env_var("WEBHOOK_URL", "http://localhost:5678/")
            self.run_command_stream(docker_cmd + ["restart", "n8n"])
            self.log("Túnel detenido y WEBHOOK_URL restaurado a localhost.")
            if on_finish:
                on_finish(code == 0)

        threading.Thread(target=worker, daemon=True).start()

    def update_env_var(self, key: str, value: str) -> None:
        """Updates or appends a key=value pair in stack/.env."""
        with self._lock:
            if not self.env_file.exists():
                self.init_stack_files()

            lines = self.env_file.read_text(encoding="utf-8").splitlines()
            found = False
            new_lines = []
            for line in lines:
                if line.strip().startswith(f"{key}="):
                    new_lines.append(f"{key}={value}")
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"{key}={value}")

            self.env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            self.log(f"Variable de entorno actualizada: {key}={value}")

    # =========================================================================
    # Ollama & Local AI
    # =========================================================================
    def toggle_ollama_async(self, start: bool, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Starts or stops the Ollama service."""
        def worker():
            docker_cmd = self.get_docker_command()
            action_name = "iniciando" if start else "deteniendo"
            self.log(f"{action_name.capitalize()} contenedor Ollama...")
            if start:
                code, _ = self.run_command_stream(docker_cmd + ["--profile", "ollama", "up", "-d", "ollama"])
            else:
                code, _ = self.run_command_stream(docker_cmd + ["--profile", "ollama", "stop", "ollama"])

            success = code == 0
            if success:
                self.log(f"Ollama {'encendido' if start else 'apagado'} correctamente.", "success")
            else:
                self.log("Error al cambiar estado de Ollama.", "error")
            if on_finish:
                on_finish(success)

        threading.Thread(target=worker, daemon=True).start()

    def install_ai_kit_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """
        Installs lightweight AI Kit:
        1. llama3.2:3b (Chat / Agents)
        2. nomic-embed-text (RAG Vectors)
        """
        def worker():
            # First ensure Ollama is running
            docker_cmd = self.get_docker_command()
            self.log("Verificando que Ollama esté en ejecución...")
            self.run_command_stream(docker_cmd + ["--profile", "ollama", "up", "-d", "ollama"])
            time.sleep(3)

            self.log("Descargando modelo de Chat y Agentes: llama3.2:3b...")
            code1, _ = self.run_command_stream(["docker", "exec", "ollama", "ollama", "pull", "llama3.2:3b"])

            self.log("Descargando modelo de Embeddings RAG: nomic-embed-text...")
            code2, _ = self.run_command_stream(["docker", "exec", "ollama", "ollama", "pull", "nomic-embed-text"])

            success = (code1 == 0 and code2 == 0)
            if success:
                self.log("🎉 Kit IA Ligero instalado con éxito.", "success")
            else:
                self.log("⚠️ Hubo problemas al descargar algunos modelos de Ollama.", "warning")
            if on_finish:
                on_finish(success)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================================
    # GitHub Sync & Workflows
    # =========================================================================
    def _export_workflows_sync(self) -> bool:
        """Runs n8n export:workflow within n8n container."""
        self.log("Exportando flujos desde n8n...")
        code, _ = self.run_command_stream(
            ["docker", "exec", "-u", "node", "n8n", "n8n", "export:workflow", "--backup", "--output=/backups/workflows/"]
        )
        return code == 0

    def _push_to_git_sync(self) -> bool:
        """Adds workflow JSONs, commits, and pushes to Git."""
        try:
            # Check if current repo is a git repo
            res = subprocess.run(["git", "status"], cwd=str(self.base_dir), capture_output=True, text=True, check=False)
            if res.returncode != 0:
                self.log("Repositorio Git no inicializado en la carpeta raíz. Inicializando...", "warning")
                subprocess.run(["git", "init"], cwd=str(self.base_dir), check=False)

            self.log("Preparando commit de flujos en Git...")
            self.run_command_stream(["git", "add", "stack/backups/workflows/"], cwd=self.base_dir)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"Auto-backup flujos n8n - {timestamp}"
            code_commit, _ = self.run_command_stream(["git", "commit", "-m", commit_msg], cwd=self.base_dir)

            self.log("Subiendo cambios al repositorio remoto (git push)...")
            code_push, _ = self.run_command_stream(["git", "push"], cwd=self.base_dir)

            if code_push == 0:
                self.log("🚀 Flujos subidos exitosamente a GitHub.", "success")
                return True
            else:
                self.log("Commit local guardado. Para sincronizar con la nube, configura tu 'git remote'.", "warning")
                return True
        except Exception as e:
            self.log(f"Error en Git Sync: {e}", "error")
            return False

    def export_and_push_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Exports workflows from n8n and pushes to GitHub asynchronously."""
        def worker():
            exp_ok = self._export_workflows_sync()
            if not exp_ok:
                self.log("❌ Falló la exportación interna de flujos.", "error")
                if on_finish:
                    on_finish(False)
                return

            git_ok = self._push_to_git_sync()
            if on_finish:
                on_finish(git_ok)

        threading.Thread(target=worker, daemon=True).start()

    def restore_and_import_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Performs git pull and imports workflows into n8n."""
        def worker():
            self.log("Descargando últimos cambios desde GitHub (git pull)...")
            self.run_command_stream(["git", "pull"], cwd=self.base_dir)

            self.log("Importando flujos al contenedor de n8n...")
            code, _ = self.run_command_stream(
                ["docker", "exec", "-u", "node", "n8n", "n8n", "import:workflow", "--separate", "--input=/backups/workflows/"]
            )
            success = code == 0
            if success:
                self.log("✅ Flujos importados y restaurados en n8n.", "success")
            else:
                self.log("❌ Error al importar flujos en n8n.", "error")
            if on_finish:
                on_finish(success)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================================
    # Cleaner / Maintenance
    # =========================================================================
    def clean_level_1_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Nivel 1 - Purga de Basura: docker system prune -f + VACUUM FULL in Postgres."""
        def worker():
            self.log("Iniciando Nivel 1: Purga de Basura de Docker...")
            self.run_command_stream(["docker", "system", "prune", "-f"])

            self.log("Ejecutando VACUUM FULL en PostgreSQL para compactar almacenamiento...")
            code, _ = self.run_command_stream(
                ["docker", "exec", "-i", "postgres", "psql", "-U", "n8n", "-d", "n8n", "-c", "VACUUM FULL;"]
            )
            if code == 0:
                self.log("✨ Nivel 1 completado: Base de datos compactada y Docker purgado.", "success")
            else:
                self.log("⚠️ Purga de Docker finalizada; Postgres no respondió a VACUUM.", "warning")
            if on_finish:
                on_finish(True)

        threading.Thread(target=worker, daemon=True).start()

    def clean_level_2_async(self, on_finish: Optional[Callable[[bool, str], None]] = None) -> None:
        """Nivel 2 - Vaciar Taller Temporal: Cleans stack/local-files/ and reports freed space."""
        def worker():
            self.log("Iniciando Nivel 2: Limpieza de archivos locales temporales...")
            total_bytes = 0
            file_count = 0

            if self.local_files_dir.exists():
                for root, _, files in os.walk(self.local_files_dir):
                    for f in files:
                        if f == ".gitkeep":
                            continue
                        p = Path(root) / f
                        try:
                            total_bytes += p.stat().st_size
                            p.unlink()
                            file_count += 1
                        except Exception as e:
                            self.log(f"No se pudo eliminar {p.name}: {e}", "warning")

                for root, dirs, _ in os.walk(self.local_files_dir, topdown=False):
                    for d in dirs:
                        dp = Path(root) / d
                        try:
                            dp.rmdir()
                        except Exception:
                            pass

            freed_mb = total_bytes / (1024 * 1024)
            msg = f"{freed_mb:.2f} MB liberados ({file_count} archivos eliminados)"
            self.log(f"🧹 Taller temporal vaciado: {msg}.", "success")
            if on_finish:
                on_finish(True, msg)

        threading.Thread(target=worker, daemon=True).start()

    def clean_level_3_async(self, on_finish: Optional[Callable[[bool], None]] = None) -> None:
        """Nivel 3 - Reset Nuclear: docker compose down -v --rmi all and recreate clean stack."""
        def worker():
            self.log("⚠️ ALERTA: Iniciando Reset Nuclear y desinstalación completa...", "warning")
            docker_cmd = self.get_docker_command()
            self.run_command_stream(
                docker_cmd + ["--profile", "ollama", "--profile", "tunnel", "down", "-v", "--rmi", "all"]
            )

            # Preserve backups if any, but clean rest of stack directory
            self.log("Limpiando directorios del stack...")
            try:
                if self.stack_dir.exists():
                    for item in self.stack_dir.iterdir():
                        if item.name == "backups":
                            continue
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
            except Exception as e:
                self.log(f"Nota en limpieza de archivos: {e}", "warning")

            self.init_stack_files()
            self.log("🔥 Reset Nuclear finalizado. Stack regenerado con configuración base limpia.", "success")
            if on_finish:
                on_finish(True)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================================
    # Academy & Course Links
    # =========================================================================
    def get_course_data(self) -> Dict[str, dict]:
        """Loads course_links.json dictionary."""
        if not self.course_links_file.exists():
            return {}
        try:
            return json.loads(self.course_links_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def update_course_link(self, module_key: str, url: str) -> None:
        """Saves a new URL for a course module in course_links.json."""
        with self._lock:
            data = self.get_course_data()
            if module_key in data:
                data[module_key]["url"] = url.strip()
            else:
                data[module_key] = {"title": module_key, "url": url.strip(), "fallback_file": ""}
            self.course_links_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            self.log(f"Enlace de academia guardado para [{module_key}]: {url}")

    def open_course(self, module_key: str) -> None:
        """
        Opens either the online Google NotebookLM/Doc link,
        or the local markdown file in academia/ as a fallback.
        """
        data = self.get_course_data()
        entry = data.get(module_key, {})
        url = entry.get("url", "").strip()
        fallback_rel = entry.get("fallback_file", "")

        if url.startswith("http://") or url.startswith("https://"):
            self.log(f"Abriendo enlace en línea para '{module_key}': {url}")
            webbrowser.open(url)
            return

        fallback_path = self.base_dir / fallback_rel
        if fallback_path.exists():
            self.log(f"Abriendo guía local para '{module_key}': {fallback_path.name}")
            try:
                system = platform.system()
                if system == "Windows":
                    os.startfile(str(fallback_path))
                elif system == "Darwin":
                    subprocess.run(["open", str(fallback_path)], check=False)
                else:
                    subprocess.run(["xdg-open", str(fallback_path)], check=False)
            except Exception as e:
                self.log(f"Abriendo en el navegador como alternativa: {e}")
                webbrowser.open(fallback_path.as_uri())
        else:
            self.log(f"No se encontró archivo de academia ni enlace configurado para '{module_key}'.", "warning")

    # =========================================================================
    # Settings Management
    # =========================================================================
    def load_settings(self) -> None:
        """Loads app_settings.json."""
        if self.settings_file.exists():
            try:
                loaded = json.loads(self.settings_file.read_text(encoding="utf-8"))
                self.settings.update(loaded)
            except Exception:
                pass

    def save_settings(self) -> None:
        """Persists app_settings.json."""
        with self._lock:
            try:
                self.settings_file.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
            except Exception as e:
                self.log(f"Error guardando configuración: {e}", "error")
