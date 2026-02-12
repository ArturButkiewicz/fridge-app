from uuid import uuid4

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Enum
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


# USERS

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    user_ingredients = relationship(
        "UserIngredient",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


# USER INGREDIENTS

class UserIngredient(Base):
    __tablename__ = "user_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity = Column(Integer, default=1, nullable=False)
    expiry_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="user_ingredients")
    ingredient = relationship("Ingredient", back_populates="user_ingredients")

    def __repr__(self):
        return f"<UserIngredient user_id={self.user_id} ingredient_id={self.ingredient_id}>"


# INGREDIENTS
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    default_shelf_life_days = Column(Integer, default=7, nullable=False)

    user_ingredients = relationship(
        "UserIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Ingredient id={self.id} name={self.name}>"


# RECIPES

class RecipeType(str, enum.Enum):
    internal = "internal"
    external = "external"

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, unique=True)

    description = Column(String, nullable=True)
    instructions = Column(Text, nullable=True)
    external_url = Column(String, nullable=True)

    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    recipe_type = Column(String, nullable=False)

    def __repr__(self):
        return f"<Recipe id={self.id} name={self.name}>"


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        primary_key=True,
    )

    amount = Column(String, nullable=True)

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return (
            f"<RecipeIngredient recipe_id={self.recipe_id} "
            f"ingredient_id={self.ingredient_id} amount={self.amount}>"
        )
