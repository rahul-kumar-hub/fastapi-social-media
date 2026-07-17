from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

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