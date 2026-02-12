from pydantic import BaseModel, model_validator
from datetime import date
from typing import List, Optional, Literal
from uuid import UUID


# INGREDIENTS

class IngredientBase(BaseModel):
    name: str
    default_shelf_life_days: int


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    default_shelf_life_days: Optional[int] = None


class IngredientOut(IngredientBase):
    id: int

    model_config = {"from_attributes": True}


# USERS

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: str


class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}


# USER INGREDIENTS

class UserIngredientBase(BaseModel):
    ingredient_id: int
    quantity: int
    expiry_date: Optional[date] = None


class UserIngredientCreate(UserIngredientBase):
    pass


class UserIngredientUpdate(BaseModel):
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None


class UserIngredientOut(BaseModel):
    id: int
    ingredient_id: int
    quantity: int
    expiry_date: Optional[date]
    ingredient_name: str

    model_config = {"from_attributes": True}


# RECIPES

class RecipeCreate(BaseModel):
    name: str
    recipe_type: Literal["internal", "external"]
    description: Optional[str] = None
    instructions: Optional[str] = None
    external_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_by_type(self):
        if self.recipe_type == "internal":
            if not self.instructions:
                raise ValueError("Internal recipe must have instructions")
            if self.external_url:
                raise ValueError("Internal recipe cannot have external_url")

        elif self.recipe_type == "external":
            if not self.external_url:
                raise ValueError("External recipe must have external_url")
            if self.instructions:
                raise ValueError("External recipe cannot have instructions")

        return self



class RecipeUpdate(RecipeCreate):
    pass


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    amount: Optional[str] = None


class RecipeIngredientOut(BaseModel):
    ingredient_id: int
    ingredient_name: str
    amount: Optional[str] = None


class RecipeOut(BaseModel):
    id: UUID
    name: str
    recipe_type: Literal["internal", "external"]
    description: Optional[str]
    instructions: Optional[str]
    external_url: Optional[str]
    recipe_ingredients: List[RecipeIngredientOut]

    model_config = {"from_attributes": True}

