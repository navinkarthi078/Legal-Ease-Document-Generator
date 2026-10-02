"""
GeminiDocumentGenerator — wraps Google Generative AI (Gemini) to
produce structured legal documents from a structured prompt.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from project root .env
_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_ENV_PATH)


class GeminiDocumentGenerator:
    """Generates professional legal documents using Google Gemini API."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()

        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. Please add it to your .env file."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model_name)
        self.model_name = model_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        document_type: str,
        parties: str,
        terms: str,
        date: str,
        additional_context: str | None = None,
    ) -> str:
        """
        Generate a legal document and return it as a plain-text string.

        Args:
            document_type: E.g. "NDA", "Employment Contract", etc.
            parties: Comma-separated party names.
            terms: Semicolon-separated clauses / terms.
            date: Effective date string.
            additional_context: Optional free-text instructions.

        Returns:
            Generated document as a string.

        Raises:
            RuntimeError: If the Gemini API call fails.
        """
        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            date=date,
            additional_context=additional_context,
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text
        except Exception as exc:
            raise RuntimeError(f"Gemini API error: {exc}") from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        date: str,
        additional_context: str | None,
    ) -> str:
        """
        Construct a detailed, structured prompt that instructs Gemini to
        output a professional legal document.
        """
        # Parse parties and terms into lists for richer formatting
        party_list = [p.strip() for p in parties.split(",") if p.strip()]
        term_list = [t.strip() for t in terms.split(";") if t.strip()]

        parties_formatted = "\n".join(f"  - {p}" for p in party_list)
        terms_formatted = "\n".join(f"  * {t}" for t in term_list)

        extra_section = (
            f"\nAdditional Instructions:\n  {additional_context}\n"
            if additional_context
            else ""
        )

        prompt = f"""
You are an expert legal document drafting assistant with 20+ years of experience.
Generate a complete, professional, and legally sound {document_type} document.

=== DOCUMENT METADATA ===
Document Type  : {document_type}
Effective Date : {date}
Parties Involved:
{parties_formatted}

=== TERMS & CLAUSES TO INCLUDE ===
{terms_formatted}
{extra_section}
=== FORMATTING REQUIREMENTS ===
Structure the document with ALL of the following sections:

1. TITLE
   - Centered, uppercase, clearly identifying the document type.

2. PREAMBLE / INTRODUCTION
   - Identify all parties with their full descriptions.
   - State the effective date.
   - State the intent/purpose of the agreement.

3. DEFINITIONS
   - Define key terms used in the document.

4. NUMBERED CLAUSES
   - Convert each provided term into a formal, numbered legal clause.
   - Each clause must have a bold heading and a full paragraph explanation.

5. TERMS & CONDITIONS
   - List specific obligations, rights, and restrictions as bullet points
     under each relevant numbered clause.

6. REPRESENTATIONS AND WARRANTIES
   - Each party's representations and warranties.

7. LIMITATION OF LIABILITY
   - Standard limitation of liability clause.

8. DISPUTE RESOLUTION
   - Governing law and dispute resolution mechanism.

9. TERMINATION
   - Conditions under which the agreement may be terminated.

10. ENTIRE AGREEMENT
    - Boilerplate entire agreement / merger clause.

11. SIGNATURE BLOCK
    - Signature lines for each party with:
      Name: ________________
      Title: ________________
      Date: ________________
      Signature: ________________

=== STYLE REQUIREMENTS ===
- Use formal legal language throughout.
- Paragraphs must be properly indented.
- Use "WHEREAS" and "NOW, THEREFORE" in the recitals where appropriate.
- All clauses must be numbered (1., 1.1, 1.2, etc.).
- Do NOT include any markdown symbols like **, ##, or *.
- Output plain text only — the document will be rendered as-is.
- Ensure the document is complete, enforceable-sounding, and professional.

Generate the full {document_type} document now:
"""
        return prompt.strip()
