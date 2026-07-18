from typing import Annotated
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from auth import CurrentUser
import models

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "title": "Login",
        },
    )


@router.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "title": "Register",
        },
    )
@router.get("/feed")
def feed_page(
    request: Request,
    current_user: CurrentUser,
):

    return templates.TemplateResponse(
        request,
        "feed.html",
        {
            "title": "Feed",
            "current_user": current_user,
        }
    )