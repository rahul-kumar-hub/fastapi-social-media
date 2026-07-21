from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File, Query, Response
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, delete
import models, schemas
from schemas import Token, UserCreate, UserResponse, UserProfileResponse,UserPublic
from config import settings
from database import get_db
from auth import(
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
)
from utils.image import(
    process_profile_image,
    delete_profile_image,
)
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/users", #used to add the comman URL prefix to all routes in an APLRouter
    tags = ["Users"], # Used only for API documentation in swagger UI
)

@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data:schemas.UserCreate, db:Annotated[Session, Depends(get_db)],):
    result = db.execute(
        select(models.User).where(
            models.User.username==user_data.username.lower()
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    result = db.execute(
        select(models.User).where(
            models.User.email==user_data.email
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    new_user=models.User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends()
    ],
    db: Annotated[
        Session,
        Depends(get_db)
    ],
):
    result = db.execute(
        select(models.User).where(
            models.User.email==form_data.username.lower()
        )
    )
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.password_hash):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    # return Token(access_token=access_token, token_type="bearer")
    response = JSONResponse(
        content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "token_type": "bearer",
                }
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax",
    )
    return response

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user(
    current_user: CurrentUser
):
    return current_user

@router.patch("/me/picture", response_model=UserResponse)
def upload_profile_picture(

    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    
    content =file.file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)}MB",
        )    
    new_filename = process_profile_image(content)
    old_filename = current_user.image_file
    current_user.image_file = new_filename
    db.commit()
    db.refresh(current_user)

    if old_filename:
        delete_profile_image(old_filename)

    return current_user
## Delete Profile Picture Endpoint
@router.delete("/me/picture", response_model=UserResponse)
def delete_user_picture(

    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    
    old_filename = current_user.image_file
    if old_filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile picture to delete",
        )
    current_user.image_file = None
    db.commit()
    db.refresh(current_user)
    delete_profile_image(old_filename)
    return current_user
    
@router.get("/{user_id}/profile", response_model=UserProfileResponse) 
def get_user_profile(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.User)
        .options(selectinload(models.User.posts))
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user 

@router.get("/search", response_model=list[UserPublic])
def search_users(
    q: Annotated[str, Query(
        min_length=1, 
        max_length=50,
        description = "Search Users by Username"),
    ],
    db: Annotated[Session, Depends(get_db)]
):
    q = q.strip()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )
    result = db.execute(
        select(models.User).where(models.User.username.ilike(f"%{q}%")).limit(20)
    )
    
    users = result.scalars().all()
    return users

@router.get("/logout")
def logout():

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.delete_cookie("access_token")

    return response

@router.delete("/me")
def delete_account(
    data: schemas.DeleteAccountRequest,
    current_user: CurrentUser,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
):
    if not verify_password(
        data.password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    db.execute(
        delete(models.SavedPost).where(
            models.SavedPost.user_id == current_user.id
        )
    )
    db.execute(
        delete(models.Like).where(
            models.Like.user_id == current_user.id
        )
    )
    db.execute(
        delete(models.Comment).where(
            models.Comment.user_id == current_user.id
        )
    )
    db.execute(
        delete(models.Post).where(
            models.Post.user_id == current_user.id
        )
    )
    old_filename = current_user.image_file
    db.delete(current_user)
    db.commit()
    if old_filename:
        delete_profile_image(old_filename)

    response = RedirectResponse(
        url="/",
        status_code=303,
    )
    response.delete_cookie("access_token")
    return response
    
@router.get("/profile")
def profile_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUser,
):
    # Count user's posts
    total_posts = db.execute(
        select(func.count(models.Post.id))
        .where(models.Post.user_id == current_user.id)
    ).scalar_one()
    # Get latest 5 posts
    recent_posts = db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == current_user.id)
        .order_by(models.Post.date_posted.desc())
        .limit(5)
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "request": request,
            "title": "My Profile",
            "current_user": current_user,
            "total_posts": total_posts,
            "recent_posts": recent_posts,
        },
    )
@router.get("/settings")
def settings_page(
    request: Request,
    current_user: CurrentUser,
):
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "request": request,
            "title": "Settings",
            "current_user": current_user,
        },
    )

@router.patch("/me", response_model=UserResponse)
def update_current_user(
    user_data: schemas.UserUpdate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    # Username already taken?
    result = db.execute(
        select(models.User).where(
            models.User.username == user_data.username,
            models.User.id != current_user.id
        )
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )
    # Email already taken?
    result = db.execute(
        select(models.User).where(
            models.User.email == user_data.email,
            models.User.id != current_user.id
        )
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )
    current_user.username = user_data.username
    current_user.email = user_data.email
    db.commit()
    db.refresh(current_user)
    return current_user

@router.patch("/change-password")
def change_password(
    password_data: schemas.PasswordChange,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if not verify_password(
        password_data.current_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )
    current_user.password_hash = hash_password(
        password_data.new_password
    )
    db.commit()
    return {
        "message": "Password changed successfully"
    }