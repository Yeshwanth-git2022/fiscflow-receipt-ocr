"""Receipt data models."""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class ReceiptItem:
    """Single line item from a receipt."""
    name: str
    quantity: float = 1.0
    unit_price: float = 0.0
    total_price: float = 0.0
    confidence: float = 1.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Receipt:
    """Complete receipt data structure."""
    merchant_name: Optional[str] = None
    receipt_total: Optional[float] = None
    receipt_date: Optional[datetime] = None
    tax_amount: Optional[float] = None
    tip_amount: Optional[float] = None
    items: List[ReceiptItem] = field(default_factory=list)
    currency: str = 'USD'
    confidence: float = 1.0
    raw_text: str = ''
    receipt_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime to ISO string
        if self.receipt_date:
            data['receipt_date'] = self.receipt_date.isoformat()
        return data

    def add_item(self, item: ReceiptItem):
        """Add item to receipt."""
        self.items.append(item)

    @property
    def items_total(self) -> float:
        """Calculate total from items."""
        return sum(item.total_price for item in self.items)

    def validate(self) -> bool:
        """Validate receipt data consistency."""
        if not self.merchant_name:
            return False

        if self.receipt_total and self.items:
            # Check if items total matches receipt total (within 10%)
            diff = abs(self.items_total - self.receipt_total)
            if diff > self.receipt_total * 0.1:
                return False

        return True
