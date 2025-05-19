# Visualization Project

A FastAPI-based visualization project with MySQL and QuadrantDB integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration (see `.env.example`)

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

- `app/`: Main application code
  - `api/`: FastAPI endpoints
  - `db/`: Database connections and models
  - `services/`: Business logic and external service integrations
  - `utils/`: Utility functions and helpers