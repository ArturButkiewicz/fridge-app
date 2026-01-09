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
@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    """Create a new ingredient."""
    return crud.create_ingredient(db, ingredient)

@app.get("/ingredients/", response_model=list[schemas.Ingredient])
def read_ingredients(db: Session = Depends(get_db)):
    """Get all ingredients."""
    return crud.get_ingredients(db)

# --- User Ingredients CRUD ---
@app.post("/users/{user_id}/ingredients/", response_model=schemas.UserIngredient)
def add_user_ingredient(user_id: int, ui: schemas.UserIngredientCreate, db: Session = Depends(get_db)):
    """Add a new ingredient to a user."""
    return crud.add_user_ingredient(db, user_id, ui)

@app.get("/users/{user_id}/ingredients/", response_model=list[schemas.UserIngredient])
def get_user_ingredients(user_id: int, db: Session = Depends(get_db)):
    """Get all ingredients for a user."""
    return crud.get_user_ingredients(db, user_id)

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
