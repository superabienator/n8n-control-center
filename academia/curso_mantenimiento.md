# 🎓 Curso: Mantenimiento, Optimización y Ciclo de Vida del Stack

Con el tiempo, las instancias de n8n con alto volumen de ejecuciones pueden acumular datos en disco (archivos binarios temporales, historial de ejecuciones en PostgreSQL y capas de contenedores no utilizadas en Docker).

---

## 1. Nivel 1: Purga de Basura y Optimización de Base de Datos
- **Docker System Prune**:
  ```bash
  docker system prune -f
  ```
  Elimina contenedores detenidos, redes huérfanas e imágenes intermedias sin etiqueta.
- **Postgres VACUUM FULL**:
  Postgres marca las filas eliminadas (dead tuples) pero no devuelve inmediatamente el espacio al sistema operativo.
  ```sql
  VACUUM FULL;
  ```
  Reconstruye físicamente las tablas e índices de la base de datos de n8n, compactando el almacenamiento y acelerando las consultas.

---

## 2. Nivel 2: Limpieza del Taller de Archivos Temporales
Los flujos que manipulan imágenes, PDFs o ficheros CSV almacenan datos binarios en `stack/local-files/` (mapeado a `/files` en el contenedor).
- **Vaciar Taller Temporal**:
  Calcula el espacio total ocupado, elimina archivos temporales antiguos y deja una carpeta limpia y lista para nuevas ejecuciones.

---

## 3. Nivel 3: Nuclear Reset / Desinstalación Completa
Útil cuando deseas empezar desde cero o limpiar por completo el proyecto:
- Detiene todos los contenedores (`n8n`, `postgres`, `ollama`, `n8n_tunnel`).
- Elimina los volúmenes de datos (`docker compose down -v --rmi all`).
- Elimina la carpeta `stack/` y regenera la plantilla inicial limpia.
- **Advertencia**: Esta acción elimina las cuentas de usuario locales y la base de datos de PostgreSQL. Asegúrate de haber realizado un backup en GitHub antes de proceder.
