# Tweet Sentiment Analysis System

A full-stack application to analyze tweet sentiment using **FastAPI**, **Streamlit**, **Docker**, and **CI/CD** automation.

---

## Features

- Real-time sentiment analysis powered by **VADER**.
- Interactive web interface built with **Streamlit**.
- Robust REST API designed with **FastAPI**.
- Containerized services managed via **Docker Compose**.
- Automated CI/CD pipeline using **GitHub Actions**.
- Comprehensive visualizations of sentiment data.
- Full test coverage for quality assurance.

---

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
git clone https://github.com/sam20704/tweet-sentiment-analyzer.git
cd tweet-sentiment-analyzer

2. Build and start the containers:
docker-compose up --build

3. Access the application in your browser:
- Frontend UI: [http://localhost:8501](http://localhost:8501)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Local Development

1. Set up the Python environment and install dependencies:
make install

2. Run the backend server:
make run-backend

3. In a new terminal, run the frontend app:
make run-frontend

---

## API Endpoints

| Method | Endpoint   | Description                      |
|--------|------------|--------------------------------|
| GET    | `/`        | Basic health check              |
| GET    | `/health`  | Detailed health status          |
| POST   | `/analyze` | Analyze tweet sentiment         |

---

## Testing

Run all tests with the following command:

make test

---

## Architecture Overview

┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Frontend │ ──▶ │ Backend │ ──▶ │ VADER │
│ (Streamlit) │ │ (FastAPI) │ │ Sentiment │
│ Port: 8501 │ │ Port: 8000 │ │ Analyzer │
└───────────────┘ └───────────────┘ └───────────────┘

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Implement changes and add tests.
4. Run tests with `make test`.
5. Submit a pull request for review.

---

## License

This project is licensed under the **MIT License**.
*Built with FastAPI, Streamlit & Docker | Powered by VADER Sentiment Analysis*
