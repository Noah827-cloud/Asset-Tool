"""Command line interface for the Asset Tool."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from .excel import ExcelWriter
from .extractor import EquipmentExtractor
from .models import EquipmentItem


def _collect_pdf_files(target: Path) -> List[Path]:
    if target.is_file() and target.suffix.lower() == ".pdf":
        return [target]
    if target.is_dir():
        return sorted(path for path in target.rglob("*.pdf") if path.is_file())
    raise FileNotFoundError(target)


def run_cli(args: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="从PDF文档中批量提取设备清单，并写入Excel模板。")
    parser.add_argument("input", help="PDF文件或包含PDF的目录")
    parser.add_argument("-o", "--output", default="设备清单汇总.xlsx", help="输出Excel文件路径")
    parser.add_argument("-t", "--template", help="Excel模版文件，可选")
    parser.add_argument("-s", "--sheet", default="设备清单", help="写入的工作表名称")
    parser.add_argument("--min-keywords", type=int, default=2, help="判定表头所需的关键字匹配数量")
    parsed = parser.parse_args(args=args)

    target = Path(parsed.input)
    pdf_files = _collect_pdf_files(target)
    if not pdf_files:
        raise SystemExit("未找到任何PDF文件")

    extractor = EquipmentExtractor(min_keyword_matches=parsed.min_keywords)
    items: List[EquipmentItem] = []
    for pdf in pdf_files:
        items.extend(extractor.extract(pdf))

    if not items:
        raise SystemExit("未能在PDF中识别出设备清单")

    writer = ExcelWriter(template=parsed.template, sheet_name=parsed.sheet)
    writer.write(items, parsed.output)
    print(f"已将 {len(items)} 条记录写入 {parsed.output}")


if __name__ == "__main__":  # pragma: no cover
    run_cli()
