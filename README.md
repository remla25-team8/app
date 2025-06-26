# Restaurant Sentiment Analysis Application - Team 8

## Description

This repository contains a web application for analyzing restaurant reviews to determine their sentiment (positive or negative). The application is built with `Flask` and is containerized using `Docker` to ensure consistency and ease of deployment across different environments (multi-stage was employed to reduce image suze and apt cache in image, as required). The application automatically analyzes review text and provides immediate feedback on sentiment, with options for users to correct predictions.

## Key Features

- **Flask Web Application:** A combined frontend and backend solution that offers:

  - User-friendly interface for submitting restaurant reviews
  - Real-time sentiment analysis using a dedicated model service
  - Feedback mechanism for correcting incorrect predictions
  - Version information display for both app and model service

- **Integration with Dependencies:**

  - **lib-version:** Integrated for version tracking and display
  - **Model Service:** Connected via REST API for sentiment analysis of reviews

- **Dockerized Environment:** The application is containerized using Docker with multi-stage builds and released as a package in GitHub Container Registry (ghcr.io).

- **Automated Release Process:** GitHub Actions workflows handle:

  - Building and publishing Docker images with proper versioning
  - Creating GitHub releases and pre-releases automatically
  - Supporting multiple architectures (amd64, arm64)

- **OpenAPI Documentation:** All API endpoints are documented using Flasgger/Swagger:
  - Interactive API documentation available at `/api/docs`
  - Fully compliant with [Open API Specification](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/2.0.md#operation-object)
  - Test API endpoints directly from the documentation interface

## API Endpoints (app-service)

| Endpoint    | Method | Description                                       |
| ----------- | ------ | ------------------------------------------------- |
| `/`         | GET    | Main application interface                        |
| `/info`     | GET    | Get version information for app and model service |
| `/analyze`  | POST   | Submit a review for sentiment analysis            |
| `/feedback` | POST   | Submit feedback for incorrect predictions         |
| `/api/docs` | GET    | Interactive API documentation (Swagger UI)        |

### Analyze Endpoint

**Request:**

```json
{
  "review": "The restaurant was fantastic!"
}
```

**Response:**

```json
{
  "review": "The restaurant was fantastic!",
  "prediction": 1,
  "sentiment": "positive"
}
```

### Feedback Endpoint

**Request:**

```json
{
  "review": "The restaurant was fantastic!",
  "prediction": 1,
  "actual_sentiment": 0
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Feedback received"
}
```

## Installation & Usage

### Using Docker (Recommended)

```bash
# Pull the latest stable release
docker pull ghcr.io/remla25-team8/app:latest

# Pull the latest pre-release
docker pull ghcr.io/remla25-team8/app:latest-pre

# Pull a specific pre-release version
docker pull ghcr.io/remla25-team8/app:v1.0.1-pre-2

# Run the container (using stable release)
docker run -p 8080:8080 -e MODEL_SERVICE_URL=http://model-service:5000 ghcr.io/remla25-team8/app:latest

# Run the container (using latest pre-release)
docker run -p 8080:8080 -e MODEL_SERVICE_URL=http://model-service:5000 ghcr.io/remla25-team8/app:latest-pre
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/remla25-team8/app.git
cd app

# Install dependencies (tested on python 3.9)
pip install -r requirements.txt

# Run the application
python app.py
```

## Configuration

The application can be configured using environment variables:

| Variable          | Description                                 | Default                                |
| ----------------- | ------------------------------------------- | -------------------------------------- |
| PORT              | Port on which the app will listen           | 8080                                   |
| MODEL_SERVICE_URL | URL of the sentiment analysis model service | http://localhost:5000 (_TODO_: change) |

## Development

### Local Development

1. Clone the repository:

   ```bash
   git clone https://github.com/remla25-team8/app.git
   cd app
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

### Project Structure

```
app/
├── .github/workflows/    # CI/CD workflows
├── static/               # Static assets (CSS, JS)
├── templates/            # HTML templates
├── app.py                # Main application code
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

### Release Process

This repository uses GitHub Actions for automated versioning and image building:

1. **Stable Releases**: When a stable version tag is pushed (e.g., `v1.0.0`), the Docker image is automatically built and published with `latest` tag
2. **Automatic Pre-releases**: After a stable release, a pre-release tag for the next version is automatically created (e.g., `v1.0.1-pre-1`)
3. **Manual Pre-releases**: Additional pre-release iterations can be created manually via GitHub Actions workflow dispatch:
   - Navigate to Actions → "Manual Pre-release Creation" 
   - Specify base version (e.g., `1.0.1`) and optional description
   - System automatically creates incremental versions (`v1.0.1-pre-2`, `v1.0.1-pre-3`, etc.)
4. **Multi-architecture Support**: Images are built for multiple architectures (amd64 and arm64)
5. **Pre-release Tagging**: Pre-release images are tagged with both specific version and `latest-pre` for easy access

For detailed information about the pre-release workflow, see [PRERELEASE_WORKFLOW.md](./PRERELEASE_WORKFLOW.md).

## Use of Generative AI

Generative AI tools were utilized in the creation of this README.md document. Specifically, these tools were employed for grammar and spell checking, suggestions on the organization of the document sections and enhancements to various content portions.

The core information about the application architecture and functionality remains accurate and was verified by the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
