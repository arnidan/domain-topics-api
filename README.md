# URL Topic Classifier API

A service that classifies domains into topics using Google Chrome's Topics API model.

## Overview

This service provides a REST API endpoint that accepts domains and returns their classified topics using the Chrome Topics API classifier model. It uses the same model and classification logic as Chrome's Topics API.

This project is based on the [Chrome Topics Classifier](https://github.com/yohhaan/topics_classifier) repository, which provides Python examples for using Chrome's Topics API model.

The Topics API is part of Chrome's Privacy Sandbox initiative, designed to help serve relevant ads without third-party cookies. You can learn more about it in the [Chrome Topics API documentation](https://developer.chrome.com/docs/privacy-sandbox/topics/).

## Quick Start with Docker

### Using Prebuilt Image

The easiest way to get started is to use the prebuilt Docker image which supports both ARM64 (Apple Silicon, AWS Graviton) and AMD64 architectures:

```bash
docker pull ghcr.io/arnidan/domain-topics-api:latest
docker run -p 8000:8000 ghcr.io/arnidan/domain-topics-api:latest
```

### Building from Source

Alternatively, you can build the image yourself:

```bash
docker build -t url-classifier .
docker run -p 8000:8000 url-classifier
```

The API will be available at `http://localhost:8000`

## Manual Setup

_Note: It seems to work only with Python 3.8._

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

3. Download the model files:
```bash
chmod +x scripts/download_model.sh
./scripts/download_model.sh
```

4. Run the application:
```bash
uvicorn src.app:app --reload
```

## API Usage

### Get All Topics

**Endpoint:** `GET /topics`

**Response:**
```json
{
    "topics": [
        {
            "id": 123,
            "name": "Topic Name"
        },
        ...
    ]
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/topics"
```

### Classify Domain

**Endpoint:** `POST /classify`

**Request:**
```json
{
    "domain": "example.com"
}
```

**Response:**
```json
{
    "domain": "example.com",
    "topics": [
        {
            "id": 123,
            "name": "Topic Name"
        }
    ]
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/classify" \
     -H "Content-Type: application/json" \
     -d '{"domain": "example.com"}'
```

### API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## License

MIT License

## Credits

This project uses the Topics API model from Google Chrome's Topics API implementation. The model and classification logic are based on the [Chrome Topics Classifier](https://github.com/yohhaan/topics_classifier) repository.