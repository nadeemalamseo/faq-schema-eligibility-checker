from html.parser import HTMLParser

from .models import VisibleFAQ
from .normalize import clean_text


class FAQHTMLParser(HTMLParser):
    """Small, dependency-free parser for common visible FAQ structures."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._stack: list[str] = []
        self._current_tag: str | None = None
        self._current_text: list[str] = []
        self._blocks: list[tuple[str, str]] = []
        self._heading: str | None = None
        self._paragraphs: list[str] = []
        self._dt: str | None = None
        self._in_script_or_style = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        self._stack.append(tag)
        if tag in {"script", "style", "noscript"}:
            self._in_script_or_style += 1
        if tag in {"h2", "h3", "h4", "dt", "dd", "p"}:
            self._current_tag = tag
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        text = clean_text(" ".join(self._current_text))

        if tag == "dt" and text:
            self._dt = text
            self._current_text = []
            self._current_tag = None
        elif tag == "dd" and text:
            if self._dt:
                self._blocks.append((self._dt, text))
            self._dt = None
            self._current_text = []
            self._current_tag = None
        elif tag in {"h2", "h3", "h4"} and text:
            self._heading = text
            self._current_text = []
            self._current_tag = None
        elif tag == "p" and text:
            self._paragraphs.append(text)
            self._current_text = []
            self._current_tag = None

        if tag in {"script", "style", "noscript"} and self._in_script_or_style:
            self._in_script_or_style -= 1

        if self._stack and self._stack[-1] == tag:
            self._stack.pop()
        elif tag in self._stack:
            self._stack.remove(tag)

    def handle_data(self, data: str) -> None:
        if self._in_script_or_style == 0 and self._current_tag:
            self._current_text.append(data)

    def visible_faqs(self) -> list[VisibleFAQ]:
        results = [VisibleFAQ(q, a) for q, a in self._blocks if q and a]

        if self._heading and self._paragraphs:
            results.append(VisibleFAQ(self._heading, self._paragraphs[-1]))

        seen: set[tuple[str, str]] = set()
        unique: list[VisibleFAQ] = []
        for item in results:
            key = (item.question.casefold(), item.answer.casefold())
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique


def extract_visible_faqs(html: str) -> list[VisibleFAQ]:
    parser = FAQHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.visible_faqs()
