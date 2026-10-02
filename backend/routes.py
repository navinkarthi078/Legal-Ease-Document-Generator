"""
API route definitions for LegalEase backend.
Registers the POST /generate endpoint.
"""
import sys
import os

# Ensure project root is on the path so `utils` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from backend.models import DocumentRequest, DocumentResponse, ErrorResponse
from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from utils.sanitizer import sanitize_text

router = APIRouter()


@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a legal document using Gemini AI",
    responses={
        400: {"model": ErrorResponse, "description": "Bad request / validation error"},
        500: {"model": ErrorResponse, "description": "Server or AI API error"},
    },
)
async def generate_document(request: DocumentRequest) -> JSONResponse:
    """
    Generate a legal document based on the provided metadata.

    - **document_type**: The type of document (NDA, Employment Contract, etc.)
    - **parties**: Comma-separated list of party names
    - **terms**: Semicolon-separated list of terms/clauses
    - **date**: Effective date of the agreement
    - **additional_context**: Optional extra instructions for the AI
    """
    # Validate that required fields are non-empty after stripping
    missing = []
    for field in ("document_type", "parties", "terms", "date"):
        if not getattr(request, field, "").strip():
            missing.append(field)

    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following required fields are empty: {', '.join(missing)}",
        )

    try:
        generator = GeminiDocumentGenerator()
    except EnvironmentError as env_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(env_err),
        )

    try:
        raw_text = generator.generate(
            document_type=request.document_type.strip(),
            parties=request.parties.strip(),
            terms=request.terms.strip(),
            date=request.date.strip(),
            additional_context=request.additional_context,
        )
    except RuntimeError as rt_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {rt_err}",
        )

    # Sanitize the AI output
    clean_text = sanitize_text(raw_text)

    return JSONResponse(
        content={
            "success": True,
            "document_type": request.document_type.strip(),
            "generated_text": clean_text,
            "message": "Document generated successfully.",
        }
    )


@router.get("/health", summary="Health check")
async def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "LegalEase API"}
