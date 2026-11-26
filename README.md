# FAQ Schema Eligibility Checker

Audit FAQPage structured data against visible FAQ content and detect common implementation and content-consistency issues.

> Status: Early alpha. The checker provides deterministic technical findings; it does not predict or guarantee a Google Search appearance.

## Why this exists

FAQPage markup can become inconsistent with the FAQ content people actually see. This tool focuses on that quality-control gap.

It checks a local HTML document for:

- visible FAQ question/answer pairs in supported HTML patterns
- FAQPage JSON-LD, including top-level arrays and nested @graph nodes
- duplicate FAQPage implementations
- malformed or incomplete supported Question/Answer structures
- exact normalized question-and-answer mismatches
- visible FAQ items not represented in detected FAQPage markup

## Important Google Search context

Google announced that FAQ rich results would stop appearing in Search beginning May 7, 2026, and removed the feature documentation in June 2026. This project name is retained for repository continuity; it does **not** assess Google FAQ rich-result eligibility. FAQPage remains a Schema.org type, and this tool audits implementation consistency rather than search-feature availability.

See [Google Search documentation updates](https://developers.google.com/search/updates).

## What it does not do

This project does not guarantee rankings, indexing, traffic, rich results, or search visibility. It does not connect to Search Console, crawl websites, execute JavaScript, render CSS, or replace the Schema.org Validator or other authoritative validators.

## Installation

Python 3.10+ is required. From a clone:

    python -m pip install -e .

No runtime dependencies outside Python's standard library are required.

## Usage

    faq-schema-check examples/valid-faq.html
    faq-schema-check examples/valid-faq.html --json

Or without installing the console script:

    python -m faq_schema_checker.cli examples/valid-faq.html

## Result statuses

- PASS — supported checks found matching FAQPage markup and visible FAQ content.
- REVIEW — attention is recommended, but no error-level finding was produced.
- FAIL — one or more error-level findings were detected.

These are tool-specific implementation statuses, not Google Search eligibility labels.

## Audit model

    HTML input
       ↓
    Visible FAQ extraction
       ↓
    FAQPage JSON-LD extraction
       ↓
    Supported structural checks
       ↓
    Visible ↔ structured-data comparison
       ↓
    Findings + recommendations

## Methodology and limitations

See [Audit Methodology](docs/methodology.md) and [Limitations](docs/limitations.md). The parser supports conventional server-rendered FAQ patterns; unusual markup, JavaScript-rendered content, shadow DOM, and CSS visibility require browser-based inspection.

## Related resource

For practical guidance on evaluating and maintaining FAQ structured data, see the [FAQ schema best practices guide](https://marketlatch.com/faq-schema-best-practices/?utm_source=github&utm_medium=referral&utm_campaign=github_faq_schema_eligibility_checker).

## Project links

- [Project landing page](https://nadeemalamseo.github.io/faq-schema-eligibility-checker/)
- [Latest source ZIP](https://github.com/nadeemalamseo/faq-schema-eligibility-checker/archive/refs/heads/main.zip)
- [Historical v0.1.0 release](https://github.com/nadeemalamseo/faq-schema-eligibility-checker/releases/tag/v0.1.0)

## License

MIT. See [LICENSE](LICENSE).
