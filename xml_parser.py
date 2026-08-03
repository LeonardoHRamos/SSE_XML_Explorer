"""Parser for the small subset of fields displayed by the application."""

from pathlib import Path
import xml.etree.ElementTree as ET


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_sse_xml(xml_path: str | Path) -> dict[str, str]:
    root = ET.parse(xml_path).getroot()

    def find_text(tag: str) -> str:
        for element in root.iter():
            if _local_name(element.tag) == tag and element.text:
                return element.text.strip()
        return "N/A"

    sequence = "N/A"
    for element in root.iter():
        if _local_name(element.tag) == "BodyIdent":
            sequence = element.attrib.get("number", "N/A").strip() or "N/A"
            break

    return {
        "data": find_text("DAT"),
        "hora": find_text("TIM"),
        "estacao": find_text("ABZ"),
        "operador": find_text("EKS"),
        "sequencia": sequence,
    }

