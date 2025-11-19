"""Logic for extracting equipment list rows from PDF documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pdfplumber

from .models import EquipmentItem


_FIELD_KEYWORDS: Dict[str, List[str]] = {
    "name": ["设备", "名称", "项目", "description", "item", "品名", "物料"],
    "specification": ["规格", "型号", "参数", "spec"],
    "quantity": ["数量", "qty", "数量(台)", "quantity", "amount"],
    "unit": ["单位", "unit"],
    "price": ["单价", "价格", "price"],
    "amount": ["合计", "总价", "金额", "subtotal", "total"],
}

@dataclass
class EquipmentExtractor:
    """Extract equipment rows from PDFs using simple table heuristics."""

    min_keyword_matches: int = 2

    def extract(self, pdf_path: Path | str) -> List[EquipmentItem]:
        pdf_path = Path(pdf_path)
        items: List[EquipmentItem] = []
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                for raw_table in page.extract_tables() or []:
                    table = self._normalize_table(raw_table)
                    if not table:
                        continue
                    header_index = self._find_header_row(table)
                    if header_index is None:
                        continue
                    mapping = self._map_columns(table[header_index])
                    if len(mapping) < self.min_keyword_matches:
                        continue
                    for row in table[header_index + 1 :]:
                        if self._is_termination_row(row):
                            break
                        item = self._row_to_item(
                            row=row,
                            mapping=mapping,
                            source_file=str(pdf_path.name),
                            page_number=page_number,
                        )
                        if item:
                            items.append(item)
        return items

    def _normalize_table(self, table: Iterable[Iterable[Optional[str]]]) -> List[List[str]]:
        normalized: List[List[str]] = []
        for row in table:
            normalized_row = [self._normalize_cell(cell) for cell in row]
            if any(normalized_row):
                normalized.append(normalized_row)
        return normalized

    def _normalize_cell(self, cell: Optional[str]) -> str:
        if cell is None:
            return ""
        text = str(cell).strip()
        return re.sub(r"\s+", " ", text)

    def _find_header_row(self, table: List[List[str]]) -> Optional[int]:
        best_index: Optional[int] = None
        best_score = 0
        for index, row in enumerate(table):
            score = self._header_score(row)
            if score > best_score:
                best_score = score
                best_index = index
        if best_score >= self.min_keyword_matches:
            return best_index
        return None

    def _header_score(self, row: List[str]) -> int:
        score = 0
        for cell in row:
            normalized = cell.lower().replace(" ", "")
            for keywords in _FIELD_KEYWORDS.values():
                if any(keyword in normalized for keyword in keywords):
                    score += 1
                    break
        return score

    def _map_columns(self, header_row: List[str]) -> Dict[str, int]:
        mapping: Dict[str, int] = {}
        for index, cell in enumerate(header_row):
            normalized = cell.lower().replace(" ", "")
            for field, keywords in _FIELD_KEYWORDS.items():
                if any(keyword in normalized for keyword in keywords):
                    mapping.setdefault(field, index)
                    break
        return mapping

    def _is_termination_row(self, row: List[str]) -> bool:
        text = "".join(row).strip()
        if not text:
            return True
        return bool(re.search(r"合计|总计", text))

    def _row_to_item(
        self,
        row: List[str],
        mapping: Dict[str, int],
        source_file: str,
        page_number: int,
    ) -> Optional[EquipmentItem]:
        name_idx = mapping.get("name")
        if name_idx is None or not row[name_idx].strip():
            return None
        values: Dict[str, Optional[str]] = {}
        for field, column_index in mapping.items():
            if column_index >= len(row):
                values[field] = None
            else:
                values[field] = row[column_index].strip()

        return EquipmentItem(
            name=values.get("name") or "",
            specification=values.get("specification"),
            quantity=self._parse_number(values.get("quantity")),
            unit=values.get("unit"),
            price=self._parse_number(values.get("price")),
            amount=self._parse_number(values.get("amount")),
            source_file=source_file,
            page_number=page_number,
            raw_row=row,
        )

    def _parse_number(self, value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        cleaned = re.sub(r"[^0-9,\.\-]", "", value)
        if not cleaned:
            return None
        cleaned = cleaned.replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None


__all__ = ["EquipmentExtractor"]
