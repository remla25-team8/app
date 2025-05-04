FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Here we're doing multistage building
FROM python:3.9-slim 

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app /app

# env variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    MODEL_SERVICE_URL=http://model-service:5000
# MODEL_SERVICE_URL TO DEFINE!!!!

EXPOSE 8080

CMD ["python", "app.py"]