from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.recipes.service import create_recipe, delete_recipe, get_all_recipes

router = APIRouter(prefix="/recipes", tags=["recipes"])
templates = Jinja2Templates(directory="templates")


@router.get("", response_class=HTMLResponse)
async def list_recipes(request: Request):
    """Render the recipes list page."""
    recipes = get_all_recipes()
    return templates.TemplateResponse(
        request=request,
        name="recipes/list.html",
        context={"recipes": recipes},
    )


@router.post("", response_class=HTMLResponse)
async def save_recipe(request: Request, recipe_url: str = Form(...)):
    """Save a new recipe URL."""
    create_recipe(url=recipe_url)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/save_success.html",
    )


@router.delete("/{recipe_id}", response_class=HTMLResponse)
async def remove_recipe(recipe_id: int):
    """Delete a recipe by ID. Returns empty response for HTMX to remove the row."""
    delete_recipe(recipe_id)
    return HTMLResponse(content="")


@router.get("/add", response_class=HTMLResponse)
async def add_recipe_page(request: Request):
    """Render the add recipe page."""
    return templates.TemplateResponse(
        request=request,
        name="recipes/add.html",
    )


@router.get("/add/form/text", response_class=HTMLResponse)
async def add_recipe_text_form(request: Request):
    """Return the text input form partial."""
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/form_text.html",
    )


@router.get("/add/form/url", response_class=HTMLResponse)
async def add_recipe_url_form(request: Request):
    """Return the URL input form partial."""
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/form_url.html",
    )
