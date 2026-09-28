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


def test_multiple_visible_faqs_are_matched():
    html = """
    <h2>What is SEO?</h2>
    <p>SEO helps search engines understand content.</p>
    <h2>What is JSON-LD?</h2>
    <p>JSON-LD is a format for structured data.</p>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {"@type":"Question","name":"What is SEO?","acceptedAnswer":{"@type":"Answer","text":"SEO helps search engines understand content."}},
        {"@type":"Question","name":"What is JSON-LD?","acceptedAnswer":{"@type":"Answer","text":"JSON-LD is a format for structured data."}}
      ]
    }
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"
    assert len(report.visible_faqs) == 2
    assert len(report.schema_faqs) == 2


def test_faqpage_inside_graph_is_detected():
    html = """
    <h2>What is SEO?</h2>
    <p>SEO helps search engines understand content.</p>
    <script type="application/ld+json">
    {
      "@context":"https://schema.org",
      "@graph":[
        {"@type":"WebSite","name":"Example"},
        {"@type":"FAQPage","mainEntity":[
          {"@type":"Question","name":"What is SEO?","acceptedAnswer":{"@type":"Answer","text":"SEO helps search engines understand content."}}
        ]}
      ]
    }
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"
