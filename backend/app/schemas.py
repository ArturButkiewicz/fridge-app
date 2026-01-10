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
    email: str

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    email: str

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

class UserIngredientOut(UserIngredient):
    ingredient_name: str

class UserIngredientOut(BaseModel):
    id: int
    ingredient_id: int
    quantity: int
    expiry_date: Optional[date]
    ingredient_name: str

    class Config:
        orm_mode = True    
        
class UserIngredientUpdate(BaseModel):
    quantity: int | None = None
    expiry_date: date | None = None


class IngredientUpdate(BaseModel):
    name: str
    default_shelf_life_days: int

