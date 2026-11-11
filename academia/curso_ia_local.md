# 🎓 Curso: IA Local, Agentes y RAG con Ollama & PGVector

Aprende a construir flujos de inteligencia artificial y agentes autónomos 100% privados, sin pagar por tokens ni enviar datos a APIs externas.

---

## 1. ¿Por qué IA Local?
- **Privacidad Total**: Documentos internos, historiales de clientes y bases de datos sensibles no salen de tu equipo.
- **Cero Costes por Token**: Ejecuta millones de inferencias gratis.
- **Baja Latencia**: Comunicación directa dentro de la red Docker interna (`n8n_network`).

---

## 2. Modelos Recomendados (Kit Ligero)
Al hacer clic en **"Instalar Kit IA Ligero (1 Clic)"**, la aplicación descarga:
1. **`llama3.2:3b`** (Meta):
   - Modelo ultrarrápido optimizado para agentes conversacionales, clasificación y extracción JSON.
   - Requiere menos de 4 GB de VRAM (o RAM en CPU).
2. **`nomic-embed-text`** (Nomic AI):
   - Modelo de embeddings de texto de alta fidelidad con ventana de contexto de 8192 tokens.
   - Ideal para vectorizar PDFs, documentación y crear bases de conocimiento RAG.

---

## 3. Conexión con PostgreSQL + PGVector
El contenedor `postgres` incluye la extensión `pgvector` inicializada mediante `stack/init.sql`:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Configuración en n8n:
1. En n8n, añade el nodo **AI Agent** o **Question and Answer Chain**.
2. Conecta el nodo **Ollama Chat Model**:
   - Base URL: `http://ollama:11434`
   - Model: `llama3.2:3b`
3. Conecta el nodo **Postgres PGVector Store**:
   - Credenciales Postgres:
     - Host: `postgres`
     - Database: `n8n`
     - User: `n8n`
     - Password: `n8n_password`
     - Port: `5432`
   - Conecta a su entrada de Embeddings el nodo **Embeddings Ollama**:
     - Base URL: `http://ollama:11434`
     - Model: `nomic-embed-text`
4. ¡Tu pipeline RAG completo estará operativo de extremo a extremo!
