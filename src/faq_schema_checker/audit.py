from .jsonld import extract_schema_faqs
from .models import AuditReport, Finding, SchemaFAQ, VisibleFAQ
from .normalize import normalize_text


def _contains_pair(visible: VisibleFAQ, schema: SchemaFAQ) -> bool:
    return (
        normalize_text(visible.question) == normalize_text(schema.question)
        and normalize_text(visible.answer) == normalize_text(schema.answer)
    )


def audit_html(html: str) -> AuditReport:
    from .html_parser import extract_visible_faqs

    visible = extract_visible_faqs(html)
    schema, faqpage_count, jsonld_errors = extract_schema_faqs(html)
    findings: list[Finding] = []

    if faqpage_count == 0:
        findings.append(
            Finding(
                "NO_FAQPAGE",
                "warning",
                "No FAQPage JSON-LD implementation was detected.",
                "No @type=FAQPage node was found in application/ld+json.",
                "If this page intentionally uses FAQPage structured data, add one implementation that accurately represents the visible FAQ content.",
            )
        )
    elif faqpage_count > 1:
        findings.append(
            Finding(
                "DUPLICATE_FAQPAGE",
                "error",
                "Multiple FAQPage JSON-LD implementations were detected.",
                f"{faqpage_count} FAQPage nodes were found.",
                "Keep one authoritative FAQPage implementation and remove conflicting duplicates.",
            )
        )

    if not visible:
        findings.append(
            Finding(
                "NO_VISIBLE_FAQ",
                "error",
                "No supported visible FAQ pattern was detected.",
                "The parser found no question/answer pairs in headings/paragraphs or definition lists.",
                "Make sure the FAQ content is visible in the HTML and uses a supported structure.",
            )
        )

    for error in jsonld_errors:
        findings.append(
            Finding(
                "INVALID_JSONLD",
                "error",
                "A JSON-LD implementation contains a structural problem.",
                error,
                "Fix the JSON-LD syntax or the affected FAQPage Question/Answer structure.",
            )
        )

    if visible and schema:
        unmatched_schema = [
            item for item in schema if not any(_contains_pair(v, item) for v in visible)
        ]
        unmatched_visible = [
            item for item in visible if not any(_contains_pair(item, s) for s in schema)
        ]

        if unmatched_schema:
            findings.append(
                Finding(
                    "SCHEMA_VISIBLE_MISMATCH",
                    "error",
                    "Some FAQPage questions or answers do not match the detected visible FAQ content.",
                    f"{len(unmatched_schema)} structured-data item(s) had no exact visible-content match.",
                    "Update the structured data so its Question.name and Answer.text accurately represent visible FAQ content.",
                )
            )

        if unmatched_visible:
            findings.append(
                Finding(
                    "VISIBLE_NOT_MARKED_UP",
                    "warning",
                    "Some detected visible FAQ pairs are not represented in FAQPage JSON-LD.",
                    f"{len(unmatched_visible)} visible FAQ pair(s) had no exact structured-data match.",
                    "If those questions are intended to be part of the FAQPage implementation, add matching Question/Answer entries.",
                )
            )

    if schema and not visible:
        findings.append(
            Finding(
                "SCHEMA_WITHOUT_VISIBLE_FAQ",
                "error",
                "FAQPage structured data was found without detectable visible FAQ content.",
                f"{len(schema)} structured-data FAQ item(s) were detected.",
                "Do not use structured data to describe content that users cannot see on the page.",
            )
        )

    if not findings:
        findings.append(
            Finding(
                "AUDIT_PASS",
                "info",
                "The detected FAQPage implementation matches the supported visible FAQ content.",
                f"{len(schema)} FAQ item(s) matched the detected visible content.",
                "Keep the visible FAQ and structured data synchronized when content changes.",
            )
        )

    errors = sum(1 for f in findings if f.severity == "error")
    warnings = sum(1 for f in findings if f.severity == "warning")
    status = "FAIL" if errors else "REVIEW" if warnings else "PASS"

    return AuditReport(
        status=status,
        summary=f"{errors} error(s), {warnings} warning(s), {len(schema)} schema FAQ item(s), {len(visible)} visible FAQ item(s).",
        visible_faqs=visible,
        schema_faqs=schema,
        findings=findings,
    )
