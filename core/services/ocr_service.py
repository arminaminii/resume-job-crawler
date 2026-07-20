import pytesseract
from PIL import Image
import pdf2image
import os


def extract_text_from_image(image_path: str) -> str:
    """Extract text from image files (PNG, JPG, etc.) using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='fas+ara+eng')
        return text.strip()
    except Exception as e:
        return f"[OCR Error: {str(e)}]"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF files. Uses pdf2image + Tesseract for scanned PDFs."""
    text_parts = []

    try:
        images = pdf2image.convert_from_path(pdf_path, dpi=300)
        for img in images:
            text = pytesseract.image_to_string(img, lang='fas+ara+eng')
            text_parts.append(text.strip())
        return '\n'.join(text_parts)
    except Exception:
        # Fallback: try PyPDF2/pdfplumber if available for text-based PDFs
        try:
            import PyPDF2
            text_parts = []
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            if text_parts:
                return '\n'.join(text_parts)
        except ImportError:
            pass
        return ""


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX files."""
    try:
        from docx import Document
        doc = Document(docx_path)
        return '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    except ImportError:
        return ""


def extract_resume_text(file_path: str) -> str:
    """Main entry point: extract text from any resume file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp'):
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ('.docx', '.doc'):
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        return ""