FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends\
    build-essential \
    gcc \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/local/share/ca-certificates/yandex && \
    curl -sS https://storage.yandexcloud.net/cloud-certs/CA.pem -o /usr/local/share/ca-certificates/yandex/YandexCA.pem && \
    update-ca-certificates \

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

EXPOSE 8000
