import os
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image using PyTesseract OCR."""
    path = Path(image_path)
    if not path.exists():
        return f"Error: Image file '{image_path}' not found."

    if Image is None or pytesseract is None:
        return "OCR Error: Pillow or PyTesseract library not available."

    try:
        img = Image.open(image_path)
        extracted = pytesseract.image_to_string(img)
        if not extracted.strip():
            return "OCR Output: No text detected in image."
        return f"OCR Extracted Text:\n{extracted}"
    except Exception as e:
        return f"OCR Execution Error: {str(e)}"
