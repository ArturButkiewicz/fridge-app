from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app import crud, schemas, models

# Create database tables (for now, without Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fridge App Backend")

# --- Users CRUD ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    return crud.create_user(db, user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    """Get all users."""
    return crud.get_users(db)

# --- Ingredients CRUD ---
@app.post("/ingredients/", response_model=schemas.IngredientOut)
def create_ingredient_endpoint(
    ingredient: schemas.IngredientCreate,
    db: Session = Depends(get_db)):
    """Create a new ingredient."""
    return crud.create_ingredient(db, ingredient)

@app.get("/ingredients/", response_model=list[schemas.IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    """Get all ingredients."""
    return crud.get_ingredients(db)

@app.get("/ingredients/{ingredient_id}", response_model=schemas.IngredientOut)
def get_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    item = crud.get_ingredient(db, ingredient_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return item

@app.put("/ingredients/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient_endpoint(
    ingredient_id: int,
    ingredient: schemas.IngredientUpdate,
    db: Session = Depends(get_db)
):
    item = crud.update_ingredient(db, ingredient_id, ingredient)
    if not item:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return item

@app.delete("/ingredients/{ingredient_id}", status_code=204)
def delete_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    ok = crud.delete_ingredient(db, ingredient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Ingredient not found")

# --- User Ingredients CRUD ---
@app.post("/users/{user_id}/ingredients/", response_model=schemas.UserIngredientOut)
def add_user_ingredient_endpoint(user_id: int, ui: schemas.UserIngredientCreate, db: Session = Depends(get_db)):
    """Add a new ingredient to a user's fridge."""
    return crud.add_user_ingredient(db, user_id, ui)

@app.get("/users/{user_id}/ingredients/", response_model=list[schemas.UserIngredientOut])
def get_user_ingredients_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get all ingredients for a user."""
    return crud.get_user_ingredients(db, user_id)

@app.put("/users/{user_id}/ingredients/{ingredient_id}/", response_model=schemas.UserIngredientOut)
def update_user_ingredient_endpoint(
    user_id: int,
    ingredient_id: int,
    data: schemas.UserIngredientUpdate,
    db: Session = Depends(get_db)
):
    """Update quantity or expiry date of a user's ingredient."""
    return crud.update_user_ingredient(db, user_id, ingredient_id, data)

@app.delete(
    "/users/{user_id}/ingredients/{ingredient_id}/",
    status_code=204
)
def delete_user_ingredient_endpoint(
    user_id: int,
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    crud.delete_user_ingredient(db, user_id, ingredient_id)

# --- Root endpoint ---
@app.get("/")
def root():
    """Root endpoint to check API status."""
    return {"message": "Fridge App Backend working!"}

# --- Recipe suggestion endpoint ---
@app.get("/recipes/suggest")
def suggest_recipes(user_id: int, db: Session = Depends(get_db)):
    """
    Suggest recipes for a user based on their available ingredients.

    Returns:
        - id: Recipe ID
        - name: Recipe name
        - can_make: True if all ingredients are available
        - missing_ingredients: List of missing ingredient names
        - used_ingredients: List of all ingredients in the recipe
    """
    # Fetch user from DB
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch all recipes
    recipes = db.query(models.Recipe).all()
    result = []

    for recipe in recipes:
        # Recipe ingredients
        recipe_ings = [ing.name for ing in recipe.ingredients]
        # Ingredients the user has
        user_ings = [ui.ingredient.name for ui in user.ingredients]

        # Missing ingredients
        missing = [ing for ing in recipe_ings if ing not in user_ings]
        can_make = len(missing) == 0

        result.append({
            "id": recipe.id,
            "name": recipe.name,
            "can_make": can_make,
            "missing_ingredients": missing,
            "used_ingredients": recipe_ings
        })

    return result
