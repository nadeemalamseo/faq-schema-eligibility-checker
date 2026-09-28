# Audit Methodology

The checker is intentionally deterministic and local.

## 1. Input

The tool reads an HTML document from the local filesystem. Core auditing does not make network requests.

## 2. Visible FAQ extraction

The first implementation supports common question-and-answer patterns:

- H2/H3/H4 followed by a paragraph or answer block
- DT/DD definition-list pairs
- SUMMARY followed by an answer paragraph

The extractor returns the question and answer text that it can identify from the supplied HTML.

## 3. JSON-LD extraction

The tool scans script elements with type application/ld+json and parses valid JSON.

It recognizes FAQPage nodes:

- directly in a JSON-LD object
- in a top-level JSON-LD array
- inside an @graph array
- where @type is FAQPage or includes FAQPage in a type array

For each Question, it checks for a non-empty name and acceptedAnswer.text.

## 4. Matching

Visible and structured-data pairs are compared using normalized text:

- HTML entities are decoded
- repeated whitespace is collapsed
- leading and trailing whitespace is removed
- comparison is case-insensitive

The first release deliberately does not use semantic similarity or an LLM.

## 5. Findings

The checker can report:

- NO_FAQPAGE
- DUPLICATE_FAQPAGE
- NO_VISIBLE_FAQ
- INVALID_JSONLD
- SCHEMA_VISIBLE_MISMATCH
- VISIBLE_NOT_MARKED_UP
- SCHEMA_WITHOUT_VISIBLE_FAQ
- AUDIT_PASS

Severity indicates the tool's own technical assessment:

- error
- warning
- info

## 6. Interpretation

PASS, REVIEW, and FAIL are tool-specific audit statuses. They are not Google's search-feature eligibility decisions.

A technically correct implementation can still receive no special search appearance.
