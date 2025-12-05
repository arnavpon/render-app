from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import duckdb

app = FastAPI(title="Render App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


def get_db_connection():
    """Get a DuckDB connection."""
    return duckdb.connect("app.db")


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    # Add your table creation here as needed
    conn.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"message": "Hello World - from Claude!"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)