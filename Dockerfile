FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD sh -c "
  echo 'Waiting for database...' &&
  while ! nc -z postgres 5432; do sleep 2; done &&
  echo 'Waiting for Redis...' &&
  while ! nc -z redis 6379; do sleep 2; done &&
  echo 'Running migrations...' &&
  alembic upgrade head &&
  echo 'Starting FastAPI...' &&
  uvicorn app:app --host 0.0.0.0 --port 8080
"