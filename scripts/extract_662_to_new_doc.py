import copy
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def paragraph_text(node):
    return "".join(t.text or "" for t in node.findall(".//w:t", NS)).strip()


def find_662_bounds(children):
    start = None
    end = None
    for idx, child in enumerate(children):
        if child.tag != f"{{{W}}}p":
            continue
        text = paragraph_text(child)
        if start is None and text.startswith("6.6.2"):
            start = idx
            continue
        if start is not None and text.startswith("6.7"):
            end = idx
            break
    if start is None or end is None or end <= start:
        raise ValueError("Failed to locate 6.6.2 section boundaries")
    return start, end


def main():
    src = Path(r"e:\sheep\All-Sheep\__desktop_final_verify.docx")
    out = Path(r"e:\sheep\All-Sheep\paper_662_only.docx")

    shutil.copyfile(src, out)

    with zipfile.ZipFile(out, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(parts["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("Missing body in document.xml")

    children = list(body)
    start, end = find_662_bounds(children)

    sect_pr = copy.deepcopy(children[-1]) if children and children[-1].tag == f"{{{W}}}sectPr" else None
    keep_nodes = [copy.deepcopy(node) for node in children[start:end]]

    for child in list(body):
        body.remove(child)

    for node in keep_nodes:
        body.append(node)
    if sect_pr is not None:
        body.append(sect_pr)

    parts["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)

    print(out)


if __name__ == "__main__":
    main()
