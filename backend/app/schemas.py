from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class IngredientBase(BaseModel):
    name: str
    default_shelf_life_days: int = 7

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    pass

class User(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class UserIngredientBase(BaseModel):
    ingredient_id: int
    quantity: int = 1
    expiry_date: Optional[date]

class UserIngredientCreate(UserIngredientBase):
    pass

class UserIngredient(UserIngredientBase):
    id: int
    class Config:
        orm_mode = True
