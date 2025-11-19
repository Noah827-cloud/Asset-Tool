"""Domain models used by the Asset Tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EquipmentItem:
    """Represents a row extracted from an equipment list."""

    name: str
    specification: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    source_file: str = ""
    page_number: Optional[int] = None
    raw_row: List[str] = field(default_factory=list)

    def as_row(self) -> List[str]:
        """Return the item formatted as an Excel row."""

        def _fmt(value: Optional[float]) -> Optional[float]:
            return None if value is None else float(value)

        return [
            self.name,
            self.specification or "",
            _fmt(self.quantity),
            self.unit or "",
            _fmt(self.price),
            _fmt(self.amount),
            self.source_file,
            self.page_number,
            " | ".join(self.raw_row),
        ]
