# UFC Nerd

This project provides a simple full-stack application that displays former UFC champions' records after they lost their belt. It consists of a Flask backend, a React frontend, and Docker-based deployment.

## Requirements
- Docker and Docker Compose
- Python 3.11
- Node 18

## Running locally

1. Copy `.env.example` to `.env` and edit if needed.
2. Run `docker-compose up --build`.
3. Access the frontend at `http://localhost:3000` and the API at `http://localhost:5000/api/champions/records`.

## Testing

Run backend tests with:
```
pip install -r backend/requirements.txt
pytest backend/tests
```

## CI/CD

GitHub Actions workflows are included:
- `ci-prod.yml` runs on pushes to `main` and builds Docker images.
- `ci-dev.yml` runs on pushes to `dev`.

## Structure
- `backend/` – Flask API
- `frontend/` – React app
- `data/` – sample data
- `.github/workflows/` – CI configurations
