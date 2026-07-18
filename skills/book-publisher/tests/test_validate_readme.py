import importlib.util
import tempfile
import time
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate-readme.py"
SPEC = importlib.util.spec_from_file_location("validate_readme", SCRIPT_PATH)
validate_readme = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_readme)


class MarkdownFenceFormattingTests(unittest.TestCase):
    def fence_issues(self, markdown: str):
        return [
            issue
            for issue in validate_readme.check_markdown_formatting(markdown)
            if "without language specification" in issue
        ]

    def test_labeled_opening_and_closing_fence_have_no_issue(self):
        markdown = "# Example\n\n```bash\necho hello\n```\n"

        self.assertEqual(self.fence_issues(markdown), [])

    def test_multiple_labeled_blocks_do_not_count_closing_fences(self):
        markdown = (
            "# Examples\n\n"
            "```bash\necho hello\n```\n\n"
            "```json\n{\"ok\": true}\n```\n\n"
            "````markdown\n```python\nprint('nested')\n```\n````\n"
        )

        self.assertEqual(self.fence_issues(markdown), [])

    def test_unlabeled_opening_is_reported_once(self):
        markdown = "# Example\n\n```\necho hello\n```\n"

        self.assertEqual(
            self.fence_issues(markdown),
            ["Found 1 code block(s) without language specification"],
        )

    def test_tilde_fence_uses_the_same_open_close_rules(self):
        labeled = "# Example\n\n~~~python\nprint('hello')\n~~~\n"
        unlabeled = "# Example\n\n~~~\nplain text\n~~~\n"

        self.assertEqual(self.fence_issues(labeled), [])
        self.assertEqual(
            self.fence_issues(unlabeled),
            ["Found 1 code block(s) without language specification"],
        )

    def test_unclosed_unlabeled_opening_is_still_reported(self):
        markdown = "# Example\n\n```\nunfinished block\n"

        self.assertEqual(
            self.fence_issues(markdown),
            ["Found 1 code block(s) without language specification"],
        )


class RequiredSectionTests(unittest.TestCase):
    def test_unrelated_license_prose_is_not_a_license_section(self):
        markdown = (
            "# Demo\n\n"
            "## Overview\n\nFixture.\n\n"
            "## Getting Started\n\nUse it.\n\n"
            "## Acknowledgements\n\n"
            "A dependency's license is documented upstream.\n\n"
            "## Contact\n\nFixture owner.\n"
        )

        found_required, missing_required, found_recommended, _ = (
            validate_readme.check_required_sections(markdown)
        )

        self.assertEqual(found_required, ["overview", "getting started", "contact"])
        self.assertEqual(missing_required, [])
        self.assertNotIn("license", found_recommended)

    def test_license_heading_is_detected_structurally(self):
        markdown = (
            "# Demo\n\n"
            "Overview\n--------\n\nFixture.\n\n"
            "## Getting-Started\n\nUse it.\n\n"
            "## License ##\n\nSee LICENSE.\n\n"
            "## Contact\n\nFixture owner.\n"
        )

        found_required, missing_required, found_recommended, _ = (
            validate_readme.check_required_sections(markdown)
        )

        self.assertEqual(found_required, ["overview", "getting started", "contact"])
        self.assertEqual(missing_required, [])
        self.assertIn("license", found_recommended)

    def test_headings_inside_fenced_examples_do_not_satisfy_sections(self):
        markdown = (
            "# Demo\n\n"
            "```markdown\n"
            "## Overview\n"
            "## Getting Started\n"
            "## Contact\n"
            "```\n"
        )

        found_required, missing_required, _, _ = (
            validate_readme.check_required_sections(markdown)
        )

        self.assertEqual(found_required, [])
        self.assertEqual(
            missing_required,
            ["overview", "getting started", "contact"],
        )

    def test_named_section_ignores_matching_heading_inside_fence(self):
        markdown = (
            "# Demo\n\n"
            "```markdown\n"
            "## License\n"
            "MIT\n"
            "```\n\n"
            "## License\n"
            "See [LICENSE](LICENSE).\n"
            "## Contact\n"
            "Write us.\n"
        )

        section = validate_readme.extract_named_section(markdown, "license")

        self.assertEqual(section, "See [LICENSE](LICENSE).")


class ReadmeLinkValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, relative_path: str, content: str = "") -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def check(self, markdown: str):
        readme = self.write("README.md", markdown)
        return validate_readme.check_links(markdown, readme, self.root)

    def test_existing_readme_relative_files_are_verified(self):
        self.write("docs/guide.md", "# Guide\n")

        report = self.check(
            "[relative](docs/guide.md) and [dot-relative](./docs/guide.md)"
        )

        self.assertEqual(report["invalid_count"], 0)
        self.assertEqual(report["local_verified_count"], 2)

    def test_origin_relative_link_is_not_certified_as_repository_local(self):
        self.write("docs/guide.md", "# Guide\n")

        report = self.check("[host path](/docs/guide.md)")

        self.assertEqual(report["invalid_count"], 0)
        self.assertEqual(report["local_verified_count"], 0)
        self.assertEqual(report["origin_relative_unverified_count"], 1)
        self.assertFalse(report["entries"][0]["reachability_verified"])

    def test_missing_file_and_repository_escape_fail_with_reasons(self):
        outside = self.root.parent / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)

        report = self.check(
            "[missing](docs/missing.md) and [escape](../outside.md)"
        )

        self.assertEqual(report["invalid_count"], 2)
        self.assertEqual(
            {issue["reason"] for issue in report["issues"]},
            {"missing-local-target", "repository-escape"},
        )

    def test_same_document_and_target_document_anchors_are_verified(self):
        self.write(
            "docs/guide.md",
            "# Guide\n\n## Setup (Advanced)\n\n## Setup (Advanced)\n",
        )

        report = self.check(
            "# Demo\n\n"
            "## Local Setup\n\n"
            "[local](#local-setup)\n"
            "[target](docs/guide.md#setup-advanced)\n"
            "[duplicate](docs/guide.md#setup-advanced-1)\n"
            "[missing](docs/guide.md#not-there)\n"
        )

        self.assertEqual(report["local_verified_count"], 3)
        self.assertEqual(report["invalid_count"], 1)
        self.assertEqual(report["issues"][0]["reason"], "missing-markdown-anchor")

    def test_heading_anchor_uses_rendered_link_text_not_nested_destination(self):
        self.write(
            "docs/guide.md",
            "# [RFC](spec(foo).md)\n\n## ![Status](badge(ok).svg) Setup\n",
        )

        report = self.check(
            "[rfc](docs/guide.md#rfc) "
            "[status](docs/guide.md#status-setup)"
        )

        self.assertEqual(report["invalid_count"], 0)
        self.assertEqual(report["local_verified_count"], 2)

    def test_nested_parentheses_reference_links_and_images_are_extracted(self):
        self.write("docs/spec(foo).md", "# Specification\n")
        self.write("assets/diagram (final).png", "png")
        markdown = (
            "[RFC](docs/spec(foo).md)\n"
            "[Guide][guide]\n"
            "![Diagram][diagram]\n\n"
            "[guide]: docs/spec(foo).md\n"
            "[diagram]: <assets/diagram (final).png>\n"
        )

        report = self.check(markdown)

        self.assertEqual(report["total"], 3)
        self.assertEqual(report["local_verified_count"], 3)
        self.assertEqual(report["invalid_count"], 0)
        self.assertEqual(
            {entry["destination"] for entry in report["entries"]},
            {"docs/spec(foo).md", "assets/diagram (final).png"},
        )

    def test_badge_markup_validates_both_image_and_link_destinations(self):
        self.write("assets/build.svg", "svg")

        report = self.check(
            "[![Build](assets/build.svg)](https://example.com/build)"
        )

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["local_verified_count"], 1)
        self.assertEqual(report["external_unverified_count"], 1)
        self.assertEqual(
            {entry["element"] for entry in report["entries"]},
            {"image", "link"},
        )

    def test_multiline_destination_and_title_are_validated(self):
        self.write("docs/guide.md", "# Guide\n")

        report = self.check(
            "[Guide](\n"
            "  docs/guide.md#guide\n"
            "  \"Read the guide\"\n"
            ")\n"
        )

        self.assertEqual(report["total"], 1)
        self.assertEqual(report["local_verified_count"], 1)
        self.assertEqual(report["invalid_count"], 0)

    def test_unreadable_markdown_anchor_target_fails_closed(self):
        target = self.root / "docs" / "invalid.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"# Guide\n\xff")

        report = self.check("[guide](docs/invalid.md#guide)")

        self.assertEqual(report["invalid_count"], 1)
        self.assertEqual(report["issues"][0]["reason"], "unreadable-local-target")

    def test_fenced_and_inline_code_links_are_ignored(self):
        report = self.check(
            "`[inline](missing-inline.md)`\n\n"
            "```markdown\n"
            "[fenced](missing-fenced.md)\n"
            "```\n"
        )

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["invalid_count"], 0)

    def test_unmatched_brackets_are_scanned_in_bounded_time(self):
        markdown = "[" * 20_000

        started = time.monotonic()
        entries = validate_readme.extract_markdown_link_entries(markdown)
        elapsed = time.monotonic() - started

        self.assertEqual(entries, [])
        self.assertLess(elapsed, 1.0)

    def test_external_and_mail_links_do_not_claim_reachability(self):
        report = self.check(
            "[web](https://example.com/path) "
            "[mail](mailto:person@example.com)"
        )

        self.assertEqual(report["invalid_count"], 0)
        self.assertEqual(report["external_unverified_count"], 1)
        self.assertEqual(report["mail_count"], 1)
        external = next(
            entry for entry in report["entries"] if entry["kind"] == "external"
        )
        self.assertFalse(external["reachability_verified"])

    def test_malformed_or_unsupported_destinations_fail_closed(self):
        report = self.check(
            "[space](docs/a b.md) "
            "[scheme](javascript:alert(1)) "
            "[host](https:///missing-host) "
            "[port](https://example.com:not-a-port)"
        )

        self.assertEqual(report["invalid_count"], 4)
        self.assertEqual(
            {issue["reason"] for issue in report["issues"]},
            {
                "invalid-destination",
                "unsupported-scheme",
                "missing-host",
                "invalid-host",
            },
        )

    def test_full_validator_fails_broken_local_link_but_not_external_reachability(self):
        readme = self.write(
            "README.md",
            "# Demo\n\n"
            "## Overview\n\nOverview.\n\n"
            "## Getting Started\n\n"
            "[missing](docs/missing.md) and "
            "[external](https://example.com/resource).\n\n"
            "## Contact\n\nContact us.\n",
        )

        report = validate_readme.validate_readme(
            str(readme),
            repo_root=str(self.root),
        )

        self.assertFalse(report["valid"])
        self.assertEqual(report["links"]["invalid_count"], 1)
        self.assertEqual(report["links"]["external_unverified_count"], 1)
        self.assertIn("missing-local-target", report["recommendations"][1])

    def test_full_validator_accepts_verified_local_and_unverified_external_links(self):
        self.write("docs/guide.md", "# Guide\n")
        readme = self.write(
            "README.md",
            "# Demo\n\n"
            "## Overview\n\nOverview.\n\n"
            "## Getting Started\n\n"
            "[guide](docs/guide.md#guide) and "
            "[external](https://example.com/resource).\n\n"
            "## Contact\n\nContact us.\n",
        )

        report = validate_readme.validate_readme(
            str(readme),
            repo_root=str(self.root),
        )

        self.assertTrue(report["valid"])
        self.assertEqual(report["links"]["local_verified_count"], 1)
        self.assertEqual(report["links"]["external_unverified_count"], 1)

if __name__ == "__main__":
    unittest.main()
