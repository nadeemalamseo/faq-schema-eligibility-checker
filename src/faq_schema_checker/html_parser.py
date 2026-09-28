from html.parser import HTMLParser

from .models import VisibleFAQ
from .normalize import clean_text


class FAQHTMLParser(HTMLParser):
    """Dependency-free parser for common visible FAQ structures."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._current_tag: str | None = None
        self._current_text: list[str] = []
        self._pairs: list[tuple[str, str]] = []
        self._pending_question: str | None = None
        self._dt: str | None = None
        self._in_script_or_style = 0
        self._in_summary = False
        self._summary_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._in_script_or_style += 1
            return

        if tag == "summary":
            self._in_summary = True
            self._summary_text = []
        elif tag in {"h2", "h3", "h4", "dt", "dd", "p"}:
            self._current_tag = tag
            self._current_text = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag in {"script", "style", "noscript"}:
            if self._in_script_or_style:
                self._in_script_or_style -= 1
            return

        if tag == "summary" and self._in_summary:
            question = clean_text(" ".join(self._summary_text))
            if question:
                self._pending_question = question
            self._in_summary = False
            self._summary_text = []
            return

        if tag not in {"h2", "h3", "h4", "dt", "dd", "p"}:
            return

        text = clean_text(" ".join(self._current_text))
        self._current_text = []
        self._current_tag = None

        if not text:
            return

        if tag in {"h2", "h3", "h4", "dt"}:
            self._pending_question = text
        elif tag in {"dd", "p"} and self._pending_question:
            self._pairs.append((self._pending_question, text))
            self._pending_question = None

    def handle_data(self, data: str) -> None:
        if self._in_script_or_style:
            return
        if self._in_summary:
            self._summary_text.append(data)
        elif self._current_tag:
            self._current_text.append(data)

    def visible_faqs(self) -> list[VisibleFAQ]:
        seen: set[tuple[str, str]] = set()
        unique: list[VisibleFAQ] = []
        for question, answer in self._pairs:
            item = VisibleFAQ(question, answer)
            key = (question.casefold(), answer.casefold())
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique


def extract_visible_faqs(html: str) -> list[VisibleFAQ]:
    parser = FAQHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.visible_faqs()
