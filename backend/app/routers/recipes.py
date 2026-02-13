from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.recipe_service import suggest_recipes_for_user
from app import crud, schemas, models

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

@router.get("/suggest")
def suggest_recipes(user_id: int, db: Session = Depends(get_db)):
    return suggest_recipes_for_user(db, user_id)

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

@router.post("/{recipe_id}/ingredients", response_model=schemas.RecipeIngredientOut)
def add_ingredient_to_recipe(
    recipe_id: UUID,
    data: schemas.RecipeIngredientCreate,
    db: Session = Depends(get_db),
):
    recipe_ingredient = crud.add_ingredient_to_recipe(
        db,
        recipe_id=recipe_id,
        ingredient_id=data.ingredient_id,
        amount=data.amount,
    )

    return schemas.RecipeIngredientOut(
        ingredient_id=recipe_ingredient.ingredient_id,
        ingredient_name=recipe_ingredient.ingredient.name,
        amount=recipe_ingredient.amount,
    )

@router.delete(
    "/{recipe_id}/ingredients/{ingredient_id}",
    status_code=204
)
def remove_ingredient_from_recipe(
    recipe_id: UUID,
    ingredient_id: int,
    db: Session = Depends(get_db),
):
    crud.remove_ingredient_from_recipe(
        db,
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
    )
