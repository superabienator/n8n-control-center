# ⚡ n8n Control Center Pro
### *Orquestador DevOps, RAG Local (PGVector + Ollama), Túneles Cloudflare y GitOps*
> **Filosofía Vibe Coding**: Construye agentes de IA, RAG y automatizaciones visuales complejas conectando bloques lógicos, con cero fricción técnica y total soberanía sobre tus datos.

---

```text
 ╔═══════════════════════════════════════════════════════════════════════════════════╗
 ║                          n8n CONTROL CENTER PRO ARQUITECTURA                     ║
 ╠═══════════════════════════════════════════════════════════════════════════════════╣
 ║                                                                                   ║
 ║   [ INTERNET ]                                                                    ║
 ║        │                                                                          ║
 ║        ▼                                                                          ║
 ║   [ Cloudflare Quick Tunnel ] ──( https://*.trycloudflare.com )                   ║
 ║        │                                                                          ║
 ║        ▼                                                                          ║
 ║  ┌───────────────┐     ┌─────────────────────┐     ┌───────────────────────────┐  ║
 ║  │   n8n CORE    │ <─> │  POSTGRESQL 16      │ <─> │  OLLAMA (IA LOCAL)        │  ║
 ║  │   (:5678)     │     │  + PGVector (RAG)   │     │  • llama3.2:3b (Chat)     │  ║
 ║  │               │     │  (:5432)            │     │  • nomic-embed-text (Vec) │  ║
 ║  └───────┬───────┘     └─────────────────────┘     └───────────────────────────┘  ║
 ║          │                                                                        ║
 ║          ▼                                                                        ║
 ║   📁 /files <───> 💻 stack/local-files/  (Taller de Archivos y PDFs)             ║
 ║   📁 /backups <─> 💻 stack/backups/      (GitOps & Backups JSON independientes)  ║
 ║                                                                                   ║
 ╚═══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 🌟 Características Principales

| Módulo | Descripción | Beneficio Clave |
| :--- | :--- | :--- |
| **🚦 Semáforo en Vivo** | Monitorización reactiva en tiempo real cada 3 segundos de 4 servicios. | Sabrás al instante si n8n, Postgres, Ollama o el Túnel están activos. |
| **🌐 Túnel Webhook Gratis** | Conexión saliente cifrada a través de Cloudflare Quick Tunnels. | Recibe webhooks de WhatsApp, Stripe o Telegram sin abrir puertos en tu router. |
| **🧠 IA Local (Ollama)** | Inferencia local con `llama3.2:3b` y `nomic-embed-text` a 1 clic. | Privacidad absoluta para tus documentos y **0,00 €** en facturas de API. |
| **📚 Memoria RAG (PGVector)**| Base de datos vectorial integrada en PostgreSQL 16 con extensión `vector`. | Dale a tu IA memoria fotográfica sin alucinaciones. |
| **🐙 GitHub Sync (GitOps)** | Exportación automática de flujos a JSON y sincronización con Git. | Máquina del tiempo para tus automatizaciones y migración entre ordenadores. |
| **🧹 Limpiador en 3 Niveles**| Purga de Docker, vaciado de temporales y Reset Nuclear con confirmación. | Mantén tu disco duro limpio y optimizado sin romper nada. |
| **🎓 Botones `[🎓 Curso]`** | Micro-botones pedagógicos con fallback automático a guías Markdown locales. | Aprende cada concepto con explicaciones sencillas y analogías visuales. |

---

## 🚀 Instalación y Puesta en Marcha (Windows, macOS, Linux)

### Requisitos Previos
1. **Docker Desktop** (o Docker Engine en Linux) en ejecución.
2. **Python 3.10 o superior**.
3. **Git** instalado.

---

### 🪟 En Windows
Abre **PowerShell** en la carpeta del proyecto:
```powershell
# 1. Crear entorno virtual (si no existe)
py -m venv .venv

# 2. Instalar dependencias
.\.venv\Scripts\pip.exe install -r requirements.txt

# 3. Lanzar la aplicación
.\.venv\Scripts\python.exe main.py
```

---

### 🍎 En macOS (Apple Silicon / Intel)
Abre la **Terminal** en la carpeta del proyecto:
```bash
# 1. Crear entorno virtual
python3 -m venv .venv

# 2. Activar e instalar dependencias
source .venv/bin/activate
pip install -r requirements.txt

# 3. Lanzar la aplicación
python main.py
```

---

### 🐧 En Linux (Ubuntu / Debian / Fedora)
Abre tu terminal favorita:
```bash
# 1. Asegurar soporte para Tkinter (si no está instalado)
sudo apt update && sudo apt install -y python3-tk python3-venv

# 2. Crear entorno virtual e instalar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Lanzar la aplicación
python main.py
```

---

## 🎙️ Cómo Crear tu Tutor IA en Google NotebookLM en 1 Minuto

Hemos empaquetado todo el conocimiento del curso en 4 guías Markdown de alto impacto dentro de la carpeta `academia/`. Puedes convertir estos archivos en un **Tutor de Inteligencia Artificial personalizado**, capaz de responder tus dudas por chat o incluso generar un **podcast de audio interactivo**:

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                PASO A PASO: TU TUTOR IA EN NOTEBOOKLM                       │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │                                                                             │
 │  1. Abre tu navegador y ve a: https://notebooklm.google.com/               │
 │                                                                             │
 │  2. Pulsa en "+ Nuevo Cuaderno" y nómbralo: "Academia n8n Control Center"   │
 │                                                                             │
 │  3. En "Fuentes", selecciona "Subir archivos" y arrastra los 4 archivos     │
 │     de la carpeta 'academia/' de tu proyecto:                               │
 │     • 01_Curso_Express_n8n_y_Webhooks.md                                    │
 │     • 02_Curso_Acelerado_RAG_y_Memoria_IA.md                                │
 │     • 03_Curso_IA_Local_Gratis_con_Ollama.md                                │
 │     • 04_Guia_GitHub_Backups_y_Limpiador.md                                 │
 │                                                                             │
 │  4. ¡Listo! NotebookLM analizará todo el contenido al instante.             │
 │     • Puedes pulsar "Generar Guía de Estudio" o "Conversación de Audio".    │
 │     • Haz clic en "Compartir" (arriba a la derecha) y copia el enlace.     │
 │                                                                             │
 │  5. Abre nuestra app, ve a la pestaña "🎓 Configurar Academia" y pega el    │
 │     enlace en los módulos correspondientes.                                 │
 │                                                                             │
 │  👉 ¡A partir de ese momento, cada micro-botón [🎓 Curso] abrirá tu tutor  │
 │     interactivo en vivo en el navegador!                                    │
 │                                                                             │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Credenciales de Conexión Interna para n8n

Al configurar nodos en el canvas de n8n, utiliza estos valores exactos:

| Servicio | Parámetro | Valor para n8n |
| :--- | :--- | :--- |
| **Ollama (IA Local)** | Base URL | `http://ollama:11434` |
| **Ollama Modelos** | Chat / Agentes | `llama3.2:3b` |
| **Ollama Modelos** | Embeddings RAG | `nomic-embed-text` |
| **Postgres PGVector** | Host | `postgres` |
| **Postgres PGVector** | Puerto | `5432` |
| **Postgres PGVector** | Database | `n8n` |
| **Postgres PGVector** | Usuario / Password | `n8n` / `n8n_password` |
| **Postgres PGVector** | SSL | `disable` |

---

## 🧹 Los 3 Niveles del Limpiador

- 🟦 **Nivel 1 - Purga de Basura (Azul)**:
  Ejecuta `docker system prune -f` y `VACUUM FULL;` en PostgreSQL. 100% seguro, recupera espacio y compacta la base de datos sin tocar flujos ni datos.
- 🟧 **Nivel 2 - Vaciar Taller Temporal (Naranja)**:
  Limpia la carpeta `stack/local-files/` (ficheros generados por tus ejecuciones de n8n) y te informa de los Megabytes liberados.
- 🟥 **Nivel 3 - Reset Nuclear (Rojo)**:
  Acción destructiva protegida por confirmación. Destruye los contenedores y volúmenes (`down -v --rmi all`) para dejar la instalación limpia como el primer día.

---

## 📦 Compilación a Ejecutable Nativo (.exe / App)

Si deseas empaquetar la aplicación en un ejecutable autónomo utilizando **PyInstaller**:

```bash
# En Windows:
.\.venv\Scripts\pyinstaller.exe --noconfirm --onedir --windowed --name "n8n_Control_Center_Pro" --add-data "academia;academia" --add-data "course_links.json;." main.py

# En Linux / macOS:
pyinstaller --noconfirm --onedir --windowed --name "n8n_Control_Center_Pro" --add-data "academia:academia" --add-data "course_links.json:." main.py
```
El binario resultante se creará en la carpeta `dist/n8n_Control_Center_Pro/`.

---

## 📄 Licencia y Filosofía
Proyecto desarrollado bajo la filosofía **Vibe Coding**: máxima potencia visual, arquitectura profesional y cero complicaciones técnicas. ¡Feliz automatización!
