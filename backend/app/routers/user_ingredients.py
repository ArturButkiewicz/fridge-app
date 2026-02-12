from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/users/{user_id}/ingredients",
    tags=["User Ingredients"],
)

@router.post("/", response_model=schemas.UserIngredientOut)
def add_user_ingredient(
    user_id: int,
    ui: schemas.UserIngredientCreate,
    db: Session = Depends(get_db),
):
    return crud.add_user_ingredient(db, user_id, ui)

@router.get("/", response_model=list[schemas.UserIngredientOut])
def get_user_ingredients(
    user_id: int,
    db: Session = Depends(get_db),
):
    return crud.get_user_ingredients(db, user_id)

@router.put("/{ingredient_id}", response_model=schemas.UserIngredientOut)
def update_user_ingredient(
    user_id: int,
    ingredient_id: int,
    data: schemas.UserIngredientUpdate,
    db: Session = Depends(get_db),
):
    return crud.update_user_ingredient(db, user_id, ingredient_id, data)

@router.delete("/{ingredient_id}", status_code=204)
def delete_user_ingredient(
    user_id: int,
    ingredient_id: int,
    db: Session = Depends(get_db),
):
    crud.delete_user_ingredient(db, user_id, ingredient_id)
