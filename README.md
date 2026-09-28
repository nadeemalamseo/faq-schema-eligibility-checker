# FAQ Schema Eligibility Checker

Audit FAQPage structured data against visible FAQ content and detect common implementation and content-consistency issues.

> Status: Early alpha. The checker provides deterministic technical findings; it does not predict or guarantee a Google Search appearance.

## Why this exists

FAQPage markup is easy to generate and easy to get out of sync with the content users can actually see. This tool focuses on that quality-control gap.

It checks a local HTML document for:

- visible FAQ question/answer pairs in common HTML patterns
- FAQPage JSON-LD
- duplicate FAQPage implementations
- malformed Question/Answer structures
- exact question-and-answer mismatches between visible content and JSON-LD
- visible FAQ items that are not represented in the detected FAQPage markup

## What it does not do

This project does not:

- guarantee Google rich results, rankings, indexing, or traffic
- determine Google's future search-feature decisions
- connect to Google Search Console
- crawl websites over the network
- replace Google's or Schema.org's validators
- decide whether a page is legally or editorially required to contain FAQs

The repository name uses "eligibility" as a historical shorthand for implementation quality. It does **not** claim eligibility for a Google Search feature. Google removed the FAQ rich result from Search in 2026; this tool remains useful for auditing the technical consistency of FAQPage structured data with visible page content.

## Installation

Python 3.10+ is required.

From a clone of this repository:

    python -m pip install -e .

No runtime dependencies outside Python's standard library are required.

## Usage

Audit an HTML file:

    faq-schema-check examples/valid-faq.html

Print machine-readable JSON:

    faq-schema-check examples/valid-faq.html --json

You can also run it without installing the console script:

    python -m faq_schema_checker.cli examples/valid-faq.html

## Result statuses

- PASS — the supported checks found a matching FAQPage implementation.
- REVIEW — the implementation needs attention but no error-level finding was produced.
- FAIL — one or more error-level findings were detected.

These statuses describe this tool's checks only. They are not Google Search eligibility labels.

## Audit model

    HTML input
       ↓
    Visible FAQ extraction
       ↓
    FAQPage JSON-LD extraction
       ↓
    Structural checks
       ↓
    Visible ↔ structured-data comparison
       ↓
    Findings + recommendations

## Example

For a valid page, the CLI reports:

    Status: PASS
    0 error(s), 0 warning(s), 1 schema FAQ item(s), 1 visible FAQ item(s).

    [INFO] AUDIT_PASS: The detected FAQPage implementation matches the supported visible FAQ content.

## Methodology

The initial implementation deliberately uses deterministic, local checks:

1. Parse supported visible FAQ structures.
2. Parse application/ld+json blocks.
3. Locate FAQPage nodes, including nodes inside @graph.
4. Validate the presence of Question names and accepted-answer text.
5. Compare normalized visible questions/answers with structured-data questions/answers.
6. Report duplicate implementations and mismatches.

The checker uses exact normalized text matching in this first release. It does not use an LLM or infer semantic equivalence.

## Limitations

HTML is flexible, and no small parser can reliably infer every visual FAQ component from arbitrary websites. A page using a JavaScript widget, unusual DOM structure, shadow DOM, or content loaded after initial HTML may require a different inspection method.

The checker therefore reports findings based on the HTML it receives and the structures it supports.

## Related resource

For practical guidance on evaluating, matching, validating, inspecting, and maintaining FAQ structured data, see the [FAQ schema best practices guide](https://marketlatch.com/faq-schema-best-practices/?utm_source=github&utm_medium=referral&utm_campaign=github_faq_schema_eligibility_checker).

## Contributing

See CONTRIBUTING.md.

## Security

See SECURITY.md.

## Project links

- [Project landing page](https://nadeemalamseo.github.io/faq-schema-eligibility-checker/)
- [v0.1.0 release](https://github.com/nadeemalamseo/faq-schema-eligibility-checker/releases/tag/v0.1.0)
- [Download v0.1.0 ZIP](https://github.com/nadeemalamseo/faq-schema-eligibility-checker/archive/refs/tags/v0.1.0.zip)

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).
