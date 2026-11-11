# 🎓 Guía Definitiva: Mantenimiento, Autoarranque del Sistema y Plantillas Nativas

En esta guía aprenderás cómo configurar el inicio automático de **n8n Control Center Pro** con tu sistema operativo y cómo activar las 3 plantillas nativas de workflows generadas en tu instalación.

---

## 🚀 1. Autoarranque del Sistema (Windows, Linux y macOS)

El módulo `autostart_manager.py` permite que la suite se inicie de forma silenciosa y automática en segundo plano cada vez que enciendas tu ordenador o inicies sesión.

### ¿Cómo funciona en cada sistema operativo?
- **🪟 Windows**:  
  Registra la clave de ejecución automática en el registro de usuario:  
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` bajo el nombre `"n8nControlCenter"`.
- **🐧 Linux**:  
  Crea un archivo estándar de autoarranque de escritorio en:  
  `~/.config/autostart/n8ncontrolcenter.desktop`.
- **🍎 macOS**:  
  Crea un agente de servicio de usuario LaunchAgent en:  
  `~/Library/LaunchAgents/com.n8ncontrol.plist`.

### Cómo Activar o Desactivar el Autoarranque:
1. **Desde la Interfaz Gráfica (`main.py`)**:
   - En la pestaña **"🐙 GitHub Sync & Ajustes"** o **"🧹 Limpiador"**, activa o desactiva el interruptor:
     `[✓] Iniciar n8n Control Center Pro automáticamente al encender el equipo`.
2. **Desde Python mediante código**:
   ```python
   from autostart_manager import AutostartManager

   manager = AutostartManager()
   
   # Para activar:
   manager.enable_autostart()

   # Para desactivar:
   manager.disable_autostart()

   # Para comprobar estado:
   print("¿Autoarranque activo?:", manager.is_autostart_enabled())
   ```

---

## 📦 2. Cómo Cargar las 3 Plantillas Nativas de n8n

Dentro de la carpeta `stack/backups/workflows/` tienes 3 flujos listos para producción diseñados para nuestro stack:

```text
stack/backups/workflows/
├── 01_Agente_IA_Ollama_Local.json          # Agente Conversacional con Llama 3.2
├── 02_RAG_PGVector_Ollama_Embeddings.json  # Memoria Vectorial RAG con Postgres
└── 03_Test_Webhook_Tunel.json              # Webhook público para pruebas con Cloudflare
```

### Método Rápido (En 1 Clic desde la Aplicación):
1. Inicia **n8n Control Center Pro**.
2. Asegúrate de que el Stack Base esté en marcha (**"▶️ Iniciar Stack Base"**).
3. Ve a la pestaña **"🐙 GitHub Sync"**.
4. Haz clic en el botón **"📥 Restaurar / Importar Flujos desde GitHub"**.
5. ¡Listo! El contenedor de n8n absorberá automáticamente los 3 archivos JSON y aparecerán activos en tu panel de control de n8n (`http://localhost:5678`).

### Método Manual (Desde el Canvas de n8n):
1. Abre n8n en tu navegador (`http://localhost:5678`).
2. En el menú superior de la derecha de tu flujo, pulsa en los tres puntos `⋮` y selecciona **"Import from File"** (o arrastra directamente el archivo `.json` sobre el lienzo).
3. Selecciona cualquiera de las plantillas desde `stack/backups/workflows/`.

---

## 🧠 3. Detalle de las 3 Plantillas Incluidas

### 1. `01_Agente_IA_Ollama_Local.json`
- **¿Qué hace?**  
  Crea un chat de IA interactivo en n8n alimentado por `llama3.2:3b` corriendo en tu máquina con Ollama.
- **Componentes**:
  - `When chat message received` (Disparador de chat).
  - `AI Agent` (Orquestador con memoria de conversación).
  - `Ollama Chat Model` conectado a `http://ollama:11434`.
  - `Window Buffer Memory` (Recuerda los últimos 10 mensajes del diálogo).

### 2. `02_RAG_PGVector_Ollama_Embeddings.json`
- **¿Qué hace?**  
  Implementa un agente RAG (Retrieval-Augmented Generation) que responde buscando primero información semántica en la tabla `documentos_rag` de PostgreSQL con PGVector.
- **Componentes**:
  - `AI Agent` + `Vector Store Tool`.
  - `Postgres PGVector Store` conectado a la base de datos interna `postgres:5432`.
  - `Ollama Embeddings` con el modelo `nomic-embed-text` (`http://ollama:11434`).

### 3. `03_Test_Webhook_Tunel.json`
- **¿Qué hace?**  
  Permite probar de forma inmediata el funcionamiento del **Túnel de Cloudflare**.
- **Cómo probarlo**:
  1. Enciende el túnel en la app (**"⚡ Iniciar Túnel Cloudflare"**).
  2. Activa este flujo en n8n.
  3. Lanza una petición con tu URL de Cloudflare:
     ```bash
     curl -X POST https://tu-subdominio.trycloudflare.com/webhook/test-webhook \
          -H "Content-Type: application/json" \
          -d '{"prueba": "conexion_exitosa"}'
     ```
  4. Recibirás una respuesta JSON inmediata confirmando que el túnel está operativo.

---

## 🧹 4. Buenas Prácticas de Mantenimiento

- **Uso Mensual del Nivel 1 (Azul)**: Pulsa el botón para ejecutar `docker system prune` y el `VACUUM FULL` en PostgreSQL para que tu base de datos permanezca compacta y rápida.
- **Vaciado del Taller (Nivel 2 - Naranja)**: Si procesas archivos binarios grandes, vacía el taller temporal periódicamente para liberar espacio en disco.
