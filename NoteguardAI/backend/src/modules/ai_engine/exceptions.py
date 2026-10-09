class AIException(Exception):
    """Base exception for all AI/ML/CV operations."""
    pass

class ImageValidationException(AIException):
    """Raised when an uploaded image fails format or resolution quality tests."""
    pass

class InvalidImageException(ImageValidationException):
    pass

class UnsupportedFormatException(ImageValidationException):
    pass

class ImageTooLargeException(ImageValidationException):
    pass

class ImageUnreadableException(ImageValidationException):
    pass

class ImageTooSmallException(ImageValidationException):
    pass

class ExtremeAspectRatioException(ImageValidationException):
    pass

class ModelLoadException(AIException):
    """Raised when model weights cannot be loaded into memory."""
    pass

class InferenceException(AIException):
    """Raised when model inference execution fails."""
    pass
