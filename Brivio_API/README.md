# Brivio API

A simple FastAPI service.

## Prerequisites

- Python 3.8+
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (optional but recommended)

## Getting Started

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd brivio-api
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your `API_KEY`.

5. **Run the application**:
   ```bash
   fastapi dev main.py
   ```

## Documentation

Once the application is running, you can access the interactive API documentation at:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
