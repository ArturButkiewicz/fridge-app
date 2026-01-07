from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

# ---- Ingredients ----
def create_ingredient(db: Session, ingredient: schemas.IngredientCreate):
    db_item = models.Ingredient(**ingredient.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_ingredients(db: Session):
    return db.query(models.Ingredient).all()

# ---- Users ----
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session):
    return db.query(models.User).all()

# ---- User Ingredients ----
def add_user_ingredient(db: Session, user_id: int, ui: schemas.UserIngredientCreate):
    if ui.expiry_date is None:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ui.ingredient_id).first()
        ui.expiry_date = datetime.today() + timedelta(days=ingredient.default_shelf_life_days)
    db_ui = models.UserIngredient(user_id=user_id, **ui.dict())
    db.add(db_ui)
    db.commit()
    db.refresh(db_ui)
    return db_ui

def get_user_ingredients(db: Session, user_id: int):
    return db.query(models.UserIngredient).filter(models.UserIngredient.user_id == user_id).all()
