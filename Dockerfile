ARG APP_VERSION=0.0.0
ARG MODEL_SERVICE_VERSION=0.0.0

FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Add build arg for requirements hash to invalidate cache when requirements change
ARG REQ_HASH
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Here we're doing multistage building
FROM python:3.10-slim 

ARG APP_VERSION
ARG MODEL_SERVICE_VERSION

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    APP_VERSION=${APP_VERSION} \
    MODEL_SERVICE_VERSION=${MODEL_SERVICE_VERSION} \
    MODEL_SERVICE_URL=http://192.168.0.103:5000

EXPOSE $PORT
CMD ["python", "app.py"]