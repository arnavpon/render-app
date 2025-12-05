# Render App

A web application built with FastAPI, HTMX, Bulma CSS, and DuckDB.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: HTMX for reactivity, Bulma CSS for styling
- **Database**: DuckDB (embedded analytical database)
- **Package Manager**: uv

## Project Structure

```
render-app/
├── main.py              # FastAPI application entry point
├── templates/           # Jinja2 HTML templates
│   └── index.html       # Main page template
├── static/              # Static assets (CSS, JS, images)
├── pyproject.toml       # Project dependencies and metadata
├── Dockerfile           # Container configuration
├── render.yaml          # Render deployment configuration
└── app.db               # DuckDB database file (created at runtime)
```

## Development

### Setup

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
uv run pytest
```

## Deployment

### Docker

```bash
# Build the image
docker build -t render-app .

# Run the container
docker run -p 8000:8000 render-app
```

### Render

The app is configured for deployment on Render via `render.yaml`. Push to your connected repository to trigger a deployment.

## API Endpoints

- `GET /` - Main page (returns HTML)
- `GET /health` - Health check endpoint (returns JSON)

## Database

DuckDB is used as an embedded database. The database file `app.db` is created automatically on startup. Add table creation logic in the `init_db()` function in `main.py`.
