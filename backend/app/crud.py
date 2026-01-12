from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from fastapi import HTTPException
from app import models

# ---- Ingredients ----
def create_ingredient(db: Session, ingredient: schemas.IngredientCreate):
    shelf_life = ingredient.default_shelf_life_days or 7
    db_item = models.Ingredient(
        name=ingredient.name,
        default_shelf_life_days=shelf_life
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_ingredients(db: Session):
    return db.query(models.Ingredient).all()

def get_ingredient(db: Session, ingredient_id: int):
    return db.query(models.Ingredient)\
             .filter(models.Ingredient.id == ingredient_id)\
             .first()

def update_ingredient(
    db: Session,
    ingredient_id: int,
    ingredient: schemas.IngredientUpdate
):
    db_item = get_ingredient(db, ingredient_id)
    if not db_item:
        return None

    for field, value in ingredient.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item

def delete_ingredient(db: Session, ingredient_id: int):
    db_item = get_ingredient(db, ingredient_id)
    if not db_item:
        return None

    db.delete(db_item)
    db.commit()
    return True

# ---- Users ----
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(db: Session, user_id: int, data: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = data.email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return user

def get_users(db: Session):
    return db.query(models.User).all()

# ---- User Ingredients ----
def add_user_ingredient(db: Session, user_id: int, ui: schemas.UserIngredientCreate):
    ingredient = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.id == ui.ingredient_id)
        .first()
    )
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    existing = (
        db.query(models.UserIngredient)
        .filter(
            models.UserIngredient.user_id == user_id,
            models.UserIngredient.ingredient_id == ui.ingredient_id
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ingredient already exists in user's fridge"
        )
    
    quantity = ui.quantity if ui.quantity is not None else 1

    if ui.expiry_date:
        expiry_date = ui.expiry_date
    else:
        expiry_date = datetime.today().date() + timedelta(
            days=ingredient.default_shelf_life_days
        )
    db_ui = models.UserIngredient(
        user_id=user_id,
        ingredient_id=ui.ingredient_id,
        quantity=quantity,
        expiry_date=expiry_date
    )
    db.add(db_ui)
    db.commit()
    db.refresh(db_ui)

    return schemas.UserIngredientOut(
        id=db_ui.id,
        ingredient_id=db_ui.ingredient_id,
        quantity=db_ui.quantity,
        expiry_date=db_ui.expiry_date,
        ingredient_name=db_ui.ingredient.name
    )

def get_user_ingredients(db: Session, user_id: int):
    user_ingredients = db.query(models.UserIngredient).filter(
        models.UserIngredient.user_id == user_id
    ).all()

    result = []
    for ui in user_ingredients:
        result.append({
            "id": ui.id,
            "ingredient_id": ui.ingredient_id,
            "quantity": ui.quantity,
            "expiry_date": ui.expiry_date,
            "ingredient_name": ui.ingredient.name
        })
    return result

def get_ingredient(db: Session, ingredient_id: int):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

def update_ingredient(db: Session, ingredient_id: int, data: schemas.IngredientUpdate):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    ingredient.name = data.name
    ingredient.default_shelf_life_days = data.default_shelf_life_days
    db.commit()
    db.refresh(ingredient)
    return ingredient

def delete_ingredient(db: Session, ingredient_id: int):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    db.delete(ingredient)
    db.commit()
    return ingredient

def update_user_ingredient(
    db: Session,
    user_id: int,
    ingredient_id: int,
    data: schemas.UserIngredientUpdate
):
    ui = (
        db.query(models.UserIngredient)
        .filter(
            models.UserIngredient.user_id == user_id,
            models.UserIngredient.ingredient_id == ingredient_id
        )
        .first()
    )

    if not ui:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found in user's fridge"
        )
    if data.quantity is not None:
        ui.quantity = data.quantity
    if data.expiry_date is not None:
        ui.expiry_date = data.expiry_date

    db.commit()
    db.refresh(ui)

    from .schemas import UserIngredientOut
    ui_out = UserIngredientOut(
        id=ui.id,
        ingredient_id=ui.ingredient_id,
        quantity=ui.quantity,
        expiry_date=ui.expiry_date,
        ingredient_name=ui.ingredient.name
    )
    return ui_out

def delete_user_ingredient(db: Session, user_id: int, ingredient_id: int):
    ui = (
        db.query(models.UserIngredient)
        .filter(
            models.UserIngredient.user_id == user_id,
            models.UserIngredient.ingredient_id == ingredient_id
        )
        .first()
    )

    if not ui:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found in user's fridge"
        )

    db.delete(ui)
    db.commit()
    return {"message": "Ingredient removed from fridge"}
