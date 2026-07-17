import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
SKILL = (SKILL_DIR / "SKILL.md").read_text()
README = (SKILL_DIR / "README.md").read_text()
ROOT_README = (REPO_ROOT / "README.md").read_text()

LICENSE_NAME = (
    "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
    "International (CC BY-NC-SA 4.0)"
)


def normalized(text):
    return " ".join(text.split())


class FaqDocumentationContractTests(unittest.TestCase):
    def test_current_surfaces_publish_the_repository_license(self):
        self.assertIn(f"license: {LICENSE_NAME}", SKILL)
        self.assertIn(LICENSE_NAME, normalized(README))
        self.assertIn("CC BY-NC-SA 4.0", ROOT_README)
        self.assertNotIn("MIT License", README)

    def test_readme_publishes_the_file_only_link_contract(self):
        self.assertIn("Link to chapter files only", README)
        self.assertIn("never use anchor fragments", README.lower())

        for stale in (
            "Use specific section anchors",
            "glossary.md#learning-graph",
        ):
            self.assertNotIn(stale, README)

    def test_readme_examples_do_not_emit_fragment_links(self):
        markdown_targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", README)
        internal_targets = [
            target
            for target in markdown_targets
            if not target.startswith(("http://", "https://"))
        ]
        self.assertFalse(
            [target for target in internal_targets if "#" in target],
            "README examples must not teach anchor-fragment links",
        )


if __name__ == "__main__":
    unittest.main()
