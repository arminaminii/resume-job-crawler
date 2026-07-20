import pytesseract
import logging
from PIL import Image
import os

logger = logging.getLogger(__name__)


def _setup_tesseract():
    """Configure Tesseract path from Django settings."""
    try:
        from django.conf import settings
        tesseract_cmd = getattr(settings, 'TESSERACT_CMD', None)
        if tesseract_cmd and os.path.isfile(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Tesseract configured: {tesseract_cmd}")
        else:
            logger.warning(f"Tesseract path not found, using system default")
    except Exception as e:
        logger.warning(f"Could not configure Tesseract path: {e}")


def _get_poppler_path():
    """Get Poppler bin directory from Django settings."""
    try:
        from django.conf import settings
        poppler_path = getattr(settings, 'POPPLER_PATH', '')
        if poppler_path and os.path.isdir(poppler_path):
            return poppler_path
    except Exception:
        pass
    return None


def extract_text_from_image(image_path: str) -> str:
    """Extract text from image files (PNG, JPG, etc.) using Tesseract OCR."""
    _setup_tesseract()
    try:
        logger.info(f"OCR: processing image {image_path}")
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='fas+ara+eng')
        result = text.strip()
        logger.info(f"OCR: extracted {len(result)} chars from image")
        return result
    except Exception as e:
        logger.error(f"OCR image error: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF files. Uses pdf2image + Tesseract for scanned PDFs."""
    _setup_tesseract()
    poppler_path = _get_poppler_path()
    text_parts = []

    # Try pdf2image (requires Poppler) for image-based or all PDFs
    try:
        import pdf2image
        kwargs = {'dpi': 300}
        if poppler_path:
            kwargs['poppler_path'] = poppler_path

        logger.info(f"OCR: converting PDF to images (poppler={poppler_path or 'system'})")
        images = pdf2image.convert_from_path(pdf_path, **kwargs)
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='fas+ara+eng')
            text_parts.append(text.strip())
            logger.info(f"OCR: PDF page {i+1}: extracted {len(text.strip())} chars")

        result = '\n'.join(text_parts)
        if result.strip():
            return result
    except Exception as e:
        logger.warning(f"PDF pdf2image failed: {e}, trying text extraction fallback")

    # Fallback 1: PyMuPDF (fitz) - best for text-based PDFs
    try:
        import fitz  # PyMuPDF
        logger.info("OCR: trying PyMuPDF text extraction")
        doc = fitz.open(pdf_path)
        for page in doc:
            t = page.get_text()
            if t.strip():
                text_parts.append(t.strip())
        doc.close()
        result = '\n'.join(text_parts)
        if result.strip():
            logger.info(f"OCR: PyMuPDF extracted {len(result)} chars")
            return result
    except ImportError:
        logger.debug("PyMuPDF not installed, skipping")
    except Exception as e:
        logger.debug(f"PyMuPDF extraction failed: {e}")

    # Fallback 2: PyPDF2
    try:
        import PyPDF2
        logger.info("OCR: trying PyPDF2 text extraction")
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t and t.strip():
                    text_parts.append(t.strip())
        result = '\n'.join(text_parts)
        if result.strip():
            logger.info(f"OCR: PyPDF2 extracted {len(result)} chars")
            return result
    except ImportError:
        logger.debug("PyPDF2 not installed, skipping")
    except Exception as e:
        logger.debug(f"PyPDF2 extraction failed: {e}")

    logger.error("OCR: all PDF extraction methods failed")
    return ""


def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from DOCX files."""
    try:
        from docx import Document
        logger.info(f"OCR: extracting DOCX {docx_path}")
        doc = Document(docx_path)
        text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        logger.info(f"OCR: DOCX extracted {len(text)} chars")
        return text
    except ImportError:
        logger.error("python-docx not installed, cannot extract DOCX")
        return ""
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


def extract_resume_text(file_path: str) -> str:
    """Main entry point: extract text from any resume file."""
    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"OCR: starting extraction for {file_path} (ext={ext})")

    if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp'):
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ('.docx', '.doc'):
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            logger.info(f"OCR: TXT extracted {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"TXT read error: {e}")
            return ""
    else:
        logger.warning(f"OCR: unsupported file type: {ext}")
        return ""