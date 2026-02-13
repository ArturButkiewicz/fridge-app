from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException
from uuid import UUID

from . import models, schemas
from .models import Recipe, Ingredient, RecipeIngredient


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
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

def update_ingredient(
    db: Session,
    ingredient_id: int,
    ingredient: schemas.IngredientUpdate
):
    db_item = get_ingredient(db, ingredient_id)

    for field, value in ingredient.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item

def delete_ingredient(db: Session, ingredient_id: int):
    ingredient = get_ingredient(db, ingredient_id) 
    db.delete(ingredient)
    db.commit()
    return True


# ---- Users ----
def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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
    user = get_user(db, user_id)

    existing_user = (
        db.query(models.User)
        .filter(models.User.email == data.email, models.User.id != user_id)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user.email = data.email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
    return True

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

# ---- Recipes ----
def add_ingredient_to_recipe(
    db: Session,
    recipe_id: UUID,
    ingredient_id: int,
    amount: str | None = None,
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    exists = (
        db.query(RecipeIngredient)
        .filter(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == ingredient_id,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=409, detail="Ingredient already in recipe")

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        amount=amount,
    )

    db.add(recipe_ingredient)
    db.commit()
    db.refresh(recipe_ingredient)

    return recipe_ingredient

def get_recipe(db: Session, recipe_id: UUID):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

def get_recipes(db: Session):
    return db.query(Recipe).all()

def create_recipe(db: Session, data: schemas.RecipeCreate):
    existing = db.query(Recipe).filter(Recipe.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Recipe already exists")

    recipe = Recipe(
        name=data.name,
        description=data.description,
        instructions=data.instructions,
        external_url=data.external_url,
        recipe_type=data.recipe_type,
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe

def update_recipe(db: Session, recipe_id: UUID, data: schemas.RecipeUpdate):
    recipe = get_recipe(db, recipe_id)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(recipe, field, value)

    db.commit()
    db.refresh(recipe)
    return recipe

def delete_recipe(db: Session, recipe_id: UUID):
    recipe = get_recipe(db, recipe_id)
    db.delete(recipe)
    db.commit()
    return True

def remove_ingredient_from_recipe(
    db: Session,
    recipe_id: UUID,
    ingredient_id: int,
):
    relation = (
        db.query(RecipeIngredient)
        .filter(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == ingredient_id,
        )
        .first()
    )

    if not relation:
        raise HTTPException(
            status_code=404,
            detail="Ingredient not found in recipe"
        )

    db.delete(relation)
    db.commit()
    return True
