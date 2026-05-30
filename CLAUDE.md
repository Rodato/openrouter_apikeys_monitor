# openrouterMonitor — Notas del proyecto

## Estado actual
- Proyecto funcionando localmente con `--watch`, `--once` y `--report`
- Management Key de OpenRouter configurada en `.env`
- Telegram bot configurado y funcionando
- Modo `--report` envía resumen diario por Telegram
- Scripts de deploy listos en `deploy/`
- GitHub: https://github.com/Rodato/openrouter_apikeys_monitor

## Deploy

### Railway (Recomendado)
- Dockerfile listo
- `railway.json` configurado
- `src/scheduler.py` para reportes diarios automáticos a las 9 AM
- Ver `deploy/RAILWAY.md` para instrucciones

### VPS (Alternativa)
- Scripts listos en `deploy/`
- `setup_cron.sh` para reportes diarios
- `openrouter-monitor.service` para systemd
- Ver `deploy/README.md`

## Decisiones tomadas
- No hay web dashboard — las alertas de Telegram son suficientes para el equipo
- No se usan `.env.example` ni `config.yaml.example` en el repo
- Stack: rich, httpx, python-dotenv, PyYAML, requests
