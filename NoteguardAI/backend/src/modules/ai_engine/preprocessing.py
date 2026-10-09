import cv2
import numpy as np
from PIL import Image

class ImagePreprocessor:
    """
    Applies alignment, deskewing, and scale corrections to normalized input images.
    """
    def __init__(self, target_size: int = 224):
        self.target_size = target_size

    def align_and_deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Detects currency boundaries, determines rotation offsets, and returns an aligned, horizontal crop.
        """
        # Convert to grayscale and blur to remove noise
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image  # Fallback to unaligned if no contours detected
            
        # Get largest contour assuming it is the note
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get minimum bounding box area
        rect = cv2.minAreaRect(largest_contour)
        box = np.asarray(cv2.boxPoints(rect), dtype=np.int32)
        
        # Get width, height and rotation angle
        (cx, cy), (width, height), angle = rect
        
        # Correct rotation angle thresholds
        if angle < -45:
            angle = 90 + angle
            width, height = height, width
            
        # Rotate image using affine transform
        h, w = image.shape[:2]
        center = (int(cx), int(cy))
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        
        # Crop rotated note out
        x, y, w_box, h_box = cv2.boundingRect(box)
        
        # Ensure coordinates are within image boundaries
        x = max(0, x)
        y = max(0, y)
        w_box = min(w - x, w_box)
        h_box = min(h - y, h_box)
        
        cropped = rotated[y:y + h_box, x:x + w_box]
        if cropped.size == 0:
            return image
            
        return cropped

    def normalize_for_cnn(self, image: Image.Image) -> np.ndarray:
        """
        Resizes PIL image to standard CNN inputs, matching Keras ImageDataGenerator exactly.
        """
        # Keras ImageDataGenerator uses bilinear interpolation when resizing images.
        resized = image.resize((self.target_size, self.target_size), resample=Image.Resampling.BILINEAR)
        
        # Convert to numpy array
        img_array = np.array(resized, dtype=np.float32)
        
        # Expand dims for batch size 1: [1, 224, 224, 3]
        img_tensor = np.expand_dims(img_array, axis=0)
        return img_tensor
