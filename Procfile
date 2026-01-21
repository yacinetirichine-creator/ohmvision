web: cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: cd backend && celery -A core.celery worker --loglevel=info
