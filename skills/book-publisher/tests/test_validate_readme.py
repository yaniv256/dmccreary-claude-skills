import importlib.util
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

if __name__ == "__main__":
    unittest.main()
