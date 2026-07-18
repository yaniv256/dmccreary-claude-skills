from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_skill_license_contract import (
    CANONICAL_LICENSE,
    creative_commons_mismatches,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SkillLicenseContractTests(unittest.TestCase):
    def write_skill(self, root: Path, license_value: str) -> Path:
        path = root / "skills" / "fixture" / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            f"---\nname: fixture\ndescription: Fixture skill.\nlicense: {license_value}\n---\n",
            encoding="utf-8",
        )
        return path

    def test_repository_creative_commons_metadata_is_canonical(self):
        self.assertEqual([], creative_commons_mismatches(REPOSITORY_ROOT))

    def test_repository_authority_names_sharealike_and_links_the_deed(self):
        expected_markers = {
            "README.md": (
                "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License",
                "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            ),
            "docs/license.md": (
                "Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0 DEED)",
                "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en",
            ),
            "docs/chapters/16-user-global-claude/index.md": (
                "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)",
            ),
        }
        for relative_path, markers in expected_markers.items():
            text = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                for marker in markers:
                    self.assertIn(marker, text)

    def test_plain_by_nc_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            value = "Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)"
            path = self.write_skill(root, value)
            self.assertEqual([(path, value)], creative_commons_mismatches(root))

    def test_hybrid_long_name_and_sharealike_abbreviation_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_skill(
                root,
                "Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC-SA 4.0)",
            )
            mismatches = creative_commons_mismatches(root)
            self.assertEqual([path], [mismatch_path for mismatch_path, _ in mismatches])

    def test_lowercase_skill_filename_is_not_skipped(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_skill(
                root,
                "Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)",
            )
            lowercase_path = path.with_name("skill.md")
            path.rename(lowercase_path)
            self.assertEqual(
                [lowercase_path],
                [mismatch_path for mismatch_path, _ in creative_commons_mismatches(root)],
            )

    def test_exact_canonical_value_is_accepted(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_skill(root, CANONICAL_LICENSE)
            self.assertEqual([], creative_commons_mismatches(root))


if __name__ == "__main__":
    unittest.main()
