"""Main ReceiptOCR client."""
from typing import Dict, List, Optional, Union
from pathlib import Path

from .extractors.base import BaseExtractor
from .extractors.vision_api import GoogleVisionExtractor
from .models.receipt import Receipt


class ReceiptOCR:
    """
    Main client for receipt OCR extraction.

    Example:
        >>> ocr = ReceiptOCR(provider='google_vision')
        >>> result = ocr.extract(image_bytes)
        >>> print(result['merchant'])
        'COSTCO WHOLESALE'
    """

    PROVIDERS = {
        'google_vision': GoogleVisionExtractor,
        # 'aws_textract': AWSTextractExtractor,  # TODO
        # 'azure': AzureExtractor,  # TODO
        # 'tesseract': TesseractExtractor,  # TODO
        # 'ml_enhanced': MLExtractor,  # TODO
    }

    def __init__(
        self,
        provider: str = 'google_vision',
        credentials_path: Optional[str] = None,
        model_path: Optional[str] = None,
        min_confidence: float = 0.5,
        feedback_enabled: bool = False,
        **kwargs
    ):
        """
        Initialize Receipt OCR client.

        Args:
            provider: OCR provider ('google_vision', 'aws_textract', etc.)
            credentials_path: Path to credentials file
            model_path: Path to ML model (if using ML provider)
            min_confidence: Minimum confidence threshold for extraction
            feedback_enabled: Enable user feedback collection
            **kwargs: Additional provider-specific arguments
        """
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Available: {list(self.PROVIDERS.keys())}"
            )

        extractor_class = self.PROVIDERS[provider]
        self.extractor: BaseExtractor = extractor_class(
            credentials_path=credentials_path,
            model_path=model_path,
            min_confidence=min_confidence,
            **kwargs
        )

        self.feedback_enabled = feedback_enabled
        self.feedback_storage = []  # TODO: Implement proper storage

    def extract(self, image: Union[bytes, Path, str]) -> Dict:
        """
        Extract structured data from receipt image.

        Args:
            image: Image as bytes, file path, or URL

        Returns:
            Dictionary with extracted receipt data:
            {
                'merchant': str,
                'total': float,
                'date': str (ISO format),
                'tax': float,
                'tip': float,
                'items': [
                    {'name': str, 'quantity': float, 'price': float},
                    ...
                ],
                'confidence': float,
                'raw_text': str
            }
        """
        # Convert to bytes if needed
        if isinstance(image, (str, Path)):
            with open(image, 'rb') as f:
                image_bytes = f.read()
        else:
            image_bytes = image

        # Extract using selected provider
        receipt = self.extractor.extract(image_bytes)

        # Convert to dict
        return receipt.to_dict()

    def extract_batch(self, images: List[Union[bytes, Path, str]]) -> List[Dict]:
        """
        Extract data from multiple receipts.

        Args:
            images: List of images

        Returns:
            List of extraction results
        """
        return [self.extract(img) for img in images]

    def submit_feedback(
        self,
        receipt_id: str,
        corrections: Dict,
        user_consent: bool = False
    ) -> bool:
        """
        Submit user corrections for model improvement.

        Args:
            receipt_id: Unique receipt identifier
            corrections: User corrections to OCR data
            user_consent: User consent to use data for training

        Returns:
            True if feedback was stored
        """
        if not self.feedback_enabled:
            return False

        if not user_consent:
            return False

        feedback_entry = {
            'receipt_id': receipt_id,
            'corrections': corrections,
            'consent': user_consent,
        }

        self.feedback_storage.append(feedback_entry)
        # TODO: Store in database/cloud storage

        return True
