import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).resolve().parents[1] / "validate-sims.py"


class ValidateSimsDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.sims_dir = self.project_dir / "docs" / "sims"
        self.sims_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_validator(self, *args):
        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--project-dir",
                str(self.project_dir),
                "--format",
                "json",
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_batch_discovery_excludes_support_only_directories(self):
        main_only = self.sims_dir / "main-only"
        main_only.mkdir()
        (main_only / "main.html").write_text("<main></main>", encoding="utf-8")

        index_only = self.sims_dir / "index-only"
        index_only.mkdir()
        (index_only / "index.md").write_text("# Incomplete sim\n", encoding="utf-8")

        metadata_only = self.sims_dir / "metadata-only"
        metadata_only.mkdir()
        (metadata_only / "metadata.json").write_text("{}\n", encoding="utf-8")

        support = self.sims_dir / "shared"
        support.mkdir()
        (support / "microsim.css").write_text("/* shared */\n", encoding="utf-8")
        (support / "microsim.js").write_text("// shared\n", encoding="utf-8")

        results = self.run_validator()

        self.assertEqual(
            [result["sim_id"] for result in results],
            ["index-only", "main-only", "metadata-only"],
        )

    def test_explicit_sim_still_validates_a_support_directory(self):
        support = self.sims_dir / "shared"
        support.mkdir()
        (support / "microsim.js").write_text("// shared\n", encoding="utf-8")

        results = self.run_validator("--sim", "shared")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["sim_id"], "shared")
        self.assertIn("main.html missing", results[0]["issues"])


if __name__ == "__main__":
    unittest.main()
