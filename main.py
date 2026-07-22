from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from database import Base,engine,get_db
import models
from routers import users, posts, comments, pages
from auth import get_optional_current_user
from middleware import NoCacheMiddleware



Base.metadata.create_all(engine)
app = FastAPI()
app.add_middleware(NoCacheMiddleware)
app.mount("/static",StaticFiles(directory="static"),name="static") 
app.mount("/media",StaticFiles(directory="media"),name="media") 

templates = Jinja2Templates(directory="templates")
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(pages.router)
@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_optional_current_user),
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
            "total_comments": total_comments,
            "current_user": current_user,
        }
    )
@app.exception_handler(HTTPException)
def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == HTTP_401_UNAUTHORIZED:

        accept = request.headers.get("accept", "")

        # Browser requesting an HTML page
        if "text/html" in accept:
            return RedirectResponse(
                url="/",
                status_code=303,
            )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )