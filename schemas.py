from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
# ConfigDict -> through this  FASTAPI convert SQLAlchemy objects into JSON automatically

class UserBase(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )
    email: EmailStr = Field(
        max_length=120,
    )
class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=128,
    )
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)#from_attributes=True -> through this  FASTAPI convert SQLAlchemy objects into JSON automatically
    id: int
    image_file:str| None
    image_path : str
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)#from_attributes=True -> through this  FASTAPI convert SQLAlchemy objects into JSON automatically
    id: int
    username: str
    image_file:str| None
    image_path : str

class UserProfileResponse(UserResponse):
    posts: list[PostResponse]

class UserUpdate(BaseModel):
    username: str
    email: EmailStr

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)

class PostCreate(PostBase):
    pass
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id:int
    date_posted:datetime
    author: UserPublic
    cover_image: str | None
    cover_image_path: str
    like_count: int=0
    comment_count: int=0
    is_saved: bool = False

class PostUpdate(BaseModel):  
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)

class PaginatedPostsResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    size: int
    total_pages:int
    has_next:bool
    has_previous:bool

class CommentBase(BaseModel):
    content: str = Field(min_length=1)
class CommentCreate(CommentBase):
    pass
class CommentUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)
class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_posted: datetime
    author: UserResponse

class PasswordChange(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)

class DeleteAccountRequest(BaseModel):
    password: str

class LikeResponse(BaseModel):
    message: str
    like_count: int
    liked: bool