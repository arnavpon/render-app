from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.recipes.service import (
    add_url_to_recipe,
    create_recipe,
    delete_recipe,
    delete_url,
    get_all_cuisines,
    get_all_recipes,
    get_all_tags,
    get_or_create_cuisine,
    get_recipe_by_id,
    update_recipe,
    update_recipe_name,
    update_recipe_tags,
    update_url,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])
templates = Jinja2Templates(directory="templates")


# Static routes MUST come before dynamic /{recipe_id} routes
@router.get("", response_class=HTMLResponse)
async def list_recipes(request: Request):
    """Render the recipes list page."""
    recipes = get_all_recipes()
    cuisines = get_all_cuisines()
    tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="recipes/list.html",
        context={"recipes": recipes, "cuisines": cuisines, "tags": tags, "search_query": None},
    )


@router.get("/add", response_class=HTMLResponse)
async def add_recipe_page(request: Request):
    """Render the add recipe page."""
    cuisines = get_all_cuisines()
    tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="recipes/add.html",
        context={"cuisines": cuisines, "tags": tags},
    )


@router.get("/search", response_class=HTMLResponse)
async def search_recipes(request: Request, q: str = ""):
    """Search recipes by name or tags. Returns partial HTML for HTMX."""
    search_query = q.strip() if q else None
    recipes = get_all_recipes(search_query=search_query)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/recipe_list.html",
        context={"recipes": recipes, "search_query": search_query},
    )


@router.get("/cuisines", response_class=JSONResponse)
async def get_cuisines():
    """Return all cuisines as JSON for autocomplete."""
    cuisines = get_all_cuisines()
    return [c["name"] for c in cuisines]


@router.get("/tags", response_class=JSONResponse)
async def get_tags():
    """Return all tags as JSON for autocomplete."""
    tags = get_all_tags()
    return [t["name"] for t in tags]


@router.post("", response_class=HTMLResponse)
async def save_recipe(
    request: Request,
    recipe_name: str = Form(...),
    cuisine: str = Form(...),
    recipe_url: str = Form(""),
    tags: str = Form(""),
    notes: str = Form(""),
):
    """Save a new recipe with name, cuisine, URL(s), optional tags, and notes."""
    cuisine_id = get_or_create_cuisine(cuisine)
    urls = [{"url": recipe_url}] if recipe_url.strip() else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    notes_value = notes.strip() if notes.strip() else None

    create_recipe(name=recipe_name, cuisine_id=cuisine_id, urls=urls, tags=tag_list, notes=notes_value)
    response = HTMLResponse(content="")
    response.headers["HX-Redirect"] = "/"
    return response


# URL management (static path before dynamic)
@router.patch("/urls/{url_id}", response_class=HTMLResponse)
async def edit_url(
    request: Request,
    url_id: int,
    url: str = Form(...),
    label: str = Form(""),
):
    """Update a URL."""
    update_url(url_id, url, label if label else None)
    return HTMLResponse(content="")


@router.delete("/urls/{url_id}", response_class=HTMLResponse)
async def remove_url(url_id: int):
    """Delete a URL."""
    delete_url(url_id)
    return HTMLResponse(content="")


# Dynamic routes with {recipe_id} come AFTER static routes
@router.get("/{recipe_id}", response_class=HTMLResponse)
async def view_recipe(request: Request, recipe_id: int):
    """View a single recipe with edit capabilities."""
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return HTMLResponse(content="Recipe not found", status_code=404)
    cuisines = get_all_cuisines()
    tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="recipes/view.html",
        context={"recipe": recipe, "cuisines": cuisines, "all_tags": tags},
    )


@router.delete("/{recipe_id}", response_class=HTMLResponse)
async def remove_recipe(recipe_id: int, request: Request):
    """Delete a recipe by ID. Returns empty response or redirect header for HTMX."""
    delete_recipe(recipe_id)
    # Check if request came from view page (has HX-Current-URL header with recipe ID)
    # Use HX-Redirect header to tell HTMX to redirect to home
    response = HTMLResponse(content="")
    response.headers["HX-Redirect"] = "/"
    return response


@router.patch("/{recipe_id}", response_class=HTMLResponse)
async def edit_recipe(
    request: Request,
    recipe_id: int,
    name: str = Form(None),
    cuisine: str = Form(None),
    tags: str = Form(None),
):
    """Update a recipe's fields. Returns the updated recipe card."""
    if name:
        update_recipe_name(recipe_id, name)
    if cuisine:
        cuisine_id = get_or_create_cuisine(cuisine)
        update_recipe(recipe_id, cuisine_id=cuisine_id)
    if tags is not None:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        update_recipe_tags(recipe_id, tag_list)

    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/recipe_card.html",
        context={"recipe": recipe},
    )


# Edit form endpoints (GET to show edit form)
@router.get("/{recipe_id}/edit/name", response_class=HTMLResponse)
async def show_name_edit(request: Request, recipe_id: int):
    """Show the name edit form."""
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/edit_name.html",
        context={"recipe": recipe},
    )


@router.get("/{recipe_id}/edit/cuisine", response_class=HTMLResponse)
async def show_cuisine_edit(request: Request, recipe_id: int):
    """Show the cuisine edit form."""
    recipe = get_recipe_by_id(recipe_id)
    cuisines = get_all_cuisines()
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/edit_cuisine.html",
        context={"recipe": recipe, "cuisines": cuisines},
    )


@router.get("/{recipe_id}/edit/tags", response_class=HTMLResponse)
async def show_tags_edit(request: Request, recipe_id: int):
    """Show the tags edit form."""
    recipe = get_recipe_by_id(recipe_id)
    all_tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/edit_tags.html",
        context={"recipe": recipe, "all_tags": all_tags},
    )


@router.get("/{recipe_id}/edit/notes", response_class=HTMLResponse)
async def show_notes_edit(request: Request, recipe_id: int):
    """Show the notes edit form."""
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/edit_notes.html",
        context={"recipe": recipe},
    )


# Save edit endpoints (PATCH to save and return display partial)
@router.patch("/{recipe_id}/name", response_class=HTMLResponse)
async def edit_recipe_name(request: Request, recipe_id: int, name: str = Form(...)):
    """Update a recipe's name. Returns the display partial."""
    update_recipe_name(recipe_id, name)
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/display_name.html",
        context={"recipe": recipe},
    )


@router.patch("/{recipe_id}/cuisine", response_class=HTMLResponse)
async def edit_recipe_cuisine(request: Request, recipe_id: int, cuisine: str = Form(...)):
    """Update a recipe's cuisine. Returns the display partial."""
    cuisine_id = get_or_create_cuisine(cuisine)
    update_recipe(recipe_id, cuisine_id=cuisine_id)
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/display_cuisine.html",
        context={"recipe": recipe},
    )


@router.patch("/{recipe_id}/tags", response_class=HTMLResponse)
async def edit_recipe_tags_endpoint(request: Request, recipe_id: int, tags: str = Form("")):
    """Update a recipe's tags. Returns the display partial."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    update_recipe_tags(recipe_id, tag_list)
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/display_tags.html",
        context={"recipe": recipe},
    )


@router.patch("/{recipe_id}/notes", response_class=HTMLResponse)
async def edit_recipe_notes(request: Request, recipe_id: int, notes: str = Form("")):
    """Update a recipe's notes. Returns the display partial."""
    update_recipe(recipe_id, notes=notes if notes.strip() else None)
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/display_notes.html",
        context={"recipe": recipe},
    )


# URL management for specific recipe
@router.post("/{recipe_id}/urls", response_class=HTMLResponse)
async def add_recipe_url(
    request: Request,
    recipe_id: int,
    url: str = Form(...),
    label: str = Form(""),
):
    """Add a URL to a recipe."""
    add_url_to_recipe(recipe_id, url, label if label else None)
    recipe = get_recipe_by_id(recipe_id)
    return templates.TemplateResponse(
        request=request,
        name="recipes/partials/url_list.html",
        context={"recipe": recipe},
    )
