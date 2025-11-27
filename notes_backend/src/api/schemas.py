from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the note")
    content: str = Field(..., min_length=1, description="Content/body of the note")
    archived: Optional[bool] = Field(default=False, description="Whether the note is archived")


class NoteCreate(NoteBase):
    """Schema for creating a note."""
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title")
    content: Optional[str] = Field(None, min_length=1, description="Updated content")
    archived: Optional[bool] = Field(None, description="Updated archived state")


class NoteOut(NoteBase):
    id: int = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
