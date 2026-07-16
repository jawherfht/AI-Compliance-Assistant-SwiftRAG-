import fitz
import re
import pandas as pd

CONTROL_PATTERN = r"^(\d+\.\d+[A-Za-z]?)\s+(.+)$"

def extract_controls(pdf_path):
    doc = fitz.open(pdf_path)

    controls = {}
    current_control_id = None

    for page_num in range(len(doc)):
        text = doc[page_num].get_text()

        for line in text.split("\n"):
            match = re.match(CONTROL_PATTERN, line.strip())

            if match:
                control_id = match.group(1)
                title = match.group(2).strip()

                if "...." in title:
                    continue

                if re.match(r"^[\d\.\sA-Z]+$", title) and sum(c.isdigit() for c in title) > 5:
                    continue

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

if __name__ == "__main__":
    controls = extract_controls("swift_cscf.pdf")
    pd.DataFrame(controls).to_csv(
        "swift_controls.csv",
        index=False
    )
    print("Controls extracted")