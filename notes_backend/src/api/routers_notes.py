from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Note, get_db
from .schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes",
    description="Returns a list of notes. Supports optional search by title and archived filtering.",
)
def list_notes(
    q: Optional[str] = Query(None, description="Search query to filter notes by title"),
    archived: Optional[bool] = Query(None, description="Filter by archived status"),
    db: Session = Depends(get_db),
):
    """List notes with optional search and archived filtering."""
    stmt = select(Note)
    if q:
        # Simple case-insensitive contains search
        stmt = stmt.where(Note.title.ilike(f"%{q}%"))
    if archived is not None:
        stmt = stmt.where(Note.archived == archived)
    stmt = stmt.order_by(Note.updated_at.desc())
    notes = db.execute(stmt).scalars().all()
    return notes


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get note by ID",
    description="Fetches a single note by its identifier.",
    responses={404: {"description": "Note not found"}},
)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Retrieve a note by ID or 404 if not found."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Creates a new note with title and content.",
    responses={400: {"description": "Validation error"}},
)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note."""
    note = Note(title=payload.title, content=payload.content, archived=payload.archived or False)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Updates an existing note. Any provided fields will be applied.",
    responses={404: {"description": "Note not found"}},
)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    """Update note by ID."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.archived is not None:
        note.archived = payload.archived

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Deletes a note by its identifier.",
    responses={404: {"description": "Note not found"}},
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note by ID."""
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db.delete(note)
    db.commit()
    return None
