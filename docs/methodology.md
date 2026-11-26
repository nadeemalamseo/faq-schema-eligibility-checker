# Audit Methodology

The checker is a deterministic, local quality-control utility. It does not fetch websites or run JavaScript.

## 1. Input

The CLI reads a local HTML document. The audit functions operate on the supplied HTML string and make no network requests.

## 2. Visible FAQ extraction

Supported patterns include:

- H2/H3/H4 followed by a paragraph or answer block
- DT/DD definition-list pairs
- SUMMARY followed by an answer paragraph

Nested inline elements (for example, strong and em) are included in captured text. Script, style, noscript, and template contents are excluded. This is a lightweight HTML parser, not a browser rendering engine; it does not calculate CSS visibility or accessibility-tree output.

## 3. JSON-LD extraction

The checker scans script elements whose media type is application/ld+json, including a media-type parameter. It recognizes FAQPage nodes in top-level objects, arrays, and nested @graph containers. The @type value may be the compact FAQPage name, an absolute Schema.org type IRI, or an array containing either form.

For each FAQPage, it checks that mainEntity contains supported Question objects with a non-empty name and acceptedAnswer.text string. This is a deliberately limited subset of Schema.org, not a complete vocabulary validator.

## 4. Matching

Visible and structured-data pairs are compared using normalized text:

- HTML entities are decoded
- repeated whitespace is collapsed
- leading and trailing whitespace is removed
- comparison is case-insensitive

The checker does not infer semantic equivalence or use an LLM.

## 5. Findings

The checker can report NO_FAQPAGE, DUPLICATE_FAQPAGE, NO_VISIBLE_FAQ, INVALID_JSONLD, SCHEMA_VISIBLE_MISMATCH, VISIBLE_NOT_MARKED_UP, SCHEMA_WITHOUT_VISIBLE_FAQ, and AUDIT_PASS.

PASS, REVIEW, and FAIL are tool-specific statuses, not Schema.org validation grades or Google Search feature eligibility decisions.

## 6. Search feature context

Google announced that FAQ rich results would stop appearing in Search beginning May 7, 2026, and removed the feature documentation in June 2026. This checker therefore focuses on structured-data implementation consistency and content quality, not Google FAQ rich-result eligibility. FAQPage remains a Schema.org type; its presence does not imply a Google Search enhancement.

Official source: [Google Search documentation updates](https://developers.google.com/search/updates).
