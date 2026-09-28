from dataclasses import asdict, dataclass
from typing import Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    message: str
    evidence: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class VisibleFAQ:
    question: str
    answer: str


@dataclass(frozen=True)
class SchemaFAQ:
    question: str
    answer: str


@dataclass
class AuditReport:
    status: str
    summary: str
    visible_faqs: list[VisibleFAQ]
    schema_faqs: list[SchemaFAQ]
    findings: list[Finding]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "summary": self.summary,
            "visible_faqs": [
                {"question": item.question, "answer": item.answer}
                for item in self.visible_faqs
            ],
            "schema_faqs": [
                {"question": item.question, "answer": item.answer}
                for item in self.schema_faqs
            ],
            "findings": [item.to_dict() for item in self.findings],
        }
