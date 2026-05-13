from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from . import models
from .database import get_db
import os

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

router = APIRouter()

# --- Pydantic schemas ---

class CommentCreate(BaseModel):
    post_slug: str
    author_name: str
    content: str

class CommentResponse(BaseModel):
    id: int
    post_slug: str
    author_name: str
    content: str
    created_at: str

    class Config:
        from_attributes = True

# --- Helper ---

def verify_admin(x_api_key: Optional[str] = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# --- Routes ---

@router.post("/comments", status_code=201)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = models.Comment(
        post_slug=comment.post_slug,
        author_name=comment.author_name,
        content=comment.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {"message": "Comment submitted and awaiting approval"}

@router.get("/comments/{post_slug}")
def get_comments(post_slug: str, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(
        models.Comment.post_slug == post_slug,
        models.Comment.is_approved == True
    ).all()
    return comments

@router.patch("/comments/{comment_id}/approve")
def approve_comment(comment_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.is_approved = True
    db.commit()
    return {"message": "Comment approved"}

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}