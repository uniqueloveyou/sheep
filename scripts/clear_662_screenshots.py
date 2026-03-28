import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def paragraph_text(node):
    return "".join(t.text or "" for t in node.findall(".//w:t", NS)).strip()


def cell_text(tc):
    return "".join(t.text or "" for t in tc.findall(".//w:t", NS)).strip()


def clear_paragraph(p):
    for child in list(p):
        p.remove(child)
    ET.SubElement(p, f"{{{W}}}r")


def clear_cell(tc):
    paras = tc.findall("w:p", NS)
    if not paras:
        paras = [ET.SubElement(tc, f"{{{W}}}p")]
    for p in paras:
        clear_paragraph(p)


def clean_file(path):
    with zipfile.ZipFile(path, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(parts["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError(f"{path} missing body")

    children = list(body)
    start = end = None
    for idx, child in enumerate(children):
        if child.tag != f"{{{W}}}p":
            continue
        text = paragraph_text(child)
        if start is None and text.startswith("6.6.2"):
            start = idx
        elif start is not None and text.startswith("6.7"):
            end = idx
            break

    if start is None:
        raise ValueError(f"{path} missing 6.6.2")
    if end is None:
        end = len(children)

    removed_drawings = 0
    cleaned_rows = 0

    for child in children[start:end]:
        if child.tag != f"{{{W}}}tbl":
            continue

        drawings = child.findall(".//w:drawing", NS)
        removed_drawings += len(drawings)
        for drawing in drawings:
            parent_map = {c: p for p in child.iter() for c in p}
            parent = parent_map.get(drawing)
            if parent is not None:
                parent.remove(drawing)

        for row in child.findall("w:tr", NS):
            cells = row.findall("w:tc", NS)
            if not cells:
                continue
            first = cell_text(cells[0])
            if "实测截图" in first:
                for tc in cells[1:]:
                    clear_cell(tc)
                cleaned_rows += 1

    parts["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)

    return removed_drawings, cleaned_rows


def main():
    files = [
        Path(r"e:\sheep\All-Sheep\paper_662_only.docx"),
        Path(r"e:\sheep\All-Sheep\__desktop_final_verify.docx"),
    ]
    for path in files:
        removed_drawings, cleaned_rows = clean_file(path)
        print(path)
        print(f"removed_drawings={removed_drawings}, cleaned_rows={cleaned_rows}")


if __name__ == "__main__":
    main()
