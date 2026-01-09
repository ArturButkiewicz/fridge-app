from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

recipe_ingredient_table = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredients.id"), primary_key=True)
)    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    ingredients = relationship("UserIngredient", back_populates="user")

class UserIngredient(Base):
    __tablename__ = "user_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    quantity = Column(Integer, default=1)
    expiry_date = Column(Date)

    user = relationship("User", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="user_ingredients")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    default_shelf_life_days = Column(Integer, default=7, nullable=False)
    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredient_table,
        back_populates="ingredients"
    )
    user_ingredients = relationship("UserIngredient", back_populates="ingredient")
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredient_table,
        back_populates="recipes"
    )

    
