"""Google Vision API extractor."""
import re
import os
from typing import Dict, List, Optional
from datetime import datetime
from google.cloud import vision
from google.cloud.vision_v1 import types

from .base import BaseExtractor
from ..models.receipt import Receipt, ReceiptItem


class GoogleVisionExtractor(BaseExtractor):
    """
    Extractor using Google Cloud Vision API.

    Uses document_text_detection and structured annotations
    for high-accuracy receipt data extraction.
    """

    def __init__(self, **kwargs):
        """Initialize Google Vision API client."""
        super().__init__(**kwargs)

        # Set credentials if provided
        if self.credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path

        # Initialize Vision API client
        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Vision API: {e}")

    def extract(self, image_bytes: bytes) -> Receipt:
        """
        Extract receipt data using Vision API.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Receipt object with extracted data
        """
        # Create Vision API image object
        image = types.Image(content=image_bytes)

        # Perform OCR
        response = self.client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")

        # Extract text and parse
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""

        # Create receipt object
        receipt = Receipt(raw_text=full_text)

        # Extract structured data
        receipt.merchant_name = self._extract_merchant(full_text)
        receipt.receipt_date = self._extract_date(full_text)
        receipt.receipt_total = self._extract_total(full_text)
        receipt.tax_amount = self._extract_tax(full_text)

        # Extract items using structured annotations
        items = self._extract_items_from_annotations(response, receipt.receipt_total)
        for item_dict in items:
            receipt.add_item(ReceiptItem(**item_dict))

        return receipt

    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from top lines."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not lines:
            return None

        # First non-empty line is usually merchant
        ignore_patterns = [
            r'receipt', r'invoice', r'bill', r'^\d+$', r'^tel:', r'^www\.'
        ]

        for line in lines[:5]:
            should_ignore = any(re.search(p, line.lower()) for p in ignore_patterns)
            if not should_ignore and len(line) > 3:
                return re.sub(r'[^a-zA-Z0-9\s\-&\.]', '', line).strip()

        return None

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from receipt text."""
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                date_formats = [
                    '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d', '%Y-%m-%d',
                    '%m/%d/%y', '%m-%d-%y',
                ]

                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

        return None

    def _extract_total(self, text: str) -> Optional[float]:
        """Extract total amount from receipt."""
        lines = text.split('\n')
        total_patterns = [
            r'total[:\s]+\$?\s*(\d+\.\d{2})',
            r'amount[:\s]+\$?\s*(\d+\.\d{2})',
        ]

        for line in reversed(lines):
            for pattern in total_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue

        return None

    def _extract_tax(self, text: str) -> Optional[float]:
        """Extract tax amount from receipt."""
        lines = text.split('\n')
        tax_patterns = [
            r'tax[:\s]+\$?\s*(\d+\.\d{2})',
            r'vat[:\s]+\$?\s*(\d+\.\d{2})',
        ]

        for line in reversed(lines):
            for pattern in tax_patterns:
                match = re.search(pattern, line.lower())
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue

        return None

    def _extract_items_from_annotations(
        self,
        vision_response,
        receipt_total: Optional[float]
    ) -> List[Dict]:
        """
        Extract line items using Vision API structured annotations.

        This is the core multi-line extraction logic that handles
        Costco and other store formats.
        """
        if not vision_response or not vision_response.full_text_annotation:
            return []

        items = []
        pages = vision_response.full_text_annotation.pages
        if not pages:
            return []

        # Group words by line using Y coordinates
        lines_data = self._group_words_by_line(pages)

        # Extract items with deduplication
        skip_keywords = [
            'subtotal', 'total', 'tax', 'change', 'cash', 'credit', 'debit',
            'visa', 'mastercard', 'thank you', 'receipt', 'date', 'time',
            'approved', 'customer', 'member', 'number', 'reference', 'invoice',
        ]

        used_item_names = set()
        used_line_indices = set()

        for idx, line_words in enumerate(lines_data):
            if not line_words:
                continue

            line_text = ' '.join([w['text'] for w in line_words])
            line_lower = line_text.lower()

            # Skip non-item lines
            if any(keyword in line_lower for keyword in skip_keywords):
                continue

            # Look for price pattern
            price_word = None
            item_words = []

            for i, word_data in enumerate(line_words):
                word = word_data['text']
                price_match = re.match(r'^\$?(\d+\.\d{2})$', word)
                if price_match:
                    price_word = float(price_match.group(1))
                    item_words = [w['text'] for w in line_words[:i]]
                    break

            # Multi-line: If price found but no item words, look back
            if price_word and not item_words and idx > 0:
                # Filter out high prices (likely totals)
                if price_word > 50:
                    continue

                # Look back for item name
                for lookback in range(1, min(11, idx + 1)):
                    prev_idx = idx - lookback

                    if prev_idx in used_line_indices:
                        continue

                    prev_line_words = lines_data[prev_idx]
                    prev_line_text = ' '.join([w['text'] for w in prev_line_words])
                    prev_line_lower = prev_line_text.lower()

                    if any(keyword in prev_line_lower for keyword in skip_keywords):
                        continue

                    if prev_line_text.replace(' ', '').isdigit():
                        continue

                    if len(prev_line_text) < 3:
                        continue

                    if prev_line_text.upper() in used_item_names:
                        continue

                    if any(c.isalpha() for c in prev_line_text):
                        item_words = [w['text'] for w in prev_line_words]
                        used_line_indices.add(prev_idx)
                        break

            # Create item if we have both price and name
            if price_word and item_words:
                item_name = ' '.join(item_words).strip()

                if len(item_name) > 2 and not item_name.isdigit():
                    # Check for quantity pattern
                    qty_match = re.match(r'^(\d+\.?\d*)\s*x?\s*(.+)$', item_name, re.IGNORECASE)
                    if qty_match:
                        quantity = float(qty_match.group(1))
                        item_name = qty_match.group(2).strip()
                        unit_price = round(price_word / quantity, 2) if quantity > 0 else price_word
                    else:
                        quantity = 1.0
                        unit_price = price_word

                    used_item_names.add(item_name.upper())

                    items.append({
                        'name': item_name,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': price_word,
                        'confidence': 0.8  # TODO: Calculate actual confidence
                    })

        return items

    def _group_words_by_line(self, pages) -> List[List[Dict]]:
        """Group words by their vertical position (Y coordinate)."""
        lines_data = []

        for page in pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    words_in_para = []

                    for word in paragraph.words:
                        vertices = word.bounding_box.vertices
                        if vertices:
                            y_coords = [v.y for v in vertices]
                            x_coords = [v.x for v in vertices]
                            avg_y = sum(y_coords) / len(y_coords)
                            avg_x = sum(x_coords) / len(x_coords)

                            word_text = ''.join([symbol.text for symbol in word.symbols])

                            words_in_para.append({
                                'text': word_text,
                                'y': avg_y,
                                'x': avg_x,
                                'confidence': word.confidence
                            })

                    if words_in_para:
                        words_in_para.sort(key=lambda w: w['y'])

                        current_line = []
                        current_y = words_in_para[0]['y']

                        for word_data in words_in_para:
                            if abs(word_data['y'] - current_y) < 15:
                                current_line.append(word_data)
                            else:
                                if current_line:
                                    lines_data.append(sorted(current_line, key=lambda w: w['x']))
                                current_line = [word_data]
                                current_y = word_data['y']

                        if current_line:
                            lines_data.append(sorted(current_line, key=lambda w: w['x']))

        return lines_data
