from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app import crud, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Fridge App Backend")

# --- Users ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

# --- Ingredients ---
@app.post("/ingredients/", response_model=schemas.Ingredient)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    return crud.create_ingredient(db, ingredient)

@app.get("/ingredients/", response_model=list[schemas.Ingredient])
def read_ingredients(db: Session = Depends(get_db)):
    return crud.get_ingredients(db)

# --- User Ingredients ---
@app.post("/users/{user_id}/ingredients/", response_model=schemas.UserIngredient)
def add_user_ingredient(user_id: int, ui: schemas.UserIngredientCreate, db: Session = Depends(get_db)):
    return crud.add_user_ingredient(db, user_id, ui)

@app.get("/users/{user_id}/ingredients/", response_model=list[schemas.UserIngredient])
def get_user_ingredients(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_ingredients(db, user_id)

@app.get("/")
def root():
    return {"message": "Fridge App Backend działa!"}
