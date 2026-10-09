import io
import numpy as np
import cv2
from PIL import Image, UnidentifiedImageError
from src.modules.ai_engine.exceptions import (
    InvalidImageException,
    UnsupportedFormatException,
    ImageTooLargeException,
    ImageUnreadableException,
    ImageTooSmallException,
    ExtremeAspectRatioException,
)

class ImageValidator:
    """
    Validates uploaded raw currency images securely, using content-based MIME checks (PIL),
    size constraints, and dimensionality checks before allowing decoding for CNN inference.
    """
    def __init__(self, min_width: int = 32, min_height: int = 32):
        self.min_width = min_width
        self.min_height = min_height
        self.max_size_bytes = 20 * 1024 * 1024  # 20 MB
        self.min_size_bytes = 100               # 100 bytes
        self.supported_formats = {'JPEG', 'PNG', 'MPO', 'WEBP', 'BMP', 'TIFF', 'GIF'}
        
        # Protect against decompression bomb attacks
        Image.MAX_IMAGE_PIXELS = 100_000_000

    def validate_and_decode(self, image_bytes: bytes) -> Image.Image:
        """
        Safely validates the byte stream and decodes it into an OpenCV matrix.
        Throws appropriate taxonomy exceptions on failure.
        """
        # 1. Size Constraints
        size = len(image_bytes)
        if size == 0:
            raise InvalidImageException("Empty image upload detected.")
        if size < self.min_size_bytes:
            raise InvalidImageException("Image file size is too small (under 100 bytes).")
        if size > self.max_size_bytes:
            raise ImageTooLargeException("Image file size exceeds the 20MB limit.")

        # 2. Content-based Format Verification
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            img_format = (pil_img.format or "").upper()
            
            if img_format not in self.supported_formats:
                raise UnsupportedFormatException(f"Unsupported image format: {img_format}. Must be JPG, PNG, or WEBP.")
                
            w, h = pil_img.size
            
            # 3. Dimension Constraints
            if w < self.min_width or h < self.min_height:
                raise ImageTooSmallException(f"Image resolution too low ({w}x{h}). Minimum is {self.min_width}x{self.min_height}.")
                
            # 4. Aspect Ratio Constraints
            ratio = max(w, h) / max(min(w, h), 1)
            if ratio > 15.0:
                raise ExtremeAspectRatioException(f"Image aspect ratio is too extreme ({w}x{h}).")
                
        except UnidentifiedImageError:
            raise ImageUnreadableException("The uploaded file is corrupted or is not a valid image.")
        except ImageTooLargeException as e:
            raise e
        except Exception as e:
            if isinstance(e, (UnsupportedFormatException, ImageTooSmallException, ExtremeAspectRatioException)):
                raise e
            raise ImageUnreadableException(f"Failed to read image headers: {str(e)}")
            
        # 5. Apply EXIF orientation and ensure RGB
        from PIL import ImageOps
        try:
            pil_img = ImageOps.exif_transpose(pil_img)
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            return pil_img
        except Exception as e:
            raise ImageUnreadableException(f"Error during EXIF transposition or RGB conversion: {str(e)}")
