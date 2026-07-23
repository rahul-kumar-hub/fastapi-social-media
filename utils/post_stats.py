from sqlalchemy import select, func
from sqlalchemy.orm import Session

import models


def get_like_counts(db: Session):

    rows = db.execute(
        select(
            models.Like.post_id,
            func.count(models.Like.id)
        )
        .group_by(models.Like.post_id)
    ).all()

    return {
        post_id: count
        for post_id, count in rows
    }


def get_comment_counts(db: Session):

    rows = db.execute(
        select(
            models.Comment.post_id,
            func.count(models.Comment.id)
        )
        .group_by(models.Comment.post_id)
    ).all()

    return {
        post_id: count
        for post_id, count in rows
    }