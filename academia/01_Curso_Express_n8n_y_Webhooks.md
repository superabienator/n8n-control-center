# 🎓 Curso Express: n8n desde Cero y el Secreto de los Webhooks

Bienvenido al mundo del **Vibe Coding** con n8n. Aquí no necesitas memorizar código ni aprender sintaxis complejas. Diseñarás automatizaciones visuales conectando bloques lógicos, como si estuvieras jugando con piezas de Lego.

---

## 🧱 1. ¿Qué es n8n? El Juego de Legos Digital

Imagina que tienes una fábrica automatizada en tu pantalla. En n8n, cada automatización se llama **Workflow** (Flujo de Trabajo) y está compuesta por dos tipos de piezas:

```text
 ┌─────────────────────────┐         ┌─────────────────────────┐
 │   PIEZA 1: DISPARADOR   │ ──────> │    PIEZA 2: ACCIÓN      │
 │        (Trigger)        │         │        (Action)         │
 │ "¿CUÁNDO EMPIEZA TODO?" │         │   "¿QUÉ HACEMOS AHORA?" │
 └─────────────────────────┘         └─────────────────────────┘
```

1. **Disparadores (Triggers / Piezas de Inicio)**:
   - Responden a la pregunta: *¿Cuándo debe despertarse mi flujo?*
   - Ejemplos: "Todos los días a las 9:00 AM", "Cuando me llegue un correo a Gmail", "Cuando alguien rellene un formulario".
2. **Acciones (Actions / Piezas de Ejecución)**:
   - Responden a la pregunta: *¿Qué debe hacer mi flujo a continuación?*
   - Ejemplos: "Guarda estos datos en Google Sheets", "Pásaselo a la IA para que lo resuma", "Manda un mensaje por Telegram".

---

## 🔔 2. ¿Qué es un Webhook? La Metáfora del Timbre de Casa

Para entender qué es un Webhook, comparemos dos formas de esperar al cartero:

```text
❌ MÉTODO ANTIGUO: SONDEO (Polling)
Tú sales a la puerta de tu casa cada 20 segundos a mirar si ha llegado una carta.
Gastas energía, te cansas y la mayoría de las veces no hay nada nuevo.

✅ MÉTODO MODERNO: WEBHOOK (El Timbre)
Tú te sientas cómodamente en el sofá a leer o ver una serie.
Cuando el cartero llega, simplemente TOCA EL TIMBRE. Tú sólo te levantas cuando suena.
```

Un **Webhook** es exactamente el timbre digital de tu flujo de n8n. Servicios como Stripe, WhatsApp, Telegram, Typeform o Shopify tocan ese timbre enviándote una notificación HTTP en el mismo milisegundo en que ocurre una compra o llega un mensaje.

---

## 🌐 3. El Problema de "localhost" y el Botón Mágico del Túnel

Cuando ejecutas n8n en tu ordenador, su dirección es:
👉 `http://localhost:5678`

`localhost` significa literalmente **"esta computadora y nadie más"**. Tu router de casa tiene un escudo (firewall) que impide que nadie en internet pueda ver tu ordenador. 

Si le dices a Stripe o a WhatsApp: *"Oye, cuando alguien compre, mándame los datos a http://localhost:5678"*, no funcionará jamás porque los servidores de Stripe no pueden entrar en tu red WiFi.

### ⚡ La Solución: El Botón "Iniciar Túnel Cloudflare"
En **n8n Control Center Pro**, dentro del **Panel Principal**, verás la sección:
> **"🌐 Túnel Webhook Gratuito (Cloudflare Quick Tunnel)"**

Al hacer un solo clic en **"⚡ Iniciar Túnel Cloudflare"**:
1. Nuestra app levanta un túnel seguro y cifrado con la red global de Cloudflare.
2. Te otorga un subdominio público legítimo en internet (ejemplo: `https://mi-tunel-temporal.trycloudflare.com`).
3. Actualiza de inmediato la variable `WEBHOOK_URL` de tu n8n y lo recarga.
4. **Copia la dirección directamente a tu portapapeles.**

¡Ahora cualquier servicio del planeta puede tocar el timbre de tu n8n sin que tengas que abrir puertos peligrosos en tu router!

---

## 🛠️ 4. Ejercicio Práctico de 5 Minutos: Tu Primer Flujo Webhook

Vamos a construir un flujo real que reciba un mensaje desde el exterior y guarde un archivo de texto en tu disco duro.

### Paso 1: Iniciar el Stack y el Túnel
1. Abre **n8n Control Center Pro**.
2. En la pestaña **"Panel Principal"**, pulsa **"▶️ Iniciar Stack Base"**.
3. Espera 10 segundos a que los indicadores de **n8n** y **Postgres** se pongan en verde.
4. Pulsa **"⚡ Iniciar Túnel Cloudflare"**. Verás cómo la consola captura tu URL pública y la copia al portapapeles.
5. Pulsa **"🌐 Abrir n8n en el Navegador"** (`http://localhost:5678`).

### Paso 2: Crear el Flujo en n8n
1. En n8n, haz clic en **"Add workflow"** (arriba a la derecha).
2. Haz clic en **"Add first step"** y busca el nodo **Webhook**.
3. Configúralo así:
   - **HTTP Method**: `POST`
   - **Path**: `notificacion-express`
   - **Response Mode**: `When Last Node Finishes`
4. Observa que el nodo te muestra dos URLs. Selecciona la pestaña **"Production URL"** o **"Test URL"**. Verás que ya empieza por tu enlace seguro de Cloudflare:
   `https://tu-subdominio.trycloudflare.com/webhook-test/notificacion-express`

### Paso 3: Guardar el mensaje en el Taller Local (`/files`)
Recuerda que nuestra aplicación mapea la carpeta de tu ordenador `stack/local-files/` directamente como `/files` dentro de n8n.
1. Haz clic en el botón `+` a la derecha del nodo Webhook.
2. Añade el nodo **"Write to Disk"** (o **"Edit Fields"** para formatear el texto y luego **"Write Binary File"**):
   - **File Path**: `/files/mi_primer_mensaje.txt`
   - **Data**: `Mensaje recibido con éxito desde el exterior: {{ $json.body.mensaje }}`
3. Haz clic en **"Save"** en el flujo.

### Paso 4: Disparar el Timbre
1. En el nodo Webhook, pulsa el botón **"Listen for Test Event"**. n8n se quedará escuchando pacientemente.
2. Abre una terminal de PowerShell o la consola de tu navegador y lanza esta petición:
   ```bash
   curl -X POST https://tu-subdominio.trycloudflare.com/webhook-test/notificacion-express -H "Content-Type: application/json" -d "{\"mensaje\": \"¡Hola n8n, mi túnel funciona perfecto!\"}"
   ```
3. ¡BAM! Verás cómo el nodo se ilumina en verde en n8n.
4. Ve a la carpeta de tu proyecto en tu ordenador:
   📁 `stack/local-files/mi_primer_mensaje.txt`
   ¡Abre el archivo y verás el texto guardado físicamente en tu disco duro!

---

## 🎯 Resumen para Recordar
- **Trigger**: El evento que enciende la mecha.
- **Action**: Las tareas que se ejecutan una tras otra.
- **Webhook**: El timbre para que internet te hable en tiempo real.
- **Túnel Cloudflare**: El puente que conecta el mundo exterior con tu ordenador sin riesgos.
- **Carpeta `/files`**: El puente entre los archivos de n8n y tu disco local (`stack/local-files/`).
