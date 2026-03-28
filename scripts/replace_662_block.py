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


def find_section_bounds(body):
    children = list(body)
    start_662 = None
    start_67 = None

    for idx, child in enumerate(children):
        if child.tag != f"{{{W}}}p":
            continue
        text = paragraph_text(child)
        if start_662 is None and text.startswith("6.6.2"):
            start_662 = idx
        elif start_662 is not None and text.startswith("6.7"):
            start_67 = idx
            break

    if start_662 is None or start_67 is None or start_67 <= start_662:
        raise ValueError("未找到 6.6.2 或 6.7 的有效边界")

    return start_662, start_67


def load_docx_parts(path):
    with zipfile.ZipFile(path, "r") as zin:
        parts = {name: zin.read(name) for name in zin.namelist()}
    root = ET.fromstring(parts["word/document.xml"])
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("文档缺少 body 节点")
    return parts, root, body


def save_docx(path, parts):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in parts.items():
            zout.writestr(name, data)


def main():
    source_path = Path(r"e:\sheep\All-Sheep\__paper_fixed_662.docx")
    target_path = Path(r"e:\sheep\All-Sheep\__desktop_check.docx")
    backup_path = Path(r"e:\sheep\All-Sheep\__desktop_check_before_replace_662.docx")

    shutil.copyfile(target_path, backup_path)

    source_parts, source_root, source_body = load_docx_parts(source_path)
    target_parts, target_root, target_body = load_docx_parts(target_path)

    source_start, source_end = find_section_bounds(source_body)
    target_start, target_end = find_section_bounds(target_body)

    source_children = list(source_body)
    target_children = list(target_body)
    replacement_nodes = [copy.deepcopy(node) for node in source_children[source_start:source_end]]

    for node in target_children[target_start:target_end]:
        target_body.remove(node)

    insert_at = target_start
    for node in replacement_nodes:
        target_body.insert(insert_at, node)
        insert_at += 1

    target_parts["word/document.xml"] = ET.tostring(
        target_root, encoding="utf-8", xml_declaration=True
    )
    save_docx(target_path, target_parts)

    print(target_path)
    print(backup_path)


if __name__ == "__main__":
    main()
