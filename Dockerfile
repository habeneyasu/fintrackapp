# Use official Python image
FROM python:3.12-slim

# Set workdir
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd gcc

# Install Python dependencies
COPY requirements/prod.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the whole app
COPY . /code

# Expose port
EXPOSE 8000

# Start FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
