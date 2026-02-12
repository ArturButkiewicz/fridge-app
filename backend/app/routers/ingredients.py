from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredients"],
)

@router.post("/", response_model=schemas.IngredientOut)
def create_ingredient_endpoint(
    ingredient: schemas.IngredientCreate,
    db: Session = Depends(get_db)
):
    return crud.create_ingredient(db, ingredient)

@router.get("/", response_model=list[schemas.IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    return crud.get_ingredients(db)

@router.get("/{ingredient_id}", response_model=schemas.IngredientOut)
def get_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_ingredient(db, ingredient_id)

@router.put("/{ingredient_id}", response_model=schemas.IngredientOut)
def update_ingredient_endpoint(
    ingredient_id: int,
    ingredient: schemas.IngredientUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_ingredient(db, ingredient_id, ingredient)

@router.delete("/{ingredient_id}", status_code=204)
def delete_ingredient_endpoint(
    ingredient_id: int,
    db: Session = Depends(get_db)
):
    crud.delete_ingredient(db, ingredient_id)
