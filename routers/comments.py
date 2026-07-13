from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
import models
from auth import CurrentUser
from database import get_db
from schemas import CommentCreate, CommentResponse

router = APIRouter(
    prefix="/posts/{post_id}/comments",
    tags=["Comments"],
)

@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    comment = models.Comment(
        content=comment_data.content,
        author=current_user,
        post=post,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get(
    "",
    response_model = list[CommentResponse],
)
def get_comments(
    post_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    post = db.get(models.Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    result = db.execute(
        select(models.Comment)
        .where(models.Comment.post_id == post_id)
        .options(selectinload(models.Comment.author))
    )
    comments = result.scalars().all()
    return comments 

@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    comment = db.get(models.Comment, comment_id)
    if comment is None: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    #ownership check
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )
    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)
    return comment

@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    comment = db.get(models.Comment, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    #ownership check
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )
    db.delete(comment)
    db.commit()