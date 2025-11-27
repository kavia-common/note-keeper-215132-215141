from datetime import datetime
from typing import Optional, List
from uuid import UUID as PyUUID

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the note")
    content: str = Field(..., min_length=1, description="Content/body of the note")
    # Preserve external API field name 'archived' while mapping internally to is_archived
    archived: Optional[bool] = Field(default=False, description="Whether the note is archived")
    # New: tags field (jsonb) exposed as list of strings
    tags: Optional[List[str]] = Field(default_factory=list, description="List of tags for the note")


class NoteCreate(NoteBase):
    """Schema for creating a note."""
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title")
    content: Optional[str] = Field(None, min_length=1, description="Updated content")
    archived: Optional[bool] = Field(None, description="Updated archived state")
    tags: Optional[List[str]] = Field(None, description="Updated tags list")


class NoteOut(NoteBase):
    # Expose id as string to be compatible with UUIDs while keeping contract stable
    id: PyUUID | str = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
