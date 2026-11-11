# 🎓 Curso: IA Local, Privacidad Total y Cero Costes con Ollama

¿Por qué pagar suscripciones mensuales o facturas imprevistas de API cuando puedes tener una Inteligencia Artificial de última generación corriendo directamente en tu propio ordenador?

En este módulo descubrirás cómo exprimir al máximo **Ollama** dentro de nuestro stack de n8n.

---

## ☁️ vs 💻 1. ¿Cuándo usar la Nube y cuándo IA Local?

No se trata de elegir una y desechar la otra; se trata de usar la herramienta adecuada para cada trabajo:

| Situación | Usa la Nube (OpenAI / Claude / Gemini) | Usa Ollama (Local en tu PC) |
| :--- | :---: | :---: |
| **Privacidad de Datos** | ⚠️ Pasa por servidores de terceros | 🛡️ **100% Privado** (nada sale de tu disco) |
| **Coste por Ejecución** | 💸 Pagas por cada palabra (tokens) | 🆓 **0,00 € para siempre** |
| **Conexión a Internet** | 🌐 Obligatoria (si se cae internet, se para) | 🔌 **Funciona 100% Offline** |
| **Contratos, Nóminas, Salud** | ❌ Riesgoso / Cumplimiento RGPD complejo | ✅ **Ideal y Seguro** |
| **Razonamiento Ultra-Complejo** | 🚀 Modelos masivos de 100B+ parámetros | ⚙️ Modelos optimizados de 3B a 8B |
| **Clasificación y Extracción masiva** | 💸 Muy caro si procesas 100.000 emails | ⚡ **Gratis y a máxima velocidad** |

> **Regla de oro del Vibe Coding**:  
> Usa **Ollama Local** para tus tareas diarias, procesamiento de datos privados, bases de conocimiento RAG y clasificación automática. Deja las APIs de la nube únicamente para razonamientos extremadamente pesados o visión multimodal gigantesca.

---

## 🔌 2. Cómo Conectar Ollama en n8n: El Error Típico de Novato

En muchas guías de internet verás que te dicen: *"Pon http://localhost:11434"*. **¡Cuidado! En entornos Docker profesionales eso fallará.**

```text
¿POR QUÉ FALLA localhost?
Dentro de Docker, cada contenedor es como un piso independiente en un edificio.
Si n8n busca en 'localhost', está buscando en su propio piso (donde no está Ollama).

¿CÓMO SE CONECTAN CORRECTAMENTE?
Ambos contenedores viven en la misma urbanización privada: 'n8n_network'.
Por tanto, n8n solo necesita llamar a su vecino por su nombre:
👉 http://ollama:11434
```

### En n8n:
1. Agrega cualquier nodo de Ollama (ej: `Ollama Chat Model`, `Ollama Model` o `Embeddings Ollama`).
2. En el campo **Base URL**, pon siempre:
   `http://ollama:11434`
3. ¡Listo! La comunicación viaja a velocidad de vértigo por la red interna de tu ordenador.

---

## 👥 3. El Dúo Dinámico: ¿Qué hace el botón "Instalar Kit IA Ligero"?

En la pestaña **"🧠 IA Local & RAG"** de nuestra aplicación tienes un botón mágico:
> **"📦 Instalar Kit IA Ligero (1 Clic)"**

Al pulsarlo, la app descarga y configura automáticamente dos modelos complementarios especialmente elegidos para consumir muy poca memoria RAM/VRAM pero ofrecer máxima precisión:

```text
┌─────────────────────────────────┐        ┌─────────────────────────────────┐
│     MODELO 1: llama3.2:3b       │        │   MODELO 2: nomic-embed-text    │
│    "EL CEREBRO CONVERSADOR"     │        │    "EL TRADUCTOR MATEMÁTICO"    │
├─────────────────────────────────┤        ├─────────────────────────────────┤
│ • Habla fluidamente y razona.   │        │ • No habla ni escribe cartas.   │
│ • Resume textos largos.         │        │ • Lee frases y las convierte en │
│ • Clasifica emails y mensajes.  │        │   coordenadas para PGVector.    │
│ • Devuelve JSON perfecto.       │        │ • Ventana enorme de 8192 tokens.│
│ • Pesa solo ~2.0 GB en disco.   │        │ • Pesa solo ~270 MB en disco.   │
└─────────────────────────────────┘        └─────────────────────────────────┘
```

### ¿Por qué necesitas a ambos?
- Cuando subes un PDF a tu sistema RAG, **`nomic-embed-text`** lee el documento y lo guarda como un mapa de vectores en PostgreSQL.
- Cuando tú haces una pregunta, **`nomic-embed-text`** busca los fragmentos relevantes y se los pasa a **`llama3.2:3b`**.
- Finalmente, **`llama3.2:3b`** redacta una respuesta humana, educada y perfecta para ti.

---

## ⚡ 4. Ejercicio Práctico: Clasificador Automático de Mensajes con Llama 3.2

Hagamos una automatización que reciba cualquier mensaje de un cliente y decida automáticamente si es **URGENTE**, **FACTURACIÓN** o **CONSULTA GENERAL**.

### Paso 1: Levantar Ollama
1. Abre **n8n Control Center Pro**.
2. Ve a la pestaña **"🧠 IA Local & RAG"**.
3. Si el semáforo de Ollama está detenido, pulsa **"⚡ Encender / Apagar Ollama Local"**.
4. Pulsa **"📦 Instalar Kit IA Ligero (1 Clic)"** y observa en la consola inferior cómo se descargan los dos modelos.

### Paso 2: Crear el Flujo en n8n
1. En n8n, crea un nuevo flujo con un nodo disparador **Manual Trigger**.
2. Agrega un nodo **Basic LLM Chain** (o **Information Extractor**).
3. Conéctale el nodo **Ollama Chat Model**:
   - **Base URL**: `http://ollama:11434`
   - **Model**: `llama3.2:3b`
4. En el campo de Prompt / Instrucción de la cadena, escribe:
   ```text
   Eres un clasificador de soporte técnico. Analiza el siguiente mensaje y responde ÚNICAMENTE con una de estas tres palabras: URGENTE, FACTURACIÓN o CONSULTA.

   Mensaje del cliente:
   "Hola, se me ha caído el servidor principal de la oficina y nadie puede trabajar, ayuda por favor."
   ```
5. Pulsa **"Test Step"**.
6. En menos de un segundo, `llama3.2:3b` responderá con:
   👉 `URGENTE`

Sin pagar APIs, sin depender de internet y con total privacidad para los datos de tus clientes.
