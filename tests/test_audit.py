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
    {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":"What is SEO?","acceptedAnswer":{"@type":"Answer","text":"SEO helps search engines understand content."}},
      {"@type":"Question","name":"What is JSON-LD?","acceptedAnswer":{"@type":"Answer","text":"JSON-LD is a format for structured data."}}
    ]}
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"
    assert len(report.visible_faqs) == 2
    assert len(report.schema_faqs) == 2


def test_faqpage_inside_graph_is_detected():
    html = """
    <h2>What is SEO?</h2><p>SEO helps search engines understand content.</p>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@graph":[
      {"@type":"WebSite","name":"Example"},
      {"@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":"What is SEO?","acceptedAnswer":{"@type":"Answer","text":"SEO helps search engines understand content."}}
      ]}
    ]}
    </script>
    """
    assert audit_html(html).status == "PASS"


def test_empty_main_entity_fails():
    html = '<h2>Q?</h2><p>A.</p><script type="application/ld+json">{"@type":"FAQPage","mainEntity":[]}</script>'
    report = audit_html(html)
    assert report.status == "FAIL"
    assert any(f.code == "INVALID_JSONLD" for f in report.findings)


def test_missing_main_entity_fails():
    report = audit_html('<script type="application/ld+json">{"@type":"FAQPage"}</script>')
    assert report.status == "FAIL"
    assert any(f.code == "INVALID_JSONLD" for f in report.findings)


def test_nested_inline_markup_does_not_truncate_question_or_answer():
    html = """
    <h2>What is <strong>technical SEO</strong>?</h2>
    <p>It helps <em>search engines</em> crawl and understand a site.</p>
    <script type="application/ld+json">
    {"@type":"FAQPage","mainEntity":[{"@type":"Question",
    "name":"What is technical SEO?","acceptedAnswer":{"@type":"Answer",
    "text":"It helps search engines crawl and understand a site."}}]}
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"
    assert report.visible_faqs[0].question == "What is technical SEO?"
    assert report.visible_faqs[0].answer == "It helps search engines crawl and understand a site."


def test_details_summary_question_matches_following_answer():
    html = """
    <details><summary>What is JSON-LD?</summary>
    <p>It is a JSON format for linked data.</p></details>
    <script type="application/ld+json">
    {"@type":"FAQPage","mainEntity":[{"name":"What is JSON-LD?",
    "acceptedAnswer":{"text":"It is a JSON format for linked data."}}]}
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"


def test_script_and_style_text_is_not_extracted_as_visible_faq():
    html = """
    <script>const x = "<h2>Fake question?</h2>";</script>
    <style>h2 { content: "Not an FAQ"; }</style>
    <h2>Real question?</h2><p>Real answer.</p>
    """
    report = audit_html(html)
    assert len(report.visible_faqs) == 1
    assert report.visible_faqs[0].question == "Real question?"


def test_schema_org_absolute_faqpage_type_is_recognized():
    html = """
    <h2>Q?</h2><p>A.</p>
    <script type="application/ld+json">
    {"@type":"https://schema.org/FAQPage","mainEntity":[{"name":"Q?","acceptedAnswer":{"text":"A."}}]}
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"
    assert len(report.schema_faqs) == 1


def test_type_array_and_media_type_parameters_are_supported():
    html = """
    <h2>Q?</h2><p>A.</p>
    <script type="application/ld+json; charset=utf-8">
    {"@type":["WebPage","https://schema.org/FAQPage"],"mainEntity":[{"name":"Q?","acceptedAnswer":{"text":"A."}}]}
    </script>
    """
    report = audit_html(html)
    assert report.status == "PASS"


def test_root_sibling_and_nested_graph_nodes_are_both_scanned():
    html = """
    <h2>Q?</h2><p>A.</p>
    <script type="application/ld+json">
    [{"@type":"WebPage","@graph":[{"@type":"FAQPage","mainEntity":[{"name":"Q?","acceptedAnswer":{"text":"A."}}]}]},
     {"@type":"FAQPage","mainEntity":[{"name":"Q?","acceptedAnswer":{"text":"A."}}]}]
    </script>
    """
    report = audit_html(html)
    assert report.status == "FAIL"
    assert any(f.code == "DUPLICATE_FAQPAGE" for f in report.findings)


def test_jsonld_type_detection_does_not_match_unrelated_suffix():
    html = '<script type="application/ld+json">{"@type":"NotFAQPage","mainEntity":[]}</script>'
    report = audit_html(html)
    assert not any(f.code == "INVALID_JSONLD" for f in report.findings)
    assert any(f.code == "NO_FAQPAGE" for f in report.findings)


def test_summary_answer_and_nested_markup_are_supported():
    html = """
    <details><summary>What is <b>SEO</b>?</summary>
    <p>SEO improves <strong>organic discoverability</strong>.</p></details>
    """
    report = audit_html(html)
    assert len(report.visible_faqs) == 1
    assert report.visible_faqs[0].question == "What is SEO?"
    assert report.visible_faqs[0].answer == "SEO improves organic discoverability."
