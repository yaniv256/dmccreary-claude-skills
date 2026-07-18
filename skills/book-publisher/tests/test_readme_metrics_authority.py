import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parents[1] / "scripts"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


metrics_authority = load_module("readme_metrics_authority_test", "metrics_authority.py")
collect_site_metrics = load_module("collect_site_metrics_test", "collect-site-metrics.py")
validate_readme = load_module("validate_readme_metrics_test", "validate-readme.py")


BASE_METRICS = {
    "concepts": 158,
    "chapters": 12,
    "microsims": 14,
    "stories": 0,
    "glossaryTerms": 158,
    "faqs": 48,
    "quizQuestions": 24,
    "chapterQuizzes": 12,
    "chapterReferences": 12,
    "references": 96,
    "diagrams": 18,
    "equations": 3,
    "words": 162054,
    "links": 1907,
    "appendices": 2,
    "mascotImages": 4,
    "developmentStage": "Published",
    "equivalentPages": 655,
}


BASE_README = """# Demo Book

## Overview

Fixture.

## Site Status and Metrics

| Metric | Count |
| --- | ---: |
| Concepts in Learning Graph | 158 |
| Chapters | 12 |
| Total Words | 162,054 |
| MicroSims | 14 |
| Markdown Files | 3 |

## Getting Started

Use it.

## Contact

Fixture owner.
"""


class MetricsRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.write("docs/index.md", "# Home\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_metrics(self, metrics=None) -> Path:
        payload = {
            "$schema": "https://example.test/book-metrics.schema.json",
            "metricsVersion": "1.0",
            "metricsGeneratedBy": "Book Metrics Python Program v0.09",
            "metricsGeneratedOn": "July 17, 2026 at 10:00 AM",
            "metricsGeneratedOnISO": "2026-07-17T10:00:00",
            "metrics": metrics or dict(BASE_METRICS),
        }
        return self.write(
            "docs/learning-graph/book-metrics.json",
            json.dumps(payload, indent=2) + "\n",
        )

    def make_fresh(self, metrics_path: Path) -> None:
        newest_input = max(
            path.stat().st_mtime
            for path in self.root.rglob("*")
            if path.is_file() and path != metrics_path
        )
        os.utime(metrics_path, (newest_input + 5, newest_input + 5))


class CanonicalMetricsAuthorityTests(MetricsRepoTestCase):
    def test_missing_canonical_file_fails_closed(self):
        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "missing")

    def test_malformed_canonical_file_fails_closed(self):
        self.write("docs/learning-graph/book-metrics.json", "{not json")

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "malformed")

    def test_schema_invalid_canonical_file_fails_closed(self):
        metrics_path = self.write_metrics({"chapters": 12})
        self.make_fresh(metrics_path)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "invalid")
        self.assertTrue(any("metrics.concepts" in issue for issue in report["issues"]))

    def test_newer_source_marks_canonical_file_stale(self):
        metrics_path = self.write_metrics()
        self.make_fresh(metrics_path)
        source = self.write("docs/chapters/01/index.md", "# Changed later\n")
        os.utime(source, (metrics_path.stat().st_mtime + 5,) * 2)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "stale")
        self.assertIn("docs/chapters/01/index.md", report["newer_sources"])

    def test_clean_git_checkout_ignores_checkout_mtime_order(self):
        metrics_path = self.write_metrics()
        self.make_fresh(metrics_path)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "book and metrics"], cwd=self.root, check=True)
        source = self.root / "docs/index.md"
        os.utime(source, (metrics_path.stat().st_mtime + 30,) * 2)

        report = metrics_authority.inspect_repository(self.root)

        self.assertTrue(report["valid"])
        self.assertEqual(report["freshnessMode"], "git")

    def test_git_source_commit_after_metrics_marks_canonical_file_stale(self):
        metrics_path = self.write_metrics()
        self.make_fresh(metrics_path)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "canonical metrics"], cwd=self.root, check=True)
        self.write("docs/chapters/02.md", "# New chapter\n")
        subprocess.run(["git", "add", "docs/chapters/02.md"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "new source"], cwd=self.root, check=True)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "stale")
        self.assertEqual(report["freshnessMode"], "git")
        self.assertIn("docs/chapters/02.md", report["newer_sources"])

    def test_git_source_deletion_after_metrics_marks_canonical_file_stale(self):
        metrics_path = self.write_metrics()
        self.make_fresh(metrics_path)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "canonical metrics"], cwd=self.root, check=True)
        (self.root / "docs/index.md").unlink()
        subprocess.run(["git", "add", "docs/index.md"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "remove source"], cwd=self.root, check=True)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "stale")
        self.assertIn("docs/index.md", report["newer_sources"])

    def test_symlinked_docs_parent_is_rejected(self):
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside_docs = Path(outside_temp.name) / "docs"
        outside_docs.mkdir()
        shutil.rmtree(self.root / "docs")
        (self.root / "docs").symlink_to(outside_docs, target_is_directory=True)
        self.write_metrics()

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "unsafe-path")

    def test_conflicting_supplied_identity_metadata_fails_closed(self):
        metrics_path = self.write_metrics()
        self.write(
            "docs/learning-graph/book-metadata.json",
            json.dumps({"title": "Metadata Title", "metrics": BASE_METRICS}),
        )
        self.write("mkdocs.yml", "site_name: 'Different Site Title'\n")
        self.make_fresh(metrics_path)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "inconsistent")
        self.assertTrue(any("site_name" in issue for issue in report["issues"]))

    def test_metadata_metrics_disagreement_fails_closed(self):
        metrics_path = self.write_metrics()
        self.write(
            "docs/learning-graph/book-metadata.json",
            json.dumps({"title": "Demo", "metrics": {**BASE_METRICS, "chapters": 99}}),
        )
        self.make_fresh(metrics_path)

        report = metrics_authority.inspect_repository(self.root)

        self.assertFalse(report["valid"])
        self.assertEqual(report["state"], "inconsistent")
        self.assertTrue(any("book-metadata.json" in issue for issue in report["issues"]))

    def test_canonical_values_and_field_provenance_survive_both_chapter_layouts(self):
        for chapter_path in ("docs/chapters/01.md", "docs/chapters/01/index.md"):
            with self.subTest(chapter_path=chapter_path):
                self.tearDown()
                self.setUp()
                self.write(chapter_path, "# Scanner would count one chapter\n")
                self.write("docs/notes.md", "```python\nprint('supplemental')\n```\n")
                self.write("docs/img/example.svg", "<svg></svg>\n")
                metrics_path = self.write_metrics()
                self.make_fresh(metrics_path)

                report = collect_site_metrics.collect_metrics(str(self.root))

                self.assertEqual(report["canonical"]["metrics"]["chapters"], 12)
                self.assertEqual(report["canonical"]["metrics"]["words"], 162054)
                self.assertNotIn("chapters", report["supplemental"])
                self.assertNotIn("words", report["supplemental"])
                self.assertEqual(report["supplemental"]["codeBlocks"], 1)
                self.assertEqual(report["supplemental"]["imageAssets"], 1)
                self.assertEqual(
                    report["canonical"]["provenance"]["chapters"],
                    "docs/learning-graph/book-metrics.json#/metrics/chapters",
                )
                self.assertEqual(
                    report["supplementalProvenance"]["codeBlocks"],
                    "filesystem:docs/**/*.md",
                )


class ReadmeMetricsValidationTests(MetricsRepoTestCase):
    def validate(self, readme_content: str):
        metrics_path = self.write_metrics()
        self.make_fresh(metrics_path)
        readme = self.write("README.md", readme_content)
        return validate_readme.validate_readme(str(readme), repo_root=str(self.root))

    def test_matching_readme_table_is_valid(self):
        report = self.validate(BASE_README)

        self.assertTrue(report["metrics_authority"]["valid"])
        self.assertEqual(report["metrics_authority"]["checked_fields"], 4)

    def test_disagreeing_readme_table_is_a_hard_failure(self):
        report = self.validate(BASE_README.replace("| Chapters | 12 |", "| Chapters | 1 |"))

        self.assertFalse(report["valid"])
        self.assertTrue(
            any("chapters" in issue for issue in report["metrics_authority"]["issues"])
        )

    def test_non_numeric_canonical_claim_cannot_bypass_validation(self):
        report = self.validate(
            BASE_README.replace("| Chapters | 12 |", "| Chapters | about twelve |")
        )

        self.assertFalse(report["valid"])
        self.assertEqual(report["metrics_authority"]["state"], "conflicting-claims")
        self.assertTrue(
            any("non-negative integer" in issue for issue in report["metrics_authority"]["issues"])
        )

    def test_metrics_table_without_canonical_file_is_a_hard_failure(self):
        readme = self.write("README.md", BASE_README)

        report = validate_readme.validate_readme(str(readme), repo_root=str(self.root))

        self.assertFalse(report["valid"])
        self.assertEqual(report["metrics_authority"]["state"], "missing")


if __name__ == "__main__":
    unittest.main()
