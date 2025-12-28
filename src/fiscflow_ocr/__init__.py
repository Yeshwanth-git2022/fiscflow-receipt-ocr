"""FiscFlow Receipt OCR - A powerful, ML-enhanced receipt OCR library."""

__version__ = "0.1.0"
__author__ = "FiscFlow Team"
__email__ = "support@fiscflow.ai"

from .client import ReceiptOCR
from .models.receipt import Receipt, ReceiptItem

__all__ = [
    "ReceiptOCR",
    "Receipt",
    "ReceiptItem",
]
