# 🎓 Curso: Git Sync, Backups y GitOps para n8n

Tener tus flujos de n8n versionados en un repositorio Git como GitHub o GitLab es una práctica profesional esencial para evitar pérdida de datos, posibilitar rollbacks y migrar flujos entre entornos de Desarrollo y Producción.

---

## 1. El Comando Oficial de Exportación de n8n
Dentro del contenedor de n8n, existe una potente CLI nativa:
```bash
docker exec -u node n8n n8n export:workflow --backup --output=/backups/workflows/
```
- El parámetro `--backup` exporta cada flujo en su propio archivo JSON independiente.
- El nombre del archivo incluye el ID del flujo y su nombre legible.
- `/backups/workflows/` está mapeado como volumen en `stack/backups/workflows/` en tu máquina anfitriona.

---

## 2. Automatización con Git
La función **"Exportar y Subir Flujos a GitHub"**:
1. Ejecuta la exportación dentro del contenedor de n8n.
2. Agrega los archivos creados o modificados:
   ```bash
   git add stack/backups/workflows/
   ```
3. Genera un commit con fecha y hora:
   ```bash
   git commit -m "Auto-backup flujos n8n - YYYY-MM-DD HH:MM:SS"
   ```
4. Hace `git push` a tu repositorio remoto configurado.

---

## 3. Restauración e Importación de Flujos
Si reinstalas tu equipo o estás en otra máquina:
1. Clonas el repositorio o haces `git pull`.
2. Presionas **"Restaurar / Importar Flujos desde GitHub"**.
3. La aplicación ejecuta:
   ```bash
   docker exec -u node n8n n8n import:workflow --separate --input=/backups/workflows/
   ```
4. Todos tus flujos se cargan instantáneamente en la base de datos de n8n listos para funcionar.
