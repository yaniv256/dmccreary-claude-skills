import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).parents[3]
GUIDANCE_PATHS = (
    REPO_ROOT / "skills" / "book-publisher" / "references" / "readme-guide.md",
    REPO_ROOT / "skills" / "archived" / "readme-generator" / "SKILL.md",
    REPO_ROOT / "skills" / "archived" / "readme-generator" / "README.md",
    REPO_ROOT / "docs" / "prompts" / "readme-generator-skill.md",
)
SCANNER_PATHS = (
    REPO_ROOT / "skills" / "book-publisher" / "scripts" / "collect-site-metrics.py",
)
ARCHIVED_SCANNER = (
    REPO_ROOT / "skills" / "archived" / "readme-generator" / "scripts"
    / "collect-site-metrics.py"
)


class ReadmeMetricsGuidanceContractTests(unittest.TestCase):
    def test_every_guidance_surface_names_the_canonical_authority(self):
        for path in GUIDANCE_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn("docs/learning-graph/book-metrics.json", content)
                self.assertRegex(content.lower(), r"single source of truth|only authority")

    def test_guidance_does_not_advertise_broad_fallback_recounting(self):
        forbidden_patterns = (
            r"scans /docs for metrics \(chapters, microsims, glossary\)",
            r"markdown file count and word counts",
            r"chapter and section counts",
            r"microsim count",
            r"glossary, faq, quiz statistics",
            r"learning graph statistics",
        )

        for path in GUIDANCE_PATHS:
            content = path.read_text(encoding="utf-8").lower()
            with self.subTest(path=path):
                for pattern in forbidden_patterns:
                    self.assertIsNone(re.search(pattern, content))

    def test_scanner_public_contract_exposes_only_supplemental_fields(self):
        forbidden_output_keys = (
            "total_words",
            "chapters",
            "equations",
            "concepts",
            "microsims",
            "quizzes",
            "quiz_questions",
            "glossary_terms",
            "faq_questions",
            "references",
        )

        for path in SCANNER_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('"canonical"', content)
                self.assertIn('"supplemental"', content)
                for key in forbidden_output_keys:
                    self.assertNotRegex(content, rf"[\"']{re.escape(key)}[\"']\s*:")

    def test_archived_scanner_delegates_to_active_contract(self):
        content = ARCHIVED_SCANNER.read_text(encoding="utf-8")

        self.assertIn('ACTIVE_SCRIPT', content)
        self.assertIn('collect_metrics = active.collect_metrics', content)


if __name__ == "__main__":
    unittest.main()
