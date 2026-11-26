from html.parser import HTMLParser

from .models import VisibleFAQ
from .normalize import clean_text


class FAQHTMLParser(HTMLParser):
    """Dependency-free extractor for common server-rendered FAQ patterns."""

    QUESTION_TAGS = {"h2", "h3", "h4", "dt"}
    ANSWER_TAGS = {"dd", "p"}
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture_tag: str | None = None
        self._capture_depth = 0
        self._capture_text: list[str] = []
        self._pairs: list[tuple[str, str]] = []
        self._pending_question: str | None = None
        self._summary_depth = 0
        self._summary_text: list[str] = []
        self._ignored_depth = 0
        self._ignored_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template"}:
            self._ignored_depth += 1
            self._ignored_tags.append(tag)
            return
        if self._ignored_depth:
            return

        if tag == "summary" and self._capture_tag is None:
            self._summary_depth = 1
            self._summary_text = []
            return
        if self._summary_depth:
            if tag not in self.VOID_TAGS:
                self._summary_depth += 1
            return

        if self._capture_tag is not None:
            if tag not in self.VOID_TAGS:
                self._capture_depth += 1
            return
        if tag in self.QUESTION_TAGS | self.ANSWER_TAGS:
            self._capture_tag = tag
            self._capture_depth = 1
            self._capture_text = []

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._ignored_depth:
            if self._ignored_tags and tag == self._ignored_tags[-1]:
                self._ignored_tags.pop()
                self._ignored_depth -= 1
            return

        if self._summary_depth:
            self._summary_depth -= 1
            if self._summary_depth == 0:
                question = clean_text(" ".join(self._summary_text))
                if question:
                    self._pending_question = question
                self._summary_text = []
            return

        if self._capture_tag is None:
            return
        self._capture_depth -= 1
        if self._capture_depth <= 0:
            captured_tag = self._capture_tag
            value = clean_text(" ".join(self._capture_text))
            self._capture_tag = None
            self._capture_depth = 0
            self._capture_text = []
            if value:
                if captured_tag in self.QUESTION_TAGS:
                    self._pending_question = value
                elif self._pending_question:
                    self._pairs.append((self._pending_question, value))
                    self._pending_question = None

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._summary_depth:
            self._summary_text.append(data)
        elif self._capture_tag is not None:
            self._capture_text.append(data)

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
