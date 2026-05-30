# openrouterMonitor — Notas del proyecto

## Estado actual
- Proyecto funcionando localmente con `--watch`, `--once` y `--report`
- Management Key de OpenRouter configurada en `.env`
- Telegram bot configurado y funcionando
- Modo `--report` envía resumen diario por Telegram
- Scripts de deploy listos en `deploy/`
- GitHub: https://github.com/Rodato/openrouter_apikeys_monitor

## Pendiente

### Deploy en VPS
- Subir el proyecto a la VPS
- Configurar cron para reportes diarios (script listo: `deploy/setup_cron.sh`)
- Opcional: correr `--watch` en background con systemd o tmux para alertas en tiempo real

## Decisiones tomadas
- No hay web dashboard — las alertas de Telegram son suficientes para el equipo
- No se usan `.env.example` ni `config.yaml.example` en el repo
- Stack: rich, httpx, python-dotenv, PyYAML, requests
