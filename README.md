# Asset-Tool

一个用于**从PDF文档中智能识别设备清单并写入Excel模版**的命令行工具。

## 功能特性

- 批量遍历单个文件或目录中的所有 PDF。
- 使用 `pdfplumber` 自动定位表头并抽取“名称、规格、数量、单价、金额”等字段。
- 自动将识别结果写入指定的 Excel 模版（若未提供模版则创建默认表头）。
- 在 Excel 中保留来源文件名、页码以及原始行，便于人工复核。

## 安装依赖

在受限网络中 `pip install -r requirements.txt` 可能会提示 *Cannot connect to
proxy*。可以按以下方式解决：

1. **配置可访问的 PyPI 镜像或代理**：仓库内提供了
   [`pip.conf.example`](pip.conf.example) 和 `scripts/setup_pip_mirror.sh`。执行
   `scripts/setup_pip_mirror.sh` 会把示例配置复制到 `~/.config/pip/pip.conf`
  （或 `$PIP_CONFIG_DIR/pip.conf`），随后根据实际网络修改 `index-url`、
   `trusted-host`、`proxy` 等字段。
2. **完全离线安装**：在有网络的机器上下载 `requirements.txt` 中列出的
   wheel 包并拷贝到 `vendor/wheels`，然后运行

   ```bash
   pip install --no-index --find-links vendor/wheels -r requirements.txt
   ```

准备好网络配置后即可安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python -m asset_tool.cli <PDF路径或目录> \
    --output 结果.xlsx \
    --template 模版.xlsx \
    --sheet 设备清单 \
    --min-keywords 2
```

参数说明：

| 参数 | 说明 |
| ---- | ---- |
| `input` | 必填，单个 PDF 文件或包含多个 PDF 的目录 |
| `-o/--output` | 输出 Excel 文件路径，默认 `设备清单汇总.xlsx` |
| `-t/--template` | 可选的 Excel 模版路径。若省略，程序会生成带默认表头的新文件 |
| `-s/--sheet` | 写入的工作表名称，默认 `设备清单` |
| `--min-keywords` | 识别表头所需的关键字匹配数量，默认 2 |

## 工作流程

1. `asset_tool.extractor.EquipmentExtractor` 逐页读取 PDF，使用关键字匹配判定设备清单表格的表头与列映射。
2. 将每行数据解析为 `asset_tool.models.EquipmentItem`，并记录来源文件及页码。
3. `asset_tool.excel.ExcelWriter` 将结果写入 Excel：若提供模版则复用模版样式，否则创建带默认表头的新表。

## 注意事项

- PDF 中的设备表格需为标准表格（可被 `pdfplumber` 识别），若是扫描件建议先进行 OCR 识别。
- 由于不同文档的列名差异较大，必要时可以调整 `asset_tool/extractor.py` 中 `_FIELD_KEYWORDS` 的关键字列表以提升识别率。
