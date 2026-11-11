# 🎓 Guía Definitiva: GitOps, Máquina del Tiempo de Flujos y Mantenimiento Seguro

Construir automatizaciones increíbles requiere tiempo e ingenio. Lo peor que le puede pasar a un creador es perder sus flujos porque se estropeó el ordenador o no saber cómo llevarse su trabajo a otro equipo.

En esta guía aprenderás a usar la **Máquina del Tiempo de n8n** con GitHub y a mantener tu sistema siempre rápido y limpio sin miedo a romper nada.

---

## ⏳ 1. La Máquina del Tiempo de tus Flujos (GitHub Sync)

Por defecto, n8n guarda los flujos dentro de la base de datos de PostgreSQL en tu disco duro. Pero, ¿qué pasa si cambias de portátil o el disco falla?

Para evitar desastres, creamos la pestaña **"🐙 GitHub Sync"**:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      CÓMO FUNCIONA LA MÁQUINA DEL TIEMPO               │
 ├────────────────────────────────────────────────────────────────────────┤
 │                                                                        │
 │  [ Tu n8n ] ──( 1 Clic: Exportar )──> [ Carpeta stack/backups/ ]       │
 │                                                  │                     │
 │                                            ( Git Commit & Push )       │
 │                                                  ▼                     │
 │                                         [ Nube Privada GitHub ]        │
 │                                                  │                     │
 │  [ Otro Ordenador ] <──( 1 Clic: Importar )──────┘                     │
 │                                                                        │
 └────────────────────────────────────────────────────────────────────────┘
```

### 📤 El Botón "Exportar y Subir Flujos a GitHub"
Al hacer un solo clic:
1. La aplicación le pide a n8n: *"Extrae todos mis flujos y conviértelos en archivos JSON limpios e independientes"*.
2. Los guarda en la carpeta física `stack/backups/workflows/`.
3. Prepara un paquete con Git, le estampa la fecha y hora actual y lo sube de forma segura a tu repositorio de GitHub.

### 📥 El Botón "Restaurar / Importar Flujos desde GitHub"
Imagina que te vas de viaje con otro portátil o instalas el programa desde cero:
1. Clonas tu proyecto y abres **n8n Control Center Pro**.
2. Pulsas **"Restaurar / Importar Flujos desde GitHub"**.
3. La aplicación descarga los últimos cambios (`git pull`) y le ordena a n8n que absorba todos los archivos JSON.
4. ¡Tus automatizaciones aparecen en tu pantalla tal y como las dejaste!

> **💡 El Interruptor Mágico**: Activa el switch *"Auto-guardar en GitHub al detener n8n"*. Cada vez que cierres la app o apagues el stack, se creará una copia de seguridad en la nube automáticamente sin que tengas que acordarte.

---

## 🧹 2. El Limpiador en 3 Niveles: Guía Sin Miedo a Romper Nada

Con el tiempo, Docker acumula versiones antiguas de imágenes y n8n va guardando historiales de ejecuciones. En la pestaña **"🧹 Limpiador"** tienes 3 niveles de mantenimiento diseñados con colores claros según su impacto:

---

### 🔹 Nivel 1: Purga de Basura & Compactación (Botón Azul)
*La metáfora: Pasar el plumero y barrer el salón.*

- **¿Qué hace técnicamente?**
  - Ejecuta `docker system prune -f` (borra contenedores detenidos e imágenes intermedias descartadas).
  - Lanza la instrucción `VACUUM FULL;` dentro de PostgreSQL (reorganiza físicamente los datos en disco para recuperar espacio sin tocar tus registros).
- **¿Qué riesgo tiene?**
  - **Cero riesgo (100% seguro)**. No borra ninguno de tus flujos, no borra credenciales y no borra archivos.
- **¿Cuándo usarlo?**
  - Una vez al mes, o cuando sientas que Docker está ocupando más espacio de la cuenta.

---

### 🔸 Nivel 2: Vaciar Taller Temporal (Botón Naranja)
*La metáfora: Vaciar la papelera de reciclaje de tu mesa de trabajo.*

- **¿Qué hace técnicamente?**
  - Escanea la carpeta `stack/local-files/` (que es la carpeta `/files` donde n8n descarga PDFs, imágenes intermedias o archivos temporales de tus flujos).
  - Elimina esos archivos sueltos y calcula exactamente cuántos Megabytes ha liberado.
- **¿Qué riesgo tiene?**
  - **Muy bajo**. No toca tus flujos ni tus credenciales. Solo borra los ficheros temporales descargados por las automatizaciones.
- **¿Cuándo usarlo?**
  - Si tienes flujos que descargan vídeos, procesan lotes grandes de fotos o generan reportes pesados y quieres liberar gigas rápidamente.

---

### 💥 Nivel 3: Reset Nuclear / Desinstalación (Botón Rojo con Confirmación)
*La metáfora: Formatear y empezar desde cero como el primer día.*

- **¿Qué hace técnicamente?**
  - Apaga todos los contenedores y destruye por completo los volúmenes de datos (`docker compose down -v --rmi all`).
  - Borra la base de datos de PostgreSQL y restablece las plantillas base.
- **¿Qué riesgo tiene?**
  - **ALTO / DESTRUCTIVO**. Borra la cuenta de usuario de n8n, las credenciales guardadas y los flujos locales que no hayas subido a GitHub. Por eso la aplicación te mostrará un cuadro de confirmación para evitar cualquier error accidental.
- **¿Cuándo usarlo?**
  - Si olvidaste tu contraseña de n8n y no puedes entrar.
  - Si quieres hacer una limpieza total para empezar un proyecto nuevo desde cero (recuerda que si antes pulsaste *"Exportar a GitHub"*, podrás recuperar todos tus flujos en 1 clic después del reinicio).

---

## 🏆 Resumen de Seguridad
| Nivel | Color | ¿Borra mis flujos? | ¿Borra mis credenciales? | ¿Para qué sirve? |
| :---: | :---: | :---: | :---: | :--- |
| **Nivel 1** | 🟦 Azul | ❌ No | ❌ No | Optimiza Docker y compacta PostgreSQL. |
| **Nivel 2** | 🟧 Naranja | ❌ No | ❌ No | Vacía los archivos temporales descargados. |
| **Nivel 3** | 🟥 Rojo | ⚠️ Sí (a menos que estén en Git) | ⚠️ Sí | Reset total a estado de fábrica. |
