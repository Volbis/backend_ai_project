import os
import magic
import logging
from pdf2image import convert_from_path
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image

logger = logging.getLogger('ai_engine')

# Get settings from Django config
ALLOWED_MIME_TYPES = getattr(settings, 'ALLOWED_MIME_TYPES', [
    'image/jpeg',
    'image/png',
    'image/jpg',
    'application/pdf',
])

ALLOWED_FILE_EXTENSIONS = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', [
    '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'
])

MAX_FILE_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)  # 10MB default

def validate_file(file):
    """Validate uploaded file type and size"""
    # Check if file exists
    if not file:
        raise ValidationError("No file provided")
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size ({file.size / (1024 * 1024):.2f}MB) exceeds "
            f"{MAX_FILE_SIZE / (1024 * 1024)}MB limit"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(
            f"File extension '{file_ext}' is not allowed. "
            f"Allowed extensions: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Check MIME type
    try:
        file.seek(0)
        mime = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)
        
        if mime not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"File type '{mime}' is not allowed. "
                f"Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
            )
    except Exception as e:
        logger.warning(f"MIME type detection failed: {e}. Relying on extension check.")
    
    logger.info(f"File validation passed: {file.name} (size: {file.size / 1024:.2f}KB)")
    return True

def pdf_to_images(pdf_path: str, output_dir: str) -> list:
    """Convert PDF to images. Returns list of image paths."""
    try:
        logger.info(f"Converting PDF to images: {pdf_path}")
        images = convert_from_path(pdf_path, dpi=300)
        
        image_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.jpg")
            image.save(image_path, 'JPEG')
            image_paths.append(image_path)
            
        logger.info(f"Converted PDF to {len(image_paths)} images")
        return image_paths
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        return []

def preprocess_image(image_path: str) -> str:
    """Basic image preprocessing (resize if too large)"""
    try:
        img = Image.open(image_path)
        
        # Resize if image is too large (max 4000px on longest side)
        max_dimension = 4000
        if max(img.size) > max_dimension:
            logger.info(f"Resizing image {image_path} from {img.size}")
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            img.save(image_path)
            logger.info(f"Image resized to {new_size}")
            
        return image_path
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return image_path
