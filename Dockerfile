FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev

# Copy requirements first to leverage Docker cache
COPY requirements/prod.txt .
RUN pip install --upgrade pip && pip install -r prod.txt

# Copy application code
COPY . .

# For production, use Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]