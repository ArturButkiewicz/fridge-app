from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app import crud, schemas, models

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

@router.get("/suggest")
def suggest_recipes(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recipes = db.query(models.Recipe).all()
    result = []

    user_ings = {ui.ingredient.name for ui in user.ingredients}

    for recipe in recipes:
        recipe_ings = [ri.ingredient.name for ri in recipe.ingredients]
        missing = [ing for ing in recipe_ings if ing not in user_ings]

        result.append({
            "id": recipe.id,
            "name": recipe.name,
            "can_make": len(missing) == 0,
            "missing_ingredients": missing,
            "used_ingredients": recipe_ings,
        })

    return result

@router.post("/", response_model=schemas.RecipeOut)
def create_recipe(
    data: schemas.RecipeCreate,
    db: Session = Depends(get_db),
):
    return crud.create_recipe(db, data)


@router.get("/", response_model=list[schemas.RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return crud.get_recipes(db)


@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def get_recipe(recipe_id: UUID, db: Session = Depends(get_db)):
    return crud.get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(
    recipe_id: UUID,
    data: schemas.RecipeUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_recipe(db, recipe_id, data)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: UUID, db: Session = Depends(get_db)):
    crud.delete_recipe(db, recipe_id)
