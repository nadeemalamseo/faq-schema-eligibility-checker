import json
from html.parser import HTMLParser

from .models import SchemaFAQ


class JSONLDScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_jsonld = False
        self._chunks: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "script":
            return
        attrs_dict = {key.lower(): value for key, value in attrs}
        if attrs_dict.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True
            self._chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_jsonld:
            self.blocks.append("".join(self._chunks))
            self.in_jsonld = False
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self.in_jsonld:
            self._chunks.append(data)


def _as_nodes(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and isinstance(value.get("@graph"), list):
        return value["@graph"]
    return [value] if isinstance(value, dict) else []


def _is_faqpage(node: dict) -> bool:
    value = node.get("@type")
    return value == "FAQPage" or (isinstance(value, list) and "FAQPage" in value)


def extract_schema_faqs(html: str) -> tuple[list[SchemaFAQ], int, list[str]]:
    parser = JSONLDScriptParser()
    parser.feed(html)
    parser.close()

    faqs: list[SchemaFAQ] = []
    faqpage_count = 0
    errors: list[str] = []

    for index, block in enumerate(parser.blocks, start=1):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"JSON-LD block {index}: invalid JSON ({exc.msg}).")
            continue

        for node in _as_nodes(data):
            if not isinstance(node, dict) or not _is_faqpage(node):
                continue

            faqpage_count += 1
            if "mainEntity" not in node:
                errors.append(
                    f"FAQPage block {index}: mainEntity is missing."
                )
                continue

            main_entity = node.get("mainEntity")
            if isinstance(main_entity, dict):
                main_entity = [main_entity]
            if not isinstance(main_entity, list):
                errors.append(
                    f"FAQPage block {index}: mainEntity is not an array or object."
                )
                continue
            if not main_entity:
                errors.append(
                    f"FAQPage block {index}: mainEntity is empty."
                )
                continue

            for position, item in enumerate(main_entity, start=1):
                if not isinstance(item, dict):
                    errors.append(
                        f"FAQPage block {index}, item {position}: Question is not an object."
                    )
                    continue

                question = item.get("name")
                answer = item.get("acceptedAnswer", {})
                answer_text = answer.get("text") if isinstance(answer, dict) else None

                if not isinstance(question, str) or not question.strip():
                    errors.append(
                        f"FAQPage block {index}, item {position}: Question.name is missing or empty."
                    )
                    continue
                if not isinstance(answer, dict) or not isinstance(answer_text, str) or not answer_text.strip():
                    errors.append(
                        f"FAQPage block {index}, item {position}: acceptedAnswer.text is missing or empty."
                    )
                    continue

                faqs.append(SchemaFAQ(question.strip(), answer_text.strip()))

    return faqs, faqpage_count, errors
