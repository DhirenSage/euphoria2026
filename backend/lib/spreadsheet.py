import csv
import re
from io import BytesIO, StringIO
from pathlib import PurePosixPath
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


MAX_ROWS = 500
MAX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024


def _normalise_header(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.strip().lower())).strip("_")


def _records(rows: list[list[str]]) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("The uploaded file is empty.")
    headers = [_normalise_header(value) for value in rows[0]]
    if not any(headers):
        raise ValueError("The first row must contain column names.")
    records: list[dict[str, str]] = []
    for values in rows[1:]:
        if not any(str(value).strip() for value in values):
            continue
        records.append({header: str(values[index]).strip() if index < len(values) else "" for index, header in enumerate(headers) if header})
        if len(records) > MAX_ROWS:
            raise ValueError(f"A maximum of {MAX_ROWS} participant rows can be imported at once.")
    if not records:
        raise ValueError("No participant rows were found below the header row.")
    return records


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference.upper())
    if not letters:
        return 0
    result = 0
    for character in letters.group(0):
        result = result * 26 + ord(character) - 64
    return result - 1


def _xlsx_rows(content: bytes) -> list[list[str]]:
    try:
        with ZipFile(BytesIO(content)) as archive:
            if sum(item.file_size for item in archive.infolist()) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("The expanded Excel file is too large.")
            shared: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
                shared = ["".join(node.text or "" for node in item.iter() if node.tag.endswith("}t")) for item in root]

            worksheet = "xl/worksheets/sheet1.xml"
            if "xl/workbook.xml" in archive.namelist() and "xl/_rels/workbook.xml.rels" in archive.namelist():
                workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
                first_sheet = next((node for node in workbook.iter() if node.tag.endswith("}sheet")), None)
                relation_id = next((value for key, value in (first_sheet.attrib.items() if first_sheet is not None else []) if key.endswith("}id")), "")
                relations = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
                target = next((node.attrib.get("Target", "") for node in relations if node.attrib.get("Id") == relation_id), "")
                if target:
                    worksheet = str(PurePosixPath("xl") / target.lstrip("/")) if not target.startswith("xl/") else target
            if worksheet not in archive.namelist():
                raise ValueError("The first Excel worksheet could not be read.")

            root = ElementTree.fromstring(archive.read(worksheet))
            rows: list[list[str]] = []
            for row_node in (node for node in root.iter() if node.tag.endswith("}row")):
                values: dict[int, str] = {}
                for cell in (node for node in row_node if node.tag.endswith("}c")):
                    index = _column_index(cell.attrib.get("r", "A1"))
                    cell_type = cell.attrib.get("t", "")
                    value_node = next((node for node in cell.iter() if node.tag.endswith("}v")), None)
                    if cell_type == "inlineStr":
                        value = "".join(node.text or "" for node in cell.iter() if node.tag.endswith("}t"))
                    else:
                        value = value_node.text if value_node is not None and value_node.text is not None else ""
                        if cell_type == "s" and value.isdigit() and int(value) < len(shared):
                            value = shared[int(value)]
                    values[index] = value
                width = max(values.keys(), default=-1) + 1
                rows.append([values.get(index, "") for index in range(width)])
            return rows
    except (BadZipFile, ElementTree.ParseError, KeyError) as exc:
        raise ValueError("The Excel file is invalid or damaged.") from exc


def parse_spreadsheet(filename: str, content: bytes) -> list[dict[str, str]]:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension == "csv":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("CSV files must use UTF-8 encoding.") from exc
        return _records(list(csv.reader(StringIO(text))))
    if extension == "xlsx":
        return _records(_xlsx_rows(content))
    raise ValueError("Upload a CSV or Excel .xlsx file.")