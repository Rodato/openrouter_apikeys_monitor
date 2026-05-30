# Deploy en VPS — OpenRouter Monitor

## 1. Subir el proyecto

```bash
# Desde tu máquina local
scp -r /Users/daniel/Documents/Dev/openrouterMonitor usuario@tu-vps-ip:/home/usuario/openrouterMonitor
```

O clonar directamente desde GitHub en la VPS:
```bash
git clone https://github.com/Rodato/openrouter_apikeys_monitor openrouterMonitor
```

## 2. Configurar entorno en la VPS

```bash
cd openrouterMonitor
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 3. Configurar variables de entorno

Crear/editar el archivo `.env` en la VPS:

```bash
nano .env
```

Contenido:
```
OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Cómo obtener el TELEGRAM_CHAT_ID:
1. Habla con @BotFather en Telegram → crea un bot → copia el token
2. Envíale un mensaje a tu bot
3. Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Busca `"chat": {"id": XXXXXXXX}` — ese es tu chat ID

## 4. Probar manualmente

```bash
cd openrouterMonitor

# Ver snapshot en terminal
.venv/bin/python3 src/main.py --once

# Enviar reporte a Telegram ahora mismo
.venv/bin/python3 src/main.py --report
```

## 5. Configurar cron (reporte cada 2 horas)

```bash
crontab -e
```

Agregar esta línea (reporte cada 2 horas):
```
0 */2 * * * cd /home/usuario/openrouterMonitor && .venv/bin/python3 src/main.py --report >> /tmp/openrouter_monitor.log 2>&1
```

O cada hora:
```
0 * * * * cd /home/usuario/openrouterMonitor && .venv/bin/python3 src/main.py --report >> /tmp/openrouter_monitor.log 2>&1
```

> **Nota:** Ajusta la ruta `/home/usuario/openrouterMonitor` a donde lo tengas en tu VPS.

## 6. (Opcional) Monitor continuo en tmux

Si además quieres ver el TUI en vivo cuando te conectes a la VPS:

```bash
# Crear sesión tmux
tmux new-session -d -s monitor

# Correr el watch en background
tmux send-keys -t monitor 'cd openrouterMonitor && .venv/bin/python3 src/main.py --watch --interval 120' Enter

# Para reconectarte después
tmux attach -t monitor
```

## Resumen de comandos útiles

| Comando | Qué hace |
|---------|----------|
| `python3 src/main.py --once` | Snapshot en terminal, sale |
| `python3 src/main.py --report` | Envía reporte a Telegram, sale |
| `python3 src/main.py --watch` | TUI en vivo (para terminal interactivo) |
| `python3 src/main.py --watch --interval 120` | TUI, refresca cada 2 min |
