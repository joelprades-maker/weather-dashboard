# Weather Dashboard — Portfolio Project

## Objetivo
Pipeline de datos automatizado que extrae datos meteorológicos diarios de 6 ciudades españolas,
los acumula en un JSON y los visualiza en un dashboard HTML público desplegado en Vercel.

## Stack
- **Extracción**: Python + API Open-Meteo (sin API key, gratuita)
- **Automatización**: GitHub Actions (cron diario a las 8:00 UTC)
- **Almacenamiento**: `data/weather.json` (histórico acumulado en el propio repo)
- **Frontend**: HTML + Chart.js (dashboard interactivo)
- **Despliegue**: Vercel (auto-deploy en cada commit)

## Ciudades
Madrid, Barcelona, Valencia, Sevilla, Bilbao, Zaragoza

## Variables a capturar por ciudad (diarias)
- Temperatura máxima y mínima (°C)
- Precipitación (mm)
- Viento máximo (km/h)
- Horas de sol
- Código meteorológico (WMO)

## Estructura de archivos
```
weather-dashboard/
├── CLAUDE.md
├── fetch_weather.py        # Script de extracción
├── data/
│   └── weather.json        # Histórico acumulado
├── index.html              # Dashboard público
└── .github/
    └── workflows/
        └── daily_fetch.yml # GitHub Actions
```

## Contexto de portfolio
Este proyecto es para el CV de un data analyst. Debe demostrar:
1. Capacidad de automatizar pipelines de datos
2. Uso de APIs reales
3. Visualización de datos con métricas de negocio
4. Despliegue en producción

## Notas importantes
- El JSON nunca se sobreescribe, solo se añaden entradas nuevas cada día
- GitHub Actions hace commit y push automático tras cada extracción
- El dashboard lee el JSON directamente, sin backend
