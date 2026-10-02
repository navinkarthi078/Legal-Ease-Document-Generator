"""
Pydantic models for LegalEase API request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class DocumentRequest(BaseModel):
    """Request model for document generation."""

    document_type: str = Field(
        ...,
        description="Type of legal document to generate",
        example="NDA",
    )
    parties: str = Field(
        ...,
        description="Names of the parties involved (comma-separated)",
        example="Acme Corp, John Doe",
    )
    terms: str = Field(
        ...,
        description="Terms/clauses for the document (semicolon-separated)",
        example="Confidentiality period: 2 years; Jurisdiction: New York",
    )
    date: str = Field(
        ...,
        description="Effective date of the document",
        example="2026-01-01",
    )
    additional_context: Optional[str] = Field(
        default=None,
        description="Any additional context or special instructions",
    )

    @validator("document_type")
    def validate_document_type(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("document_type must not be empty.")
        return v

    @validator("parties")
    def validate_parties(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("parties must not be empty.")
        return v

    @validator("terms")
    def validate_terms(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("terms must not be empty.")
        return v

    @validator("date")
    def validate_date(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("date must not be empty.")
        return v

    class Config:
        schema_extra = {
            "example": {
                "document_type": "NDA",
                "parties": "Acme Corp, John Doe",
                "terms": "Confidentiality period: 2 years; Jurisdiction: New York; Governing law: Delaware",
                "date": "2026-01-01",
                "additional_context": None,
            }
        }


class DocumentResponse(BaseModel):
    """Response model returned after document generation."""

    success: bool
    document_type: str
    generated_text: str
    message: str = "Document generated successfully."

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "document_type": "NDA",
                "generated_text": "NON-DISCLOSURE AGREEMENT\n\n...",
                "message": "Document generated successfully.",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""

    success: bool = False
    error: str
    detail: Optional[str] = None
