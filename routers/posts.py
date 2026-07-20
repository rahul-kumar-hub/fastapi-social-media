from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select,func, or_
import math 
from sqlalchemy.orm import selectinload

import models
import schemas
from auth import CurrentUser
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostsResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from auth import get_optional_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)
templates = Jinja2Templates(directory="templates")

@router.get("/create")
def create_post_page(
    request: Request,
    current_user: Annotated[
        models.User | None,
        Depends(get_optional_current_user)
    ],
):
    if current_user is None:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        request,
        "create_post.html",
        {
            "request": request,
            "title": "Write Story",
            "current_user": current_user,
        },
    )
@router.post(
    "",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    post_data: PostCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    new_post = models.Post(
        title=post_data.title,
        content=post_data.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post,attribute_names=["author"]) 
    return new_post

@router.get(
    "",
    response_model=PaginatedPostsResponse,
)
def get_posts(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    sort: Annotated[str, Query(pattern="^(newest|oldest)$")] = "newest",
    author_id: Annotated[int | None, Query(ge=1)] = None,
):
    # Calculate offset
    offset = (page - 1) * size
    # Count Query
    count_query = select(func.count(models.Post.id))
    if author_id is not None:
        count_query = count_query.where(
            models.Post.user_id == author_id
        )
    total = db.execute(count_query).scalar_one()
    # Pagination Metadata
    total_pages = math.ceil(total / size) if total else 1

    has_next = page < total_pages
    has_previous = page > 1
    # Sorting
    if sort == "newest":
        order = models.Post.date_posted.desc()
    else:
        order = models.Post.date_posted.asc()
    # Build Query
    query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
    )
    # Optional Filter
    if author_id is not None:
        query = query.where(
            models.Post.user_id == author_id
        )
    # Sorting + Pagination
    query = (
        query
        .order_by(order)
        .offset(offset)
        .limit(size)
    )
    # Execute Query
    result = db.execute(query)
    posts = result.scalars().all()
    # Response
    return PaginatedPostsResponse(
        items=posts,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )

@router.get("/page")
def blogs_page(
    request: Request,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    current_user: Annotated[
        models.User | None,
        Depends(get_optional_current_user)
    ],
    search: str | None = Query(default=None),
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=20)] = 6,
):
    query = (
        select(models.Post)
        .options(selectinload(models.Post.author))
    )
    # Search
    if search:
        query = query.where(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%"),
            )
        )
# Count total results
    count_query = select(func.count(models.Post.id))
    if search:
        count_query = count_query.where(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%"),
            )
        )
    total_posts = db.scalar(count_query)
# Pagination
    total_pages = max(1, math.ceil(total_posts / size))
    query = (
        query
        .order_by(models.Post.date_posted.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    posts = db.execute(query).scalars().all()
    return templates.TemplateResponse(
    request,
    "blogs.html",
    {
        "title": "Blogs",
        "posts": posts,
        "current_user": current_user,
        "search": search,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    },
)
@router.get("/my-posts")
def my_posts_page(
    request: Request,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    current_user: CurrentUser,
):
    posts = db.execute(
        select(models.Post)
        .options(
            selectinload(models.Post.author)
        )
        .where(
            models.Post.user_id == current_user.id
        )
        .order_by(
            models.Post.date_posted.desc()
        )
    ).scalars().all()

    return templates.TemplateResponse(
        request,
        "my_posts.html",
        {
            "request": request,
            "title": "My Posts",
            "posts": posts,
            "current_user": current_user,
        },
    )
@router.post("/{post_id}/save")
def toggle_save(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
):

    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )
    existing = db.get(
        models.SavedPost,
        (current_user.id, post_id),
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {
            "message": "Removed from saved"
        }
    saved = models.SavedPost(
        user_id=current_user.id,
        post_id=post_id,
    )
    db.add(saved)
    db.commit()
    return {
        "message": "Post saved"
    }

@router.get("/saved")
def saved_posts_page(
    request: Request,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    current_user: CurrentUser,
):
    saved = db.execute(
        select(models.SavedPost)
        .options(
            selectinload(models.SavedPost.post)
            .selectinload(models.Post.author)
        )
        .where(
            models.SavedPost.user_id == current_user.id
        )
    ).scalars().all()
    return templates.TemplateResponse(
        request,
        "saved_posts.html",
        {
            "request": request,
            "title": "Saved Posts",
            "saved_posts": saved,
            "current_user": current_user,
        },
    )

@router.get("/edit/{post_id}")
def edit_post_page(
    post_id: int,
    request: Request,
    db: Annotated[
        Session,
        Depends(get_db)
    ],
    current_user: CurrentUser,
):
    post = db.scalar(
        select(models.Post)
        .where(models.Post.id == post_id)
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return templates.TemplateResponse(
        request,
        "edit_post.html",
        {
            "request": request,
            "title": "Edit Post",
            "post": post,
            "current_user": current_user,
        },
    )
@router.get("/blog/{post_id}")
def blog_post(
    request: Request,
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[
        models.User | None,
        Depends(get_optional_current_user)
    ],
):
   post = db.scalar(
    select(models.Post)
    .options(selectinload(models.Post.author))
    .where(models.Post.id == post_id)
)
   if post is None:
    raise HTTPException(
        status_code=404,
        detail="Post not found"
    )
   return templates.TemplateResponse(
    request,
    "post_detail.html",
    {
        "title": post.title,
        "post": post,
        "current_user":current_user,
    }
)
@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


        
@router.put("/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int, 
    post_data: PostCreate,
    current_user:CurrentUser, 
    db: Annotated[Session, Depends(get_db)],
):
    result =db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # ownership check 
    if post.user_id!=current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this post",
        )
    post.title = post_data.title
    post.content = post_data.content
    db.commit()
    db.refresh(post, attribute_names=["author"])
    return post

@router.patch("/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int, 
    post_data: PostUpdate, 
    current_user:CurrentUser, 
    db: Annotated[Session, Depends(get_db)],
):
    result =db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    #ownership check
    if post.user_id!=current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    update_data=post_data.model_dump(exclude_unset=True) #exclude_unset=True → only include fields that were provided in the request (not None)
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post,attribute_names=["author"]) 
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, current_user:CurrentUser,db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, 
           detail="Post not found",
        )
    #ownership check
    if post.user_id!=current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )
    db.delete(post)
    db.commit()

@router.post(
    "/{post_id}/like",
)
def toggle_like(post_id:int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    post = db.get(models.Post,post_id)
    if post is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="post not found",
        )
    result = db.execute(
        select(models.Like)
        .where(models.Like.user_id==current_user.id, models.Like.post_id==post_id)
    )
    existing_like = result.scalar_one_or_none()
    if existing_like:
        db.delete(existing_like)
        message = "Post unliked"
    else:
        like = models.Like(
            user=current_user,
            post=post,
        )
        db.add(like)
        message = "Post liked"

    db.commit()
    count = db.execute(
        select(func.count(models.Like.id))
        .where(models.Like.post_id==post_id)
    ).scalar_one()
    return {
        "message": message,
        "like_count": count,
    }