from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import Base,engine
import models
from routers import users, posts

Base.metadata.create_all(engine)
app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static") 
app.mount("/media",StaticFiles(directory="media"),name="media") 

templates = Jinja2Templates(directory="templates")
app.include_router(users.router)
app.include_router(posts.router)
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "title": "Home page"
        }

    )