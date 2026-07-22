from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from auth import CurrentUser
import models
from auth import get_optional_current_user
from fastapi.responses import RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(
    request: Request,
    current_user: models.User | None = Depends(get_optional_current_user),
):
    if current_user:
        return RedirectResponse("/feed", status_code=303)

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "title": "Login",
        },
    )


@router.get("/register")
def register_page(
    request: Request,
    current_user: models.User | None = Depends(get_optional_current_user),
):
    if current_user:
        return RedirectResponse("/feed", status_code=303)

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