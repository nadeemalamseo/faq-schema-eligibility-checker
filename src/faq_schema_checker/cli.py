import argparse
import json
import sys
from pathlib import Path

from .audit import audit_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="faq-schema-check",
        description="Audit FAQPage JSON-LD against visible FAQ content in an HTML file.",
    )
    parser.add_argument("html_file", type=Path, help="Path to an HTML file to audit.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete audit report as JSON.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        html = args.html_file.read_text(encoding="utf-8")
    except OSError as exc:
        parser.error(f"cannot read {args.html_file}: {exc}")

    report = audit_html(html)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(f"Status: {report.status}")
        print(report.summary)
        print()
        for finding in report.findings:
            print(f"[{finding.severity.upper()}] {finding.code}: {finding.message}")
            if finding.evidence:
                print(f"  Evidence: {finding.evidence}")
            if finding.recommendation:
                print(f"  Recommendation: {finding.recommendation}")
            print()

    return 1 if report.status == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
