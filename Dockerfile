# Builder stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY requirements/prod.txt .
RUN pip install --user -r prod.txt

# Final stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .