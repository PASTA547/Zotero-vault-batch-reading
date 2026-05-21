from __future__ import annotations

import argparse
import json
import re
import shutil
import textwrap
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import requests


BASE_URL = "http://127.0.0.1:23119/api/users/0"
ZOTERO_PAGE_LIMIT = 100
REQUIRED_TEMPLATE_HEADINGS = [
    "## 基本信息",
    "## 一句话摘要",
    "## 研究对象",
    "## 研究方法",
    "## 数据来源",
    "## 研究结论",
    "## 我的判断",
]


def api_get(path: str, **params: Any) -> Any:
    url = f"{BASE_URL}{path}"
    response = requests.get(url, params=params or None, timeout=30)
    response.raise_for_status()
    return response.json()


def get_collection_items(collection_key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    start = 0
    while True:
        page = api_get(
            f"/collections/{collection_key}/items/top",
            format="json",
            limit=ZOTERO_PAGE_LIMIT,
            start=start,
        )
        if not page:
            break
        items.extend(page)
        if len(page) < ZOTERO_PAGE_LIMIT:
            break
        start += ZOTERO_PAGE_LIMIT
    return items


def get_children(item_key: str) -> list[dict[str, Any]]:
    return api_get(f"/items/{item_key}/children", format="json")


def get_file_url(attachment_key: str) -> str | None:
    url = f"{BASE_URL}/items/{attachment_key}/file"
    response = requests.get(url, timeout=30, allow_redirects=False)
    if response.status_code in (301, 302, 303, 307, 308):
        return response.headers.get("Location")
    if response.ok:
        text = response.text.strip()
        return text or None
    return None


def file_url_to_path(file_url: str | None) -> Path | None:
    if not file_url or not file_url.startswith("file:///"):
        return None
    parsed = urllib.parse.urlparse(file_url)
    return Path(urllib.parse.unquote(parsed.path.lstrip("/")))


def normalize_space(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("‐", "-").replace("‑", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_year(date_text: str) -> str:
    match = re.search(r"(19|20)\d{2}", date_text or "")
    return match.group(0) if match else "unknown"


def safe_stem(text: str, limit: int = 72) -> str:
    text = normalize_space(re.sub(r"<[^>]+>", "", text))
    text = re.sub(r"[^0-9A-Za-z一-鿿]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:limit].rstrip("_") or "untitled"


def note_filename(row: dict[str, Any]) -> str:
    return f"{row['year']}_{safe_stem(row['title'])}_{row['item_key']}.md"


def validate_template_contract() -> None:
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    template_paths = sorted(templates_dir.glob("*.md"))
    if not template_paths:
        raise SystemExit(f"Missing note template markdown in {templates_dir}")
    template_text = template_paths[0].read_text(encoding="utf-8", errors="ignore")
    missing = [heading for heading in REQUIRED_TEMPLATE_HEADINGS if heading not in template_text]
    if missing:
        missing_text = ", ".join(missing)
        raise SystemExit(f"Template is missing required headings: {missing_text}")


def collect_authors(creators: list[dict[str, Any]]) -> list[str]:
    authors = []
    for creator in creators:
        name = creator.get("name")
        if name:
            authors.append(normalize_space(name))
            continue
        full_name = normalize_space(f"{creator.get('firstName', '')} {creator.get('lastName', '')}")
        if full_name:
            authors.append(full_name)
    return authors


def first_nonempty(*values: str) -> str:
    for value in values:
        value = normalize_space(value or "")
        if value:
            return value
    return ""


def detect_pdf_attachment(item_key: str) -> tuple[str | None, Path | None]:
    for child in get_children(item_key):
        data = child.get("data", {})
        if data.get("itemType") != "attachment":
            continue
        if data.get("contentType") != "application/pdf":
            continue
        attachment_key = child.get("key")
        attachment_path = file_url_to_path(get_file_url(attachment_key))
        if attachment_path and attachment_path.exists():
            return attachment_key, attachment_path
    return None, None


def extract_markdown_from_pdf(pdf_path: Path, title: str) -> str:
    lines = [f"# {title}", ""]
    with fitz.open(pdf_path) as document:
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            lines.append(f"## Page {page_index + 1}")
            lines.append("")
            blocks = page.get_text("blocks")
            blocks = sorted(blocks, key=lambda block: (block[1], block[0]))
            for block in blocks:
                if len(block) < 5:
                    continue
                text = normalize_space(str(block[4]))
                if not text:
                    continue
                lines.append(text)
                lines.append("")
    return "\n".join(lines).strip() + "\n"


def stage_and_convert(item_rows: list[dict[str, Any]], output_root: Path) -> None:
    pdf_dir = output_root / "01_original_pdf"
    md_dir = output_root / "02_original_md"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    for row in item_rows:
        source_pdf = row.get("source_pdf")
        if not source_pdf:
            row["staged_pdf"] = None
            row["markdown_path"] = None
            row["status"] = "no_pdf"
            continue
        source_pdf_path = Path(source_pdf)
        staged_name = f"{row['year']}_{safe_stem(row['title'])}_{row['item_key']}.pdf"
        staged_pdf_path = pdf_dir / staged_name
        if not staged_pdf_path.exists():
            shutil.copy2(source_pdf_path, staged_pdf_path)
        markdown_name = staged_pdf_path.with_suffix(".md").name
        markdown_path = md_dir / markdown_name
        markdown_text = extract_markdown_from_pdf(staged_pdf_path, row["title"])
        markdown_path.write_text(markdown_text, encoding="utf-8")
        row["staged_pdf"] = str(staged_pdf_path)
        row["markdown_path"] = str(markdown_path)
        row["status"] = "converted"


def infer_class(title: str, abstract: str) -> str:
    """Classify paper as core compound-event research or supporting background."""
    title_text = normalize_space(title).lower()
    text = normalize_space(f"{title} {abstract}").lower()
    text = text.replace("‐", "-").replace("‑", "-").replace("–", "-")
    core_keywords = [
        "compound",
        "multiple climate-related hazards",
        "hot-and-polluted",
        "hot and polluted",
        "heat-pollution",
        "ozone pollution events",
        "compound climate extreme",
        "compound extreme heat-air pollution",
        "compound episodes",
        "compound heatwave",
    ]
    background_keywords = [
        "dataset",
        "data descriptor",
        "risk factors",
        "source sector",
        "pm2.5 concentration dataset",
        "reversal of trends",
    ]
    if any(keyword in text for keyword in core_keywords):
        return "核心复合灾害"
    if any(keyword in title_text for keyword in background_keywords):
        return "支撑背景"
    return "支撑背景"


def split_sentences(text: str) -> list[str]:
    text = normalize_space(text)
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if part.strip()]


def choose_summary_sentence(abstract: str) -> str:
    sentences = split_sentences(abstract)
    if not sentences:
        return "摘要未提供足够信息，需回查全文。"
    markers = [
        "most quantitative studies reveal",
        "we observed",
        "we found",
        "our findings",
        "results",
        "we identify",
        "this study aims to",
    ]
    for marker in markers:
        for sentence in sentences:
            if marker in sentence.lower():
                return sentence
    return sentences[0]


def infer_region(title: str, abstract: str) -> str:
    text = f"{title} {abstract}"
    mapping = [
        ("Pearl River Basin", "中国珠江流域"),
        ("China", "中国"),
        ("Europe", "欧洲"),
        ("United States", "美国"),
        ("U.S.", "美国"),
        ("Taiwan", "中国台湾"),
        ("South Asia", "南亚"),
        ("Jiangsu Province", "中国江苏省"),
        ("Northern China", "中国北方"),
        ("Middle East and North Africa", "中东和北非"),
        ("Sub-Saharan Africa", "撒哈拉以南非洲"),
        ("Indus River Valley", "印度河流域"),
        ("global", "全球"),
    ]
    for raw, zh in mapping:
        if raw.lower() in text.lower():
            return zh
    return "摘要未明确指出具体研究区，需查全文"


def infer_theme(title: str, abstract: str, paper_class: str) -> str:
    text = f"{title} {abstract}".lower()
    if "scoping review" in text or "review" in text:
        return "梳理复合气候极端事件及其健康影响的流行病学证据"
    if "population exposure" in text and "multiple climate-related hazards" in text:
        return "评估多重气候灾害叠加下的人群暴露时空格局"
    if "pm2.5" in text and "heat" in text:
        return "分析复合高温-颗粒物污染事件的空间分布、暴露或健康风险"
    if "ozone" in text and "compound" in text:
        return "评估复合热浪-臭氧事件的时空变化与健康负担"
    if paper_class == "支撑背景":
        return "提供复合灾害研究所需的背景证据、数据或方法支撑"
    return "研究复合灾害事件的暴露格局及其潜在影响"


def infer_methodology(title: str, abstract: str, markdown_text: str) -> str:
    text = normalize_space(f"{title} {abstract} {markdown_text[:5000]}").lower()
    if "scoping review" in text:
        return "采用范围综述与系统检索框架整理复合极端事件健康研究"
    if "retrospective study" in text or "retrospective analysis" in text:
        return "采用回顾性时空分析识别多灾种暴露热点与变化趋势"
    if "time-series" in text or "time series" in text:
        return "采用时间序列或相关流行病学模型评估暴露与健康结局关系"
    if "case-crossover" in text:
        return "采用病例交叉或时间序列设计识别短期健康风险"
    if "machine learning" in text:
        return "采用机器学习结合时空分析估计暴露分布"
    if "cohort study" in text:
        return "采用队列研究评估长期联合暴露与死亡风险"
    if "global assessment" in text or "assessment" in text:
        return "采用全球栅格评估与时空统计分析刻画灾害暴露格局"
    return "摘要和Markdown正文未完整说明方法细节，需结合全文补充模型设定与检验流程"


def infer_data_source(abstract: str, year: str, markdown_text: str) -> str:
    text = normalize_space(f"{abstract} {markdown_text[:5000]}").lower()
    if "web of science" in text and "scopus" in text and "medline" in text:
        return "基于 Web of Science、Scopus 和 Medline/OVID 检索文献开展范围综述"
    if "2003 to 2021" in text:
        return "基于2003-2021年全球多类气候灾害与人口暴露数据进行回顾性分析"
    if "2000-2021" in text or "2000−2021" in text:
        return "基于2000-2021年全球环境暴露与人口数据开展时空分析"
    if "1-km" in text:
        return "基于1公里尺度环境暴露与相关气象变量开展评估"
    if year != "unknown":
        return f"当前可稳定恢复到的最小信息是发表年份 {year}，完整数据来源需查全文"
    return "摘要未完整列出数据来源、时间范围和样本信息，需查全文"


def infer_core_variable(title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    if "multiple climate-related hazards" in text:
        return "多重气候灾害暴露频次、共现组合与人口暴露强度"
    if "pm2.5" in text and "heat" in text:
        return "高温与PM2.5或臭氧的复合暴露频次、持续时间与人口暴露"
    if "mortality" in text or "death burden" in text:
        return "复合暴露强度、归因风险与过早死亡负担"
    if "review" in text:
        return "复合极端事件类型、暴露表征方式与健康结局类别"
    return "复合灾害暴露指标及其对应的人群或健康风险表征"


def infer_relevance(paper_class: str, abstract: str) -> str:
    text = abstract.lower()
    if paper_class == "核心复合灾害":
        if "mortality" in text or "death burden" in text:
            return "可直接支撑复合灾害暴露向健康负担扩展的研究设计"
        if "population exposure" in text:
            return "可为复合灾害人口暴露测度、热点识别与分区比较提供参照"
        return "可为复合灾害定义、指标选择与时空格局分析提供直接参考"
    return "可作为复合灾害研究中的背景数据、方法或单因子对照证据"


def build_skim_note(row: dict[str, Any], output_root: Path) -> str:
    """Build an auto-generated SKIM note from metadata + abstract only.
    This is NOT deep reading — gaps are explicitly marked as 需查全文."""

    markdown_text = ""
    markdown_path = row.get("markdown_path")
    if markdown_path and Path(markdown_path).exists():
        markdown_text = Path(markdown_path).read_text(encoding="utf-8", errors="ignore")

    paper_class = infer_class(row["title"], row["abstract"])
    year = row["year"]
    theme = infer_theme(row["title"], row["abstract"], paper_class)
    region = infer_region(row["title"], row["abstract"])
    methodology = infer_methodology(row["title"], row["abstract"], markdown_text)
    data_source = infer_data_source(row["abstract"], year, markdown_text)
    core_variable = infer_core_variable(row["title"], row["abstract"])
    relevance = infer_relevance(paper_class, row["abstract"])
    summary_sentence = choose_summary_sentence(row["abstract"])
    findings = split_sentences(row["abstract"])[:3] or ["摘要未提供足够信息，需回查全文。"]

    findings_block = []
    for index, sentence in enumerate(findings, start=1):
        findings_block.extend(
            [
                f"- **主要发现 {index}**：{sentence}",
                f"- **原文引用 {index}**：",
                "",
                f"> {sentence}",
                "",
            ]
        )

    authors = "、".join(row["authors"]) if row["authors"] else "Not provided in source"
    pdf_path = row.get("staged_pdf") or row.get("source_pdf") or "Not provided in source"
    markdown_link = markdown_path or "Not provided in source"
    source_lines = [
        f"- Zotero 条目：{row['zotero_select']}",
        f"- DOI：{row['doi'] or 'Not provided in source'}",
        f"- PDF：{pdf_path}",
        f"- Markdown：{markdown_link}",
    ]
    if row.get("attachment_key"):
        source_lines.append(f"- PDF Attachment Key：{row['attachment_key']}")

    note = f"""---
title: "{row['title'].replace('"', "'")}"
aliases: []
tags:
  - literature-note
  - reading-note
  - {row['collection_name']}
  - {paper_class}
  - 泛读
created: "{datetime.now().date().isoformat()}"
source: "{row['zotero_select']}"
author: "{authors.replace('"', "'")}"
year: "{year}"
theme: "{theme}"
study_area: "{region}"
data_source: "{data_source}"
methodology: "{methodology}"
core_variable: "{core_variable}"
key_finding: "{summary_sentence.replace('"', "'")[:140]}"
relevance: "{relevance}"
---

# {row['title']}

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 作者 | {authors} |
| 年份 | {year} |
| 来源 | {row['publication'] or 'Not provided in source'} |
| 主题 | {theme} |
| 链接 | {row['zotero_select']} |

## 分类判断

- **条目归类**：{paper_class}
- **判断依据**：依据标题与摘要中是否直接涉及复合极端事件、复合暴露或多灾种共现。
- **阅读层级**：泛读（基于摘要与元数据自动生成，细节可能不完整）

## 一句话摘要

> 该研究聚焦{region}相关问题，{methodology}，{summary_sentence}

## 研究对象

- **研究对象**：{theme}
- **核心问题**：识别该研究如何界定复合灾害或支撑背景，并说明其空间分布、暴露或健康效应。
- **研究情境/范围**：{region}

## 研究方法

### 方法概述

- **方法类型**：{"综述" if "review" in (row["title"] + row["abstract"]).lower() else "实证 / 时空分析"}
- **总体思路**：{methodology}
- **为什么用这种方法**：用于在多灾种或复合暴露框架下识别空间热点、趋势变化或健康影响差异。

### 方法分析

- **分析单位**：摘要与Markdown正文可见的区域网格、国家/地区、时间序列或综述纳入研究。
- **关键变量/概念**：{core_variable}
- **识别/推断逻辑**：优先依据摘要和转换后的Markdown正文概述，统计识别细节不足时明确标注待查全文。
- **具体步骤**：先界定复合事件或灾害暴露，再进行时空统计、风险估计或证据综述，最后比较区域差异或健康结局。
- **泛读说明**：此笔记为自动生成的泛读版本，方法细节、核心公式、稳健性检验等信息可能缺失。若需完整方法论证，请查看精读版本或回查全文。

## 数据来源

- **数据类型**：以 Zotero 元数据、摘要和 Markdown 转换正文为主。
- **样本来源**：{region}
- **时间范围**：{data_source}
- **样本量/案例数**：摘要未完整提供时，不补造。
- **数据局限**：当前工作流未从全文逐页恢复所有表格、附录和稳健性检验细节。

## 研究结论

{chr(10).join(findings_block)}
## 我的判断

- **最有启发的点**：{relevance}
- **可借鉴的方法**：{methodology}
- **可继续追问的问题**：如果需要进入正式写作，应补齐复合事件定义、暴露阈值、统计模型与稳健性设计。
- **与我的研究关联**：{relevance}

## 原始语料

{chr(10).join(source_lines)}

## 摘要原文

> {row['abstract'] or 'Not provided in source'}
"""

    return note.rstrip() + "\n"


def write_outputs(
    item_rows: list[dict[str, Any]],
    output_root: Path,
    collection_key: str | None = None,
    collection_name: str | None = None,
) -> None:
    validate_template_contract()

    notes_dir = output_root / "03_reading_notes"
    workflow_dir = output_root / "_workflow"
    notes_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)

    if not item_rows:
        name = collection_name or "Unknown collection"
        key = collection_key or "unknown"
        overview_text = f"""# {name} 批量阅读总览

- **生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Zotero 分类**：`{name}` (`{key}`)
- **总条目数**：0
- **说明**：Zotero API 没有返回 top-level items。请确认 collection key 是否正确、分类是否为空，以及 Zotero Desktop local API 是否启用。
"""
        log_text = "# 批处理进度记录\n\n- [!] 未发现可处理条目。\n"
        (output_root / "00_collection_overview.md").write_text(overview_text, encoding="utf-8")
        (output_root / "_ProcessLog_进度记录.md").write_text(log_text, encoding="utf-8")
        (workflow_dir / "collection_items.json").write_text("[]\n", encoding="utf-8")
        return

    core_count = 0
    background_count = 0
    overview_rows = []
    log_lines = ["# 批处理进度记录", ""]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    for row in item_rows:
        note_name = note_filename(row)
        note_path = notes_dir / note_name
        note_text = build_skim_note(row, output_root)
        note_path.write_text(note_text, encoding="utf-8")
        row["note_path"] = str(note_path)
        paper_class = infer_class(row["title"], row["abstract"])
        if paper_class == "核心复合灾害":
            core_count += 1
        else:
            background_count += 1
        overview_rows.append(
            f"| {row['year']} | {paper_class} | {row['title']} | {row['doi'] or '-'} | [03](03_reading_notes/{note_path.name}) |"
        )
        log_lines.append(f"- [x] {timestamp} | 泛读生成 | {row['item_key']} | {row['title']}")

    has_deep = (output_root / "04_deep_reading_notes").exists() and list((output_root / "04_deep_reading_notes").glob("*.md"))

    deep_note = ""
    if has_deep:
        deep_note = f"\n- **精读笔记**：[04_deep_reading_notes](04_deep_reading_notes/) — Claude 全文深度精读，仅核心论文"

    overview_text = f"""# {item_rows[0]['collection_name']} 批量精读总览

- **生成时间**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Zotero 分类**：`{item_rows[0]['collection_name']}` (`{item_rows[0]['collection_key']}`)
- **总条目数**：{len(item_rows)}
- **核心复合灾害**：{core_count}
- **支撑背景**：{background_count}
- **说明**：本轮采用 Markdown-first 工作流，PDF → Markdown → 两层笔记输出：
  - **[03_reading_notes](03_reading_notes/)** — 泛读：自动生成（基于 Zotero 元数据与摘要），{len(item_rows)}篇全覆盖{deep_note}

## 条目索引

| 年份 | 归类 | 标题 | DOI | 泛读(03) |
| --- | --- | --- | --- | --- |
{chr(10).join(overview_rows)}
"""

    (output_root / "00_collection_overview.md").write_text(overview_text, encoding="utf-8")
    (output_root / "_ProcessLog_进度记录.md").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    (workflow_dir / "collection_items.json").write_text(json.dumps(item_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_rows(collection_key: str, collection_name: str) -> list[dict[str, Any]]:
    rows = []
    for item in get_collection_items(collection_key):
        data = item["data"]
        attachment_key, source_pdf = detect_pdf_attachment(item["key"])
        rows.append(
            {
                "collection_key": collection_key,
                "collection_name": collection_name,
                "item_key": item["key"],
                "title": normalize_space(re.sub(r"<[^>]+>", "", data.get("title", ""))),
                "year": parse_year(data.get("date", "")),
                "date": data.get("date", ""),
                "doi": (data.get("DOI", "") or "").strip(),
                "abstract": normalize_space(data.get("abstractNote", "") or ""),
                "authors": collect_authors(data.get("creators", [])),
                "publication": first_nonempty(
                    data.get("publicationTitle", ""),
                    data.get("proceedingsTitle", ""),
                    data.get("publisher", ""),
                    data.get("blogTitle", ""),
                ),
                "item_type": data.get("itemType", ""),
                "attachment_key": attachment_key,
                "source_pdf": str(source_pdf) if source_pdf else None,
                "zotero_select": f"zotero://select/library/items/{item['key']}",
            }
        )
    rows.sort(key=lambda row: (row["year"], row["title"].lower()))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Markdown-first Zotero collection workflow (skim notes only; deep reading is done by Claude)")
    parser.add_argument("--collection-key", required=True)
    parser.add_argument("--collection-name", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--mode", choices=["prepare", "skim", "all"], default="all",
                        help="prepare: PDF to Markdown only; skim: generate 03 skim notes; all: prepare + skim")
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    workflow_dir = output_root / "_workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    items_json = workflow_dir / "collection_items.json"

    if args.mode in {"prepare", "all"}:
        rows = collect_rows(args.collection_key, args.collection_name)
        stage_and_convert(rows, output_root)
        items_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        if not items_json.exists():
            raise SystemExit("Missing _workflow/collection_items.json. Run prepare or all first.")
        rows = json.loads(items_json.read_text(encoding="utf-8"))

    if args.mode in {"skim", "all"}:
        if not items_json.exists():
            raise SystemExit("Missing _workflow/collection_items.json. Run prepare or all first.")
        rows = json.loads(items_json.read_text(encoding="utf-8"))
        write_outputs(rows, output_root, args.collection_key, args.collection_name)

    print(f"Done. Mode={args.mode}, items={len(json.loads(items_json.read_text(encoding='utf-8'))) if items_json.exists() else 'N/A'}")
    print("Next: use the gathered research context to recommend papers for deep reading (Phase 3).")


if __name__ == "__main__":
    main()
