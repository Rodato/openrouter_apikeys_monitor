# Deploy a VPS

Este proyecto ya está listo para enviar reportes diarios por Telegram.

## Requisitos en la VPS

- Python 3.9+ (`python3 --version`)
- Git instalado

## Opción 1: Reportes diarios (recomendado)

Cron enviará un reporte por Telegram todos los días a las 9 AM.

```bash
# Clonar el repo
git clone https://github.com/Rodato/openrouter_apikeys_monitor.git
cd openrouter_apikeys_monitor

# Instalar dependencias
pip3 install --user -r requirements.txt

# Configurar .env con tus credenciales
nano .env
# Agregar:
# OPENROUTER_MANAGEMENT_KEY=tu_key_aqui
# TELEGRAM_BOT_TOKEN=tu_bot_token
# TELEGRAM_CHAT_ID=tu_chat_id
# REFRESH_INTERVAL=60

# Setup cron (reporte diario a las 9 AM)
chmod +x deploy/setup_cron.sh
./deploy/setup_cron.sh
```

**Probar manualmente:**
```bash
python3 src/main.py --report
```

Si recibes el mensaje en Telegram, está funcionando.

## Opción 2: Monitor continuo (--watch en background)

Si también quieres monitorear en tiempo real con alertas por umbral:

### Con tmux (simple)

```bash
tmux new -s openrouter
python3 src/main.py --watch
# Ctrl+B, D para detach
```

Reconectar: `tmux attach -t openrouter`

### Con systemd (más robusto)

```bash
# Editar el archivo de servicio con tus rutas
nano deploy/openrouter-monitor.service

# Copiar a systemd
sudo cp deploy/openrouter-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openrouter-monitor
sudo systemctl start openrouter-monitor

# Ver logs
sudo journalctl -u openrouter-monitor -f
```

## Personalizar horario del reporte

Editar el cron:
```bash
crontab -e
```

Ejemplos de horarios:
- `0 9 * * *` — Diario a las 9 AM
- `0 9,18 * * *` — 9 AM y 6 PM
- `0 9 * * 1-5` — 9 AM solo días laborables

## Verificar que funciona

```bash
# Ver logs del cron
tail -f logs/cron.log

# Forzar envío manual
python3 src/main.py --report
```

## Actualizar código

```bash
git pull
sudo systemctl restart openrouter-monitor  # si usas systemd
```
