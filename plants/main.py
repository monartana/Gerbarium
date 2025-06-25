from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import threading

from plant.api_router import router as plant_api_router
from plant.view_router import router as plant_view_router
from plant.identification_router import router as plant_identification_router
from auth.api_router import router as auth_api_router
from auth.view_router import router as auth_view_router
from comment.api_router import router as comment_api_router
from comment.view_router import router as comment_view_router
from favorite.api_router import router as favorite_api_router
from favorite.view_router import router as favorite_view_router
from dashboard.plant_view_router import router as dashboard_plant_view_router
from plant.bot import run_bot

from database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(plant_api_router, prefix="/api/plants", tags=["plants-api"])
app.include_router(plant_view_router, prefix="/plants", tags=["plants-view"])
app.include_router(plant_identification_router, prefix="/api/plants", tags=["plants-identification"])
app.include_router(auth_api_router, prefix="/api/auth", tags=["auth-api"])
app.include_router(auth_view_router, prefix="/auth", tags=["auth-view"])
app.include_router(comment_api_router, prefix="/api/comments", tags=["comments-api"])
app.include_router(comment_view_router, prefix="/comments", tags=["comments-view"])
app.include_router(favorite_api_router, prefix="/api/favorites", tags=["favorites-api"])
app.include_router(favorite_view_router, prefix="/favorites", tags=["favorites-view"])
app.include_router(dashboard_plant_view_router, prefix="/dashboard/plants", tags=["dashboard-plant-view"])

# Start the bot in a background thread
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()