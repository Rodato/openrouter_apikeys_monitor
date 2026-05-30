# 🤖 Telegram Bot Interactivo

Gestiona tus proyectos de OpenRouter directamente desde Telegram.

## Comandos disponibles

### `/start`
Muestra el menú de ayuda con todos los comandos

### `/list`
📋 Lista todas tus API keys de OpenRouter con su uso actual

### `/status`
✅ Muestra los proyectos que estás monitoreando actualmente

### `/add`
➕ Agregar un proyecto al monitoreo

**Formato:**
```
/add nombre_key | Nombre Bonito | umbral_usd
```

**Ejemplo:**
```
/add AMABot_Bruno | Chat Bot AMA | 200.0
```

### `/remove`
🗑️ Remover un proyecto del monitoreo

**Formato:**
```
/remove nombre_key
```

**Ejemplo:**
```
/remove AMABot_Bruno
```

### `/threshold`
⚙️ Cambiar el umbral de alerta de un proyecto

**Formato:**
```
/threshold nombre_key | nuevo_umbral
```

**Ejemplo:**
```
/threshold AMABot_Bruno | 250.0
```

### `/report`
📊 Enviar reporte de estado inmediato (sin esperar a las 9 AM)

---

## Ejemplo de uso

```
Tú: /list

Bot: 📋 Tus API keys en OpenRouter (13):

1. facturacion_plural
   💰 $9.1538 este mes ($9.1538 total)

2. siigoAgent
   💰 $2.6899 este mes ($2.6899 total)

3. AMABot_Bruno
   💰 $0.1214 este mes ($0.6580 total)
...

Para agregar al monitoreo: /add


Tú: /add AMABot_Bruno | Chat Bot AMA | 200

Bot: ✅ Proyecto agregado:

Chat Bot AMA
Key: AMABot_Bruno
Umbral: $200.00/mes

Usa /status para verificar.


Tú: /status

Bot: ✅ Proyectos monitoreados (1):

• Chat Bot AMA
  Key: AMABot_Bruno
  Umbral: $200.00/mes

Comandos: /add /remove /threshold /report


Tú: /report

Bot: 📊 Generando reporte...

📊 OpenRouter — Estado de proyectos
🕐 2026-05-30 15:30

💳 Créditos totales: $450.00 | Consumido: $25.50 | Disponible: $424.50

Uso mensual por proyecto (activos esta semana):
✅ Chat Bot AMA — $0.12 / $200.00 (0.1%)
...
```

---

## Deployment

### Opción 1: Bot + Scheduler (Recomendado)

Correr ambos servicios:
- Scheduler envía reportes diarios a las 9 AM
- Bot responde a comandos 24/7

**En Railway:**
Crea 2 servicios desde el mismo repo:

**Servicio 1:** openrouter-scheduler
```
Start Command: python3 src/scheduler.py
```

**Servicio 2:** openrouter-bot
```
Start Command: python3 src/telegram_bot.py
```

Ambos usan las mismas variables de entorno.

### Opción 2: Solo Bot (interactivo)

Si prefieres controlar todo manualmente desde Telegram:

**Railway Start Command:**
```
python3 src/telegram_bot.py
```

Luego usa `/report` cuando quieras ver el estado.

---

## Seguridad

El bot **solo responde** a mensajes del `TELEGRAM_CHAT_ID` configurado. Otros usuarios no pueden interactuar con él.

Para permitir múltiples usuarios (equipo), necesitarías modificar el código para aceptar una lista de chat IDs autorizados.

---

## Testing local

```bash
# Asegúrate de tener las variables en .env
python3 src/telegram_bot.py
```

El bot se queda corriendo y responde a tus mensajes en tiempo real.

Ctrl+C para detener.
