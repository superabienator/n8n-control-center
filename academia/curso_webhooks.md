# 🎓 Curso: Webhooks Públicos y Túneles con Cloudflare

Los webhooks son el corazón de las automatizaciones basadas en eventos. Permiten que servicios externos (como WhatsApp API, Stripe, GitHub, Shopify o pasarelas de pago) notifiquen a n8n en tiempo real.

---

## 1. El Desafío de localhost
Cuando ejecutas n8n en tu computadora local:
- Tu IP suele ser privada o estar tras un router NAT/CGNAT.
- Los servicios de internet no pueden enviar solicitudes HTTP POST a `http://localhost:5678/webhook/...`.
- Abrir puertos en tu router (port forwarding) expone tu red y es peligroso sin un cortafuegos dedicado.

---

## 2. Solución: Cloudflare Quick Tunnels
**n8n Control Center Pro** incluye un contenedor oficial con `cloudflare/cloudflared`:
1. Establece una conexión saliente segura (sin abrir puertos entrantes en tu router) hacia la red global de Cloudflare.
2. Te asigna un subdominio seguro temporal: `https://[aleatorio].trycloudflare.com`.
3. Todo el tráfico entrante a ese subdominio es redirigido por un túnel cifrado hacia el contenedor `n8n:5678`.

---

## 3. Flujo Automatizado en la Aplicación
Cuando presionas **"Iniciar Túnel Cloudflare"**:
1. Se levanta el contenedor `n8n_tunnel`.
2. Se monitorean los registros hasta capturar la URL generada (`https://*.trycloudflare.com`).
3. Se actualiza el parámetro `WEBHOOK_URL` en `stack/.env`.
4. Se reinicia el contenedor de n8n para que cargue la nueva URL base.
5. La URL se copia automáticamente a tu portapapeles.

---

## 4. Cómo Probar un Webhook en n8n
1. En tu flujo de n8n, añade el nodo **Webhook**.
2. Verás que la "Production URL" y "Test URL" ahora usan tu dominio de Cloudflare.
3. Haz clic en "Listen for Test Event".
4. Envía un `curl` o petición desde Postman:
   ```bash
   curl -X POST https://tu-subdominio.trycloudflare.com/webhook-test/mi-endpoint \
        -H "Content-Type: application/json" \
        -d '{"mensaje": "Hola n8n!"}'
   ```
5. ¡Verás los datos recibidos instantáneamente en el canvas de n8n!
