# Plataforma de Web Scraping y Analítica de Contenido

Aplicación web educativa para registrar proyectos de scraping, ejecutar extracciones, procesar contenido y visualizar resultados analíticos (sentimiento y tópicos).

## Stack
- FastAPI + Jinja2 (web app)
- SQLModel + SQLite (persistencia)
- BeautifulSoup + httpx (scraping)

## Módulos implementados
- Gestión de usuarios y roles básicos (admin/analista)
- Gestión de proyectos y fuentes
- Ejecución manual de scraping por fuente
- Almacenamiento raw y procesado
- Análisis de sentimiento básico (positivo/negativo/neutral)
- Dashboard con agregaciones y exportación CSV
- Registro de historial de ejecuciones y errores

## Ejecutar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Abrir: http://127.0.0.1:8000

## Notas de cumplimiento
- Diseñada para uso educativo y con fuentes públicas/autorizadas.
- Incluye política por proyecto para trazabilidad de uso.
- No implementa identificación individual; solo procesamiento agregado.
