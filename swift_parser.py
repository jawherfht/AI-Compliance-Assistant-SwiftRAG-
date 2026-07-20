import fitz
import re
import pandas as pd
from pathlib import Path

CONTROL_PATTERN = r"^(\d+\.\d+[A-Za-z]?)\s+(.+)$"


def _is_control_heading(line):
    """Return the control ID and title for a valid CSCF control heading."""
    match = re.match(CONTROL_PATTERN, line.strip())
    if not match:
        return None

    control_id = match.group(1)
    title = match.group(2).strip()

    # Ignore table-of-contents entries and numeric page references.
    if "...." in title:
        return None
    if re.match(r"^[\d\.\sA-Z]+$", title) and sum(c.isdigit() for c in title) > 5:
        return None

    return control_id, title


def _is_table_of_contents_page(page):
    """Detect a contents page by the presence of several control headings."""
    headings = [
        _is_control_heading(line)
        for line in page.get_text().splitlines()
    ]
    return sum(heading is not None for heading in headings) > 2


def extract_controls(pdf_path):
    doc = fitz.open(pdf_path)

    controls = {}
    current_control_id = None

    for page_num in range(len(doc)):
        if _is_table_of_contents_page(doc[page_num]):
            continue

        text = doc[page_num].get_text()

        for line in text.split("\n"):
            heading = _is_control_heading(line)

            if heading:
                control_id, title = heading

                if control_id not in controls:
                    if current_control_id:
                        controls[current_control_id]["end_page"] = page_num

                    controls[control_id] = {
                        "control_id": control_id,
                        "title": title,
                        "start_page": page_num + 1
                    }
                    current_control_id = control_id

    if current_control_id:
        controls[current_control_id]["end_page"] = len(doc)

    return list(controls.values())


def _safe_filename(control_id, title):
    """Create a Windows-safe filename while retaining the control identifier."""
    name = f"{control_id}_{title}"
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\s+", "_", name).strip("._ ")
    return name[:180] or control_id


def _repeated_margin_text(document):
    """Identify recurring top/bottom text blocks as headers or footers."""
    margin_blocks = []
    for page in document:
        page_height = page.rect.height
        for block in page.get_text("blocks", sort=True):
            y0, y1, text = block[1], block[3], block[4]
            normalized = " ".join(text.split()).casefold()
            if normalized and (y0 < page_height * 0.08 or y1 > page_height * 0.92):
                margin_blocks.append(normalized)

    return {text for text in margin_blocks if margin_blocks.count(text) > 1}


def _content_lines(page, repeated_margin_text):
    """Return page text while omitting repeated headers and footers."""
    lines = []
    for block in page.get_text("blocks", sort=True):
        normalized = " ".join(block[4].split()).casefold()
        if normalized in repeated_margin_text:
            continue
        lines.extend(block[4].splitlines())
    return lines


def generate_control_pdfs(pdf_path, controls, output_dir="generated_controls"):
    """Copy each control's original source pages into its own PDF."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated_files = []

    source_document = fitz.open(pdf_path)
    try:
        for control in controls:
            start_page = control["start_page"] - 1
            end_page = max(start_page, control["end_page"] - 1)

            control_document = fitz.open()
            try:
                control_document.insert_pdf(
                    source_document, from_page=start_page, to_page=end_page
                )
                file_path = output_path / f"{_safe_filename(control['control_id'], control['title'])}.pdf"
                control_document.save(file_path)
                generated_files.append(str(file_path))
            finally:
                control_document.close()
    finally:
        source_document.close()

    return generated_files

if __name__ == "__main__":
    controls = extract_controls("swift_cscf.pdf")
    pd.DataFrame(controls).to_csv(
        "swift_controls.csv",
        index=False
    )
    print("Controls extracted")
