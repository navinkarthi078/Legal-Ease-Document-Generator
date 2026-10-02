"""
Text sanitization utilities for LegalEase.
Cleans and normalises user input and AI-generated output before
it is formatted or stored.
"""
import re
import unicodedata


def sanitize_text(text: str) -> str:
    """
    Sanitize raw text by:
      1. Normalising Unicode characters to NFC form.
      2. Stripping leading/trailing whitespace.
      3. Replacing smart/curly quotes with straight quotes.
      4. Removing non-printable control characters (except newlines/tabs).
      5. Collapsing more-than-two consecutive blank lines to two.
      6. Removing null bytes.

    Args:
        text: The raw input string.

    Returns:
        A cleaned, sanitised string safe for downstream processing.
    """
    if not isinstance(text, str):
        raise TypeError(f"sanitize_text expects a str, got {type(text).__name__}.")

    # 1. Unicode normalisation
    text = unicodedata.normalize("NFC", text)

    # 2. Strip surrounding whitespace
    text = text.strip()

    # 3. Replace smart/curly quotes
    replacements = {
        "\u2018": "'",    # left single quotation mark
        "\u2019": "'",    # right single quotation mark
        "\u201c": '"',    # left double quotation mark
        "\u201d": '"',    # right double quotation mark
        "\u2013": "-",    # en dash
        "\u2014": "--",   # em dash
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",    # non-breaking space
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # 4. Remove non-printable control characters (keep \n, \r, \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 5. Collapse excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. Remove null bytes
    text = text.replace("\x00", "")

    return text


def sanitize_filename(name: str) -> str:
    """
    Convert a string into a safe filename by removing or replacing
    characters that are illegal on Windows/Linux/macOS.

    Args:
        name: Proposed filename (without extension).

    Returns:
        A filesystem-safe filename string.
    """
    # Remove characters not allowed in filenames
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Strip leading/trailing dots and spaces
    name = name.strip(". ")
    # Truncate to 200 chars max
    return name[:200] or "document"
