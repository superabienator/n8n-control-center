# 🚀 n8n Control Center Pro

Aplicación de escritorio multiplataforma (Windows, Linux, macOS) para orquestar **n8n**, **PostgreSQL con PGVector (RAG)**, **Ollama (IA Local)**, **Túneles de Cloudflare** y sincronización GitOps de flujos.

---

## 📁 Estructura del Proyecto

```text
├── main.py                     # Interfaz gráfica moderna en CustomTkinter con pestañas y semáforo en vivo
├── core_manager.py             # Controlador asíncrono multiplataforma (Docker, subprocess, threading)
├── course_links.json           # Mapeo de URLs públicas de NotebookLM / Docs con fallback a academia/
├── requirements.txt            # Dependencias del proyecto (customtkinter, packaging, pyinstaller, etc.)
├── .gitignore                  # Exclusiones de Git preservando backups/ y academia/
├── README.md                   # Documentación y guía de ejecución
├── academia/                   # Guías educativas locales en Markdown (fallback automático)
│   ├── curso_general.md        # Arquitectura del stack y variables de entorno
│   ├── curso_webhooks.md       # Exposición de webhooks con Cloudflare Tunnels
│   ├── curso_ia_local.md       # IA Local, modelos Llama 3.2 y Embeddings RAG
│   ├── curso_git_sync.md       # Respaldo y versionado GitOps de flujos JSON
│   └── curso_mantenimiento.md  # Purga de Docker, VACUUM en Postgres y limpieza
└── stack/                      # Directorio de contenedores y volúmenes Docker
    ├── docker-compose.yml      # Stack modular (postgres:pgvector, n8n, ollama, cloudflared)
    ├── .env                    # Variables de entorno optimizadas
    ├── init.sql                # Inicialización de la extensión PGVector en Postgres
    ├── backups/workflows/      # Flujos exportados en formato JSON independiente
    └── local-files/            # Directorio para archivos binarios de n8n (/files)
```

---

## ⚡ Requisitos Previos

1. **Python 3.10+**: Asegúrate de tener Python instalado.
2. **Docker & Docker Compose**: Docker Desktop (Windows/Mac) o Docker Engine (Linux) en ejecución.
3. **Git**: Para el control de versiones y sincronización con GitHub.

---

## 🚀 Inicio Rápido

1. **Activar el entorno virtual**:
   - En Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - En Linux / macOS:
     ```bash
     source .venv/bin/activate
     ```

2. **Ejecutar la aplicación**:
   ```bash
   python main.py
   # o utilizando el entorno directamente:
   .\.venv\Scripts\python.exe main.py
   ```

---

## 🧩 Características Principales

### 1. Panel Principal & Semáforo en Vivo
- Semáforo con refresco automático cada 3 segundos indicando el estado de **n8n**, **Postgres (PGVector)**, **Ollama** y **Túnel Webhook**.
- Botones de arranque y parada seguros.
- Túnel Cloudflare: genera una URL pública `https://*.trycloudflare.com` temporal, actualiza automáticamente `WEBHOOK_URL` en `stack/.env`, reinicia el contenedor de n8n y copia la URL al portapapeles.

### 2. IA Local & RAG (Ollama)
- Control de encendido/apagado del contenedor de Ollama.
- **Kit IA Ligero (1 Clic)**: Descarga automática de `llama3.2:3b` (chat/agentes rápidos) y `nomic-embed-text` (vectores RAG).
- Tarjeta de credenciales con botones para copiar hosts y contraseñas listos para pegar en n8n (`http://ollama:11434`, `postgres:5432`).

### 3. GitHub Sync (Backups & GitOps)
- **Exportar y Subir**: Exporta flujos de n8n con `n8n export:workflow --backup --output=/backups/workflows/` y hace commit/push en Git.
- **Restaurar e Importar**: Descarga con `git pull` e importa los flujos con `n8n import:workflow --separate`.
- Switch para auto-guardar en Git antes de detener el stack.

### 4. Limpiador y Mantenimiento
- **Nivel 1 (Azul)**: Purga de imágenes no usadas (`docker system prune -f`) y compactación de base de datos (`VACUUM FULL;` en Postgres).
- **Nivel 2 (Naranja)**: Limpieza del taller temporal `stack/local-files/` con reporte de megabytes liberados.
- **Nivel 3 (Rojo)**: Reset Nuclear del stack (`docker compose down -v --rmi all` con confirmación de seguridad).

### 5. Configurar Academia & Botones `[🎓 Curso]`
- Cada tarjeta dispone de un micro-botón `[🎓 Curso]`.
- En la pestaña **Configurar Academia**, puedes vincular URLs públicas a cuadernos de Google NotebookLM o Google Docs. Si se deja en blanco, la aplicación abrirá automáticamente la guía local en Markdown de la carpeta `academia/`.

---

## 📦 Compilación a Ejecutable Nativo (PyInstaller)

Para generar un ejecutable independiente:
```bash
.\.venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed --name "n8n_Control_Center_Pro" --add-data "academia;academia" --add-data "course_links.json;." main.py
```
El ejecutable se generará en la carpeta `dist/n8n_Control_Center_Pro/`.
