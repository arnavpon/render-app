from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.recipes.router import router as recipes_router
from app.recipes.service import get_all_cuisines, get_all_recipes, get_all_tags

app = FastAPI(title="Kitchen Companion")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(recipes_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the recipe list as the homepage."""
    recipes = get_all_recipes()
    cuisines = get_all_cuisines()
    tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="recipes/list.html",
        context={"recipes": recipes, "cuisines": cuisines, "tags": tags, "search_query": None},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)