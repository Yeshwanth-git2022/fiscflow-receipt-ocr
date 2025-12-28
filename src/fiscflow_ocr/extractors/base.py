"""Base extractor interface."""
from abc import ABC, abstractmethod
from typing import Optional

from ..models.receipt import Receipt


class BaseExtractor(ABC):
    """
    Abstract base class for receipt extractors.

    All extractors must implement the extract() method.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        model_path: Optional[str] = None,
        min_confidence: float = 0.5,
        **kwargs
    ):
        """
        Initialize extractor.

        Args:
            credentials_path: Path to credentials file
            model_path: Path to ML model
            min_confidence: Minimum confidence threshold
            **kwargs: Additional provider-specific arguments
        """
        self.credentials_path = credentials_path
        self.model_path = model_path
        self.min_confidence = min_confidence
        self.config = kwargs

    @abstractmethod
    def extract(self, image_bytes: bytes) -> Receipt:
        """
        Extract receipt data from image.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Receipt object with extracted data

        Raises:
            Exception: If extraction fails
        """
        pass

    def preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Preprocess image before OCR (optional).

        Args:
            image_bytes: Raw image bytes

        Returns:
            Preprocessed image bytes
        """
        # TODO: Add preprocessing (resize, denoise, etc.)
        return image_bytes

    def validate_result(self, receipt: Receipt) -> bool:
        """
        Validate extraction result.

        Args:
            receipt: Extracted receipt data

        Returns:
            True if valid
        """
        return receipt.validate()
