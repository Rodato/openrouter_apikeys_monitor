# Deploy a Railway

Railway es la forma más simple de tener el monitor corriendo 24/7 con reportes diarios automáticos.

## 🚀 Setup rápido (5 minutos)

### 1. Crear proyecto en Railway

1. Ve a [railway.app](https://railway.app) e inicia sesión con GitHub
2. Click en **New Project** → **Deploy from GitHub repo**
3. Selecciona `Rodato/openrouter_apikeys_monitor`
4. Railway detectará automáticamente el Dockerfile

### 2. Configurar variables de entorno

En el dashboard de Railway, ve a **Variables** y agrega:

```
OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
REFRESH_INTERVAL=60
```

### 3. Elegir modo de operación

Railway arrancará automáticamente en modo `--watch` (monitoreo continuo).

**Para reportes diarios a las 9 AM**, cambia el comando de inicio:

1. En Railway → **Settings** → **Deploy**
2. **Custom Start Command**: `python3 src/scheduler.py`
3. Click **Deploy**

Esto enviará un reporte diario a Telegram a las 9 AM automáticamente.

## 📋 Modos disponibles

### Opción A: Solo reportes diarios (Recomendado)
```bash
# Start Command en Railway:
python3 src/scheduler.py
```
- ✅ Envía reporte diario a las 9 AM por Telegram
- ✅ Mínimo uso de recursos
- ✅ No alertas en tiempo real (solo resumen diario)

### Opción B: Monitoreo continuo con alertas
```bash
# Start Command en Railway:
python3 src/main.py --watch
```
- ✅ Monitoreo en tiempo real (refresca cada 60s)
- ✅ Alertas inmediatas cuando se supera umbral
- ⚠️ No envía reporte diario (solo alertas por umbral)

### Opción C: Ambos (2 servicios)

Crea dos servicios en Railway:

**Servicio 1 - Reportes diarios:**
- Start Command: `python3 src/scheduler.py`

**Servicio 2 - Monitor continuo:**
- Start Command: `python3 src/main.py --watch`

Ambos servicios usan las mismas variables de entorno.

## 💰 Costos

- **Plan gratuito Railway**: $5 de crédito mensual
- **Uso estimado**: ~$2-3/mes (modo scheduler) o ~$3-5/mes (modo watch)
- ✅ **Cabe en el plan gratuito**

## 📊 Verificar que funciona

1. **Ver logs en Railway**: Dashboard → tu servicio → **Deployments** → **View Logs**
2. **Probar manualmente** (desde Railway CLI o logs):
   ```bash
   python3 src/main.py --report
   ```
   Deberías recibir el mensaje en Telegram inmediatamente.

3. **Verificar el scheduler**:
   - En los logs deberías ver: `🤖 OpenRouter Monitor Scheduler started`
   - Cada hora: `💓 [HH:MM] Scheduler alive, next report: tomorrow 9 AM`
   - A las 9 AM: `📊 Sending daily report...` → `✅ Report sent successfully`

## 🔄 Actualizaciones automáticas

Cada vez que hagas `git push` a `main`, Railway redeploya automáticamente.

```bash
git add -A
git commit -m "Update config"
git push
```

## 🐛 Troubleshooting

### El servicio se reinicia constantemente
- Revisa **Logs** en Railway
- Verifica que las 3 variables de entorno estén configuradas
- Ambos modos (`scheduler` y `--watch`) deben correr indefinidamente

### No llegan reportes a Telegram
1. Verifica `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en Railway Variables
2. Prueba el bot localmente: `python3 src/main.py --report`
3. Revisa los logs del scheduler a las 9 AM

### Errores de API (Connection reset)
- El retry logic se encarga automáticamente
- Si persiste, aumenta `REFRESH_INTERVAL` a 120 segundos

### Cambiar hora del reporte diario
Edita `src/scheduler.py`, línea donde dice `if now.hour == 9`:
```python
if now.hour == 15:  # Para 3 PM
```
Commit y push.

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Cómo obtener tu CHAT_ID de Telegram](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)
- [OpenRouter Management Keys](https://openrouter.ai/settings/keys)
