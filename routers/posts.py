from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select,func
import math 
from sqlalchemy.orm import selectinload

import models
import schemas
from auth import CurrentUser
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostsResponse

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
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

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = result.scalar().first()
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
async def update_post_partial(
    post_id: int, 
    post_data: PostUpdate, 
    current_user:CurrentUser, 
    db: Annotated[Session, Depends(get_db)],
):
    result =await db.execute(select(models.Post).where(models.Post.id == post_id))
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
    await db.commit()
    await db.refresh(post,attribute_names=["author"]) 
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