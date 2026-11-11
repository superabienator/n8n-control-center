# 🎓 Curso: Arquitectura y Despliegue de n8n con Docker

Bienvenido a la guía oficial de arquitectura de **n8n Control Center Pro**. Este documento detalla la estructura del entorno, el ciclo de vida de los contenedores y las mejores prácticas para un entorno robusto y escalable.

---

## 1. Arquitectura de Componentes
El stack se compone de contenedores intercomunicados en una red de puente aislada (`n8n_network`):
- **n8n Core (`n8n`)**: Orquestador principal de automatizaciones. Corre sobre Node.js y se ejecuta bajo el usuario sin privilegios `node` (UID/GID 1000).
- **PostgreSQL 16 + PGVector (`postgres`)**: Base de datos relacional y motor vectorial. Almacena configuraciones, ejecuciones, credenciales cifradas y tablas de embeddings para RAG.
- **Ollama (`ollama`)**: Servidor local de inferencia para Modelos de Lenguaje Grande (LLMs) y embeddings sin enviar datos a la nube.
- **Cloudflare Quick Tunnel (`n8n_tunnel`)**: Proxy inverso efímero y seguro para exponer webhooks a internet con cifrado TLS automático.

---

## 2. Variables de Entorno Clave (`stack/.env`)
| Variable | Valor por Defecto | Propósito |
| :--- | :--- | :--- |
| `DB_TYPE` | `postgresdb` | Define PostgreSQL como motor principal en vez de SQLite. |
| `POSTGRES_USER` | `n8n` | Usuario administrador de la base de datos. |
| `POSTGRES_PASSWORD` | `n8n_password` | Contraseña cifrada en tránsito dentro de la red Docker. |
| `N8N_DEFAULT_BINARY_DATA_MODE` | `filesystem` | Guarda archivos pesados en disco (`/files`), no en RAM ni DB. |
| `EXECUTIONS_DATA_PRUNE` | `true` | Habilita la purga automática de ejecuciones antiguas. |
| `EXECUTIONS_DATA_MAX_AGE` | `72` | Elimina ejecuciones tras 72 horas para ahorrar espacio. |
| `WEBHOOK_URL` | `http://localhost:5678/` | URL base para generar enlaces de webhook en flujos. |

---

## 3. Acceso a la Interfaz Web
Una vez iniciado el stack:
- **URL Local**: `http://localhost:5678`
- **Primer inicio**: n8n te solicitará crear la cuenta de propietario inicial (email y contraseña).
- **Credenciales en n8n**:
  - Para conectar Postgres desde un nodo de base de datos o vector store:
    - Host: `postgres`
    - Puerto: `5432`
    - Base de datos: `n8n`
    - Usuario: `n8n`
    - Password: `n8n_password`
  - Para conectar Ollama:
    - Host / Base URL: `http://ollama:11434`
