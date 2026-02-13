from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User, Recipe


def suggest_recipes_for_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    recipes = db.query(Recipe).all()
    result = []

    user_ingredients = {
        ui.ingredient.name for ui in user.user_ingredients
    }

    for recipe in recipes:
        recipe_ingredients = {
            ri.ingredient.name for ri in recipe.recipe_ingredients
        }

        missing = list(recipe_ingredients - user_ingredients)
        can_make = len(missing) == 0

        result.append({
            "id": recipe.id,
            "name": recipe.name,
            "can_make": can_make,
            "missing_ingredients": missing,
            "used_ingredients": list(recipe_ingredients),
        })

    return result
