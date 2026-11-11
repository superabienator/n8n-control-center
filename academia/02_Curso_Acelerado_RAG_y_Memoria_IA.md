# 🎓 Curso Acelerado: RAG y Memoria de IA (Sin Matemáticas ni Dolores de Cabeza)

¿Alguna vez le has preguntado a ChatGPT sobre un documento privado de tu empresa o las notas de tu curso y te ha respondido con inventos (alucinaciones)? 

En este curso aprenderás a darle a la Inteligencia Artificial una **memoria fotográfica perfecta** utilizando **RAG** y **PGVector**, sin necesidad de saber matemáticas ni álgebra lineal.

---

## 📚 1. ¿Qué es RAG? La Metáfora del Bibliotecario con Post-its

Imagina que contratas a un asesor muy inteligente, pero que nunca ha leído los manuales ni los contratos internos de tu negocio:

```text
SITUACIÓN SIN RAG:
Le haces una pregunta difícil sobre un contrato tuyo de ayer.
Como no lo conoce, improvisa o te dice que no tiene acceso a internet.

SITUACIÓN CON RAG (Retrieval-Augmented Generation):
Antes de que el asesor abra la boca, un BIBLIOTECARIO VELOZ busca en tus archivadores,
encuentra las 3 páginas exactas del contrato, les pega un Post-it fluorescente 
y se las pone en la mesa al asesor diciendo: "Léete esto y responde basándote SOLO en esto".
```

**RAG significa exactamente eso**:
1. **R (Retrieval - Recuperar)**: El bibliotecario busca la información precisa en tus documentos.
2. **A (Augmented - Aumentar)**: Pega esa información encontrada dentro de la pregunta.
3. **G (Generation - Generar)**: El modelo de IA lee la información real y genera una respuesta 100% verídica y sin alucinaciones.

---

## 🧭 2. ¿Qué es una Base de Datos Vectorial? (El Mapa de Ideas)

Una base de datos tradicional busca palabras exactas: si buscas *"automóvil"*, no encontrará documentos que digan *"coche"* o *"vehículo"*.

Una **Base de Datos Vectorial** (como **PGVector** sobre PostgreSQL) no guarda letras: guarda **significados e ideas**. Coloca los conceptos en un mapa mental:
- "Gatito" y "Felino" están pegados en el mapa.
- "Factura impagada" y "Deuda pendiente" están en el mismo barrio.

Cuando el usuario pregunta algo con sus propias palabras, el sistema busca en el mapa los fragmentos de tus documentos que estén en el mismo barrio temático.

---

## 🔑 3. Conexión de Postgres PGVector en n8n

En **n8n Control Center Pro**, ya tenemos un motor PostgreSQL 16 con la extensión `vector` preinstalada y configurada en la red interna de Docker.

Cuando agregues en n8n el nodo **Postgres PGVector Store**, haz clic en **"Create New Credential"** y copia y pega estos datos (los mismos que tienes en la pestaña **"🧠 IA Local & RAG"** de nuestra app):

| Campo en n8n | Valor Exacto | Explicación |
| :--- | :--- | :--- |
| **Host** | `postgres` | Nombre del contenedor en la red interna de Docker (¡no uses localhost!). |
| **Database** | `n8n` | Base de datos principal donde se alojan las tablas vectoriales. |
| **User** | `n8n` | Usuario configurado en el archivo `.env`. |
| **Password** | `n8n_password` | Contraseña interna configurada en el stack. |
| **Port** | `5432` | Puerto estándar de PostgreSQL. |
| **SSL** | `disable` | Desactivado (la conexión es dentro de la red privada interna). |

---

## 🛠️ 4. Ejercicio Práctico: Tu Propio "Chat con tus Documentos"

Vamos a construir un flujo en n8n que lea un documento, lo guarde en la memoria vectorial y te permita hacerle preguntas por chat.

### Paso 1: Poner el documento en el Taller
1. Busca un archivo PDF o un documento de texto cualquiera (por ejemplo `politica_empresa.txt` o `guia.pdf`).
2. Cópialo dentro de la carpeta de tu proyecto:
   📁 `stack/local-files/mi_documento.txt`
   *(Recuerda que n8n ve esta carpeta con la ruta `/files/mi_documento.txt`)*.

### Paso 2: Crear el Flujo de Ingestión (El Bibliotecario)
1. En n8n, crea un nuevo flujo y añade el nodo de inicio **Manual Trigger** (o un Webhook).
2. Añade el nodo **"Read / Write Files from Disk"**:
   - **Operation**: `Read`
   - **File Path**: `/files/mi_documento.txt`
3. Conecta el nodo **"Default Data Loader"** o **"Text Splitter"**:
   - Este nodo trocea el documento largo en pequeños "Post-its" (por ejemplo, fragmentos de 500 caracteres) para que el bibliotecario pueda encontrar datos específicos.
4. Conecta el nodo **"Postgres PGVector Store"**:
   - Selecciona la credencial que creamos antes (`Host: postgres`).
   - Nombre de la tabla: `documentos_rag`.
5. Conecta a la entrada de Embeddings del nodo Postgres el nodo **"Embeddings Ollama"**:
   - **Base URL**: `http://ollama:11434`
   - **Model**: `nomic-embed-text`
6. Pulsa **"Test Step"** o ejecuta el flujo. En un par de segundos, todo tu documento habrá sido transformado en vectores y guardado en PostgreSQL.

### Paso 3: Crear el Agente de Chat Inteligente
1. En el mismo flujo (o en uno nuevo), añade el nodo disparador **"When chat message received"** (Chat Trigger de n8n).
2. Conecta el nodo **"AI Agent"** (o **"Question and Answer Chain"**).
3. Conéctale sus 3 acompañantes:
   - **Chat Model**: Nodo `Ollama Chat Model` (Base URL: `http://ollama:11434`, Modelo: `llama3.2:3b`).
   - **Vector Store Tool**: Nodo `Postgres PGVector Store` conectado a la tabla `documentos_rag` que llenamos en el Paso 2.
   - **Memory**: Nodo `Window Buffer Memory` (para que recuerde lo que le dijiste en el mensaje anterior).
4. Haz clic en el botón inferior **"Chat"** de n8n.
5. Pregúntale cualquier detalle específico que sólo aparezca en tu documento:
   💬 *"¿Cuáles son las normas de vacaciones según el documento?"*
6. ¡Magia pura! El bibliotecario buscará los fragmentos exactos en PGVector, se los entregará a Llama 3.2 y el agente te responderá con precisión quirúrgica citando tu documento.

---

## 💡 Consejo Pro de Vibe Coding
Si necesitas actualizar el documento con nueva información, simplemente vuelve a ejecutar el flujo de ingestión. La memoria de tu IA siempre estará al día sin gastar ni un solo céntimo en APIs.
