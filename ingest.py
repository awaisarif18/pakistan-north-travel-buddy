"""Extract a PDF locally, or index saved chunks with --embed."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pymupdf

ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "pakistan-north-tours-final.pdf"
MIN_CHARS = 1600
MAX_CHARS = 2800
OVERLAP_CHARS = 320


def clean_text(text):
    return re.sub(r"\s+", " ", text.replace("\u00ad", "")).strip()


def extract_pages(pdf_path):
    pages = []
    with pymupdf.open(pdf_path) as document:
        for number, page in enumerate(document, 1):
            pages.append({"page": number, "paragraphs": extract_paragraphs(page)})
    return pages


def extract_paragraphs(page):
    blocks = [block for block in page.get_text("dict", sort=True)["blocks"] if block["type"] == 0]
    sizes = Counter()
    for block in blocks:
        for line in block["lines"]:
            for span in line["spans"]:
                sizes[round(span["size"], 1)] += len(span["text"])
    body_size = sizes.most_common(1)[0][0] if sizes else 0
    tables = page.find_tables().tables
    items = []
    for table in tables:
        rows = [" | ".join(clean_text(cell or "") for cell in row) for row in table.extract()]
        items.append((table.bbox, "\n".join(rows), False))
    for block in blocks:
        rect = pymupdf.Rect(block["bbox"])
        if any(pymupdf.Rect(table.bbox).contains(rect.tl + (rect.br - rect.tl) / 2) for table in tables):
            continue
        spans = [span for line in block["lines"] for span in line["spans"]]
        text = clean_text("\n".join("".join(span["text"] for span in line["spans"]) for line in block["lines"]))
        if text:
            heading = max(span["size"] for span in spans) > body_size + 0.5 and len(text) < 250
            items.append((block["bbox"], text, heading))
    paragraphs, previous = [], None
    for bbox, text, heading in sorted(items, key=lambda item: (item[0][1], item[0][0])):
        if (previous and heading == paragraphs[-1]["heading"]
                and abs(bbox[0] - previous[0]) < 3
                and 0 <= bbox[1] - previous[3] < body_size * 0.65):
            paragraphs[-1]["text"] += " " + text
        else:
            paragraphs.append({"text": text, "heading": heading})
        previous = bbox
    return paragraphs


def paragraph_units(pages):
    # Attach headings to the next paragraph so a chunk cannot end on a heading.
    pending = []
    for page in pages:
        for paragraph in page["paragraphs"]:
            unit = {**paragraph, "page_start": page["page"], "page_end": page["page"]}
            if unit["heading"]:
                pending.append(unit)
                continue
            if pending:
                unit["text"] = "\n\n".join(item["text"] for item in pending) + "\n\n" + unit["text"]
                unit["page_start"] = pending[0]["page_start"]
                unit["heading"] = True
                pending = []
            yield unit
    yield from pending


def split_unit(unit):
    text = unit["text"]
    while len(text) > MAX_CHARS:
        cut = text.rfind(" ", 0, MAX_CHARS)
        if cut <= 0:
            cut = MAX_CHARS
        yield {**unit, "text": text[:cut]}
        text = text[cut:].lstrip()
    if text:
        yield {**unit, "text": text}


def make_chunk(units, source):
    text = "\n\n".join(unit["text"] for unit in units)
    start = min(unit["page_start"] for unit in units)
    end = max(unit["page_end"] for unit in units)
    digest = hashlib.sha256(f"{source}:{start}:{end}:{text}".encode()).hexdigest()[:12]
    return {
        "id": f"p{start:03d}-{end:03d}-{digest}",
        "text": text,
        "estimated_tokens": (len(text) + 3) // 4,
        "metadata": {"source": source, "page_start": start, "page_end": end},
    }


def chunk_pages(pages, source):
    chunks, current = [], []
    for paragraph in paragraph_units(pages):
        for unit in split_unit(paragraph):
            length = sum(len(item["text"]) + 2 for item in current)
            new_section = unit["heading"] and length >= MIN_CHARS
            if current and (new_section or length + len(unit["text"]) > MAX_CHARS):
                chunks.append(make_chunk(current, source))
                # Overlap within a section; start fresh when a new section begins.
                previous = current[-1]
                tail = previous["text"][-OVERLAP_CHARS:]
                tail = tail.split(" ", 1)[-1]
                current = [] if new_section else [{**previous, "text": tail}]
                if sum(len(item["text"]) + 2 for item in current) + len(unit["text"]) > MAX_CHARS:
                    current = []
            current.append(unit)
    if current:
        chunks.append(make_chunk(current, source))
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--embed", action="store_true", help="Index the reviewed data/chunks.json; reuse saved vectors.")
    args = parser.parse_args()
    if args.embed:
        if args.pdf != PDF_PATH or args.output_dir != ROOT / "data":
            parser.error("--embed uses the reviewed data/chunks.json; omit --pdf and --output-dir.")
        from google.genai import errors
        from rag import build_index
        try:
            build_index()
        except errors.APIError as error:
            parser.exit(1, f"Gemini API error {error.code}. Check model access, API key, or quota. "
                        "Completed vectors are saved; rerun to resume.\n")
        except ValueError as error:
            parser.exit(1, f"{error}\n")
        return
    if not args.pdf.is_file():
        parser.error(f"PDF not found: {args.pdf}")
    pages = extract_pages(args.pdf)
    empty = [page["page"] for page in pages if not page["paragraphs"]]
    if empty:
        parser.exit(1, f"No text on pages {empty}. Review extraction before continuing.\n")
    chunks = chunk_pages(pages, args.pdf.name)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, data in (("pages.json", pages), ("chunks.json", chunks)):
        (args.output_dir / filename).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    estimates = [chunk["estimated_tokens"] for chunk in chunks]
    print(f"Pages extracted: {len(pages)}")
    print(f"Chunks generated: {len(chunks)}")
    print(f"Estimated tokens per chunk: {min(estimates)}-{max(estimates)}, median {sorted(estimates)[len(estimates) // 2]}")
    print("Token counts use a local 4-characters-per-token estimate, not the Gemini tokenizer.")
    print("Extraction failures: 0")
    print("Embedding API calls: 0; vectors stored: 0")
    print(f"Review files: {args.output_dir / 'pages.json'} and {args.output_dir / 'chunks.json'}")


if __name__ == "__main__":
    main()
