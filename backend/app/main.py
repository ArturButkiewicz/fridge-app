from fastapi import FastAPI
from app.database import Base, engine
from app.routers import ingredients, users, user_ingredients, recipes

# Create database tables (for now, without Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fridge App Backend")

app.include_router(ingredients.router)
app.include_router(users.router)
app.include_router(user_ingredients.router)
app.include_router(recipes.router)

# --- Root endpoint ---
@app.get("/")
def root():
    """Root endpoint to check API status."""
    return {"message": "Fridge App Backend working!"}
