import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/microsim-utils/scripts/diagram-report.py"
COMPATIBILITY_SCRIPT = ROOT / "src/diagram-reports/diagram-report.py"

spec = importlib.util.spec_from_file_location("diagram_report", SCRIPT)
diagram_report = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = diagram_report
spec.loader.exec_module(diagram_report)


SPEC = """# Chapter

#### Diagram: Decision <Boundary>

<details>
<summary>Specification</summary>

**Type:** MicroSim
**Status:** Planned
**Learning Objective:** Compare the outcomes.
**Bloom's Taxonomy:** Analyzing
**MicroSim Generator Recommendations:**
1. forms-generator (88/100)

A slider and a button control the display.
</details>
"""


class DiagramReportTests(unittest.TestCase):
    def test_discovers_flat_and_nested_chapter_layouts(self):
        with tempfile.TemporaryDirectory() as directory:
            chapters = Path(directory)
            (chapters / "01-flat.md").write_text(SPEC, encoding="utf-8")
            nested = chapters / "02-nested"
            nested.mkdir()
            (nested / "index.md").write_text(SPEC, encoding="utf-8")

            analyzer = diagram_report.DiagramAnalyzer(str(chapters))
            analyzer.analyze_all_chapters()

            self.assertEqual(len(analyzer.chapter_files), 2)
            self.assertEqual(len(analyzer.elements), 2)
            self.assertEqual(analyzer.errors, [])
            self.assertEqual(
                [element.source_file for element in analyzer.elements],
                ["01-flat.md", "02-nested/index.md"],
            )

    def test_reports_link_to_the_real_source_layout_and_label_heuristics(self):
        with tempfile.TemporaryDirectory() as directory:
            chapters = Path(directory)
            (chapters / "01-flat.md").write_text(SPEC, encoding="utf-8")
            analyzer = diagram_report.DiagramAnalyzer(str(chapters))
            analyzer.analyze_all_chapters()

            generator = diagram_report.ReportGenerator(analyzer.elements)
            table = generator.generate_markdown_table()
            details = generator.generate_markdown_details()

            self.assertIn(
                "../chapters/01-flat.md#diagram-decision-boundary", table
            )
            self.assertIn("UI Mentions", table)
            self.assertIn("Planning Heuristic", table)
            self.assertIn("forms-generator (88)", table)
            self.assertIn("**UI keyword mentions:** 4", details)

    def test_csv_includes_status_and_recommendations(self):
        with tempfile.TemporaryDirectory() as directory:
            chapters = Path(directory) / "chapters"
            chapters.mkdir()
            (chapters / "01-flat.md").write_text(SPEC, encoding="utf-8")
            analyzer = diagram_report.DiagramAnalyzer(str(chapters))
            analyzer.analyze_all_chapters()
            output = Path(directory) / "report.csv"

            diagram_report.ReportGenerator(analyzer.elements).generate_csv(str(output))
            with output.open(newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle))

            self.assertEqual(row["Status"], "Planned")
            self.assertEqual(row["MicroSim Recommendations"], "forms-generator (88)")

    def test_empty_schema_fails_closed_unless_explicitly_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "01-flat.md").write_text("# No legacy specs\n", encoding="utf-8")
            output = root / "out"
            command = [
                sys.executable,
                str(SCRIPT),
                "--chapters-dir",
                str(chapters),
                "--output-dir",
                str(output),
            ]

            failed = subprocess.run(command, capture_output=True, text=True)
            allowed = subprocess.run(
                [*command, "--allow-empty"], capture_output=True, text=True
            )

            self.assertEqual(failed.returncode, 2)
            self.assertIn("only inventories", failed.stdout)
            self.assertEqual(allowed.returncode, 0)
            self.assertTrue((output / "diagram-table.md").exists())

    def test_html_escapes_specification_titles(self):
        with tempfile.TemporaryDirectory() as directory:
            chapters = Path(directory)
            (chapters / "01-flat.md").write_text(SPEC, encoding="utf-8")
            analyzer = diagram_report.DiagramAnalyzer(str(chapters))
            analyzer.analyze_all_chapters()

            rendered = diagram_report.ReportGenerator(analyzer.elements).generate_html()

            self.assertIn("Decision &lt;Boundary&gt;", rendered)
            self.assertNotIn("<td>Decision <Boundary></td>", rendered)

    def test_legacy_command_delegates_to_the_canonical_script(self):
        result = subprocess.run(
            [sys.executable, str(COMPATIBILITY_SCRIPT), "--help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--allow-empty", result.stdout)

    def test_published_guides_preserve_the_evidence_boundary(self):
        route = (ROOT / "skills/microsim-utils/SKILL.md").read_text(encoding="utf-8")
        guide = (ROOT / "skills/microsim-utils/references/diagram-reports.md").read_text(
            encoding="utf-8"
        )
        installer = (
            ROOT / "skills/book-installer/references/supplementary-content-generator.md"
        ).read_text(encoding="utf-8")

        self.assertIn("not rendered figures, images, iframes", route)
        self.assertIn("Do not use it as a publication-quality gate", guide)
        self.assertIn("Do not copy it into the textbook", guide)
        self.assertIn("Run this optional step only", installer)
        self.assertNotIn(
            "This script audits all MicroSims and diagrams in the project", installer
        )


if __name__ == "__main__":
    unittest.main()
