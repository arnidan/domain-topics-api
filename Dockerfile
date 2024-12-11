FROM python:3.8-slim as downloader

RUN apt-get update && apt-get install -y curl

WORKDIR /model

COPY download_model.sh .
RUN chmod +x download_model.sh && ./download_model.sh

FROM python:3.8-slim as builder

WORKDIR /install

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev 
    
COPY requirements.txt .
RUN pip3 install --prefix=/install -r requirements.txt && \
    pip3 install --prefix=/install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime

FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=downloader /model/chrome5 ./chrome5
COPY --from=builder /install /usr/local

COPY src/ ./src/

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"] 