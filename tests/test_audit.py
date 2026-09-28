from pathlib import Path

from faq_schema_checker.audit import audit_html

ROOT = Path(__file__).resolve().parents[1]


def read_example(name: str) -> str:
    return (ROOT / "examples" / name).read_text(encoding="utf-8")


def test_valid_faq_passes():
    report = audit_html(read_example("valid-faq.html"))
    assert report.status == "PASS"
    assert any(f.code == "AUDIT_PASS" for f in report.findings)


def test_mismatch_fails():
    report = audit_html(read_example("mismatched-faq.html"))
    assert report.status == "FAIL"
    assert any(f.code == "SCHEMA_VISIBLE_MISMATCH" for f in report.findings)


def test_duplicate_faq_fails():
    report = audit_html(read_example("duplicate-faq.html"))
    assert report.status == "FAIL"
    assert any(f.code == "DUPLICATE_FAQPAGE" for f in report.findings)


def test_invalid_faq_fails():
    report = audit_html(read_example("invalid-faq.html"))
    assert report.status == "FAIL"
    assert any(f.code == "INVALID_JSONLD" for f in report.findings)
