from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from database import Base,engine,get_db
import models
from routers import users, posts, comments


Base.metadata.create_all(engine)
app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static") 
app.mount("/media",StaticFiles(directory="media"),name="media") 

templates = Jinja2Templates(directory="templates")
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(models.Post)
        .order_by(models.Post.date_posted.desc())
    )
    posts = result.scalars().all()
    total_posts = db.scalar(select(func.count(models.Post.id)))
    total_users = db.scalar(select(func.count(models.User.id)))
    total_comments = db.scalar(select(func.count(models.Comment.id)))
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "title": "BlogSphere",
            "posts": posts,
            "total_posts": total_posts,
            "total_users": total_users,
            "total_comments": total_comments
        }
)