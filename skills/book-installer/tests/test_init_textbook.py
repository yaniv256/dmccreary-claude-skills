import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "init_textbook.py"
TEMPLATE_ROOT = Path(__file__).parents[1] / "assets" / "init-textbook"
SPEC = importlib.util.spec_from_file_location("init_textbook", SCRIPT_PATH)
init_textbook = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = init_textbook
SPEC.loader.exec_module(init_textbook)


def arguments(project: Path, **overrides):
    values = {
        "project_dir": project,
        "site_name": "Builder's Guide & Atlas",
        "site_description": "A practical guide to agents, evidence & tests.",
        "site_author": "Yaniv Ben-Ami",
        "github_username": "yaniv256",
        "repo_name": "builder-atlas",
        "linkedin_url": "https://www.linkedin.com/in/yaniv-ben-ami-9208b9184/",
        "primary_color": "deep orange",
        "accent_color": "blue",
        "year": "2026",
    }
    values.update(overrides)
    return init_textbook.argparse.Namespace(**values)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class InitTextbookTests(unittest.TestCase):
    def test_scaffold_copies_hidden_and_binary_assets_and_escapes_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            config = init_textbook.build_config(
                arguments(project, site_author="Yaniv O'Ben-Ami")
            )

            paths = init_textbook.scaffold(config)

            self.assertIn(project / ".gitignore", paths)
            self.assertTrue((project / ".gitignore").is_file())
            self.assertTrue((project / "builder-atlas.code-workspace").is_file())
            self.assertTrue((project / "docs" / "js").is_dir())
            self.assertEqual(
                (project / "docs" / "img" / "cover.png").read_bytes(),
                (TEMPLATE_ROOT / "docs" / "img" / "cover.png").read_bytes(),
            )
            mkdocs = (project / "mkdocs.yml").read_text(encoding="utf-8")
            index = (project / "docs" / "index.md").read_text(encoding="utf-8")
            self.assertIn("site_name: 'Builder''s Guide & Atlas'", mkdocs)
            self.assertIn("site_author: 'Yaniv O''Ben-Ami'", mkdocs)
            self.assertIn("2026 Yaniv O''Ben-Ami. Licensed", mkdocs)
            self.assertIn("title: 'Builder''s Guide & Atlas'", index)
            self.assertIn("edit_uri: 'edit/main/docs/'", mkdocs)
            self.assertNotRegex(
                "\n".join(
                    path.read_text(encoding="utf-8")
                    for path in project.rglob("*")
                    if path.is_file() and init_textbook.is_text_template(path)
                ),
                init_textbook.TOKEN_PATTERN,
            )

    def test_collision_fails_before_any_output_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            existing = project / ".gitignore"
            existing.write_text("keep-me\n", encoding="utf-8")
            before = tree_digest(project)
            config = init_textbook.build_config(arguments(project))

            with self.assertRaisesRegex(init_textbook.ScaffoldError, "refusing to overwrite"):
                init_textbook.scaffold(config)

            self.assertEqual(tree_digest(project), before)
            self.assertFalse((project / "mkdocs.yml").exists())

    def test_dry_run_validates_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            config = init_textbook.build_config(arguments(project))

            paths = init_textbook.scaffold(config, dry_run=True)

            self.assertGreater(len(paths), 10)
            self.assertEqual(list(project.iterdir()), [])

    def test_write_failure_rolls_back_files_and_created_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            config = init_textbook.build_config(arguments(project))
            real_link = os.link
            calls = 0

            def fail_second_link(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected write failure")
                return real_link(source, destination)

            with mock.patch.object(init_textbook.os, "link", side_effect=fail_second_link):
                with self.assertRaisesRegex(OSError, "injected write failure"):
                    init_textbook.scaffold(config)

            self.assertEqual(list(project.iterdir()), [])

    def test_commit_does_not_overwrite_destination_created_after_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            config = init_textbook.build_config(arguments(project))
            init_textbook.preflight(config)

            with tempfile.TemporaryDirectory(dir=project.parent) as stage_dir:
                stage = Path(stage_dir)
                relative_paths = init_textbook.render_stage(config, stage)
                raced_destination = project / ".gitignore"
                raced_destination.write_text("created concurrently\n", encoding="utf-8")

                with self.assertRaises(FileExistsError):
                    init_textbook.commit_stage(config, stage, relative_paths)

            self.assertEqual(
                raced_destination.read_text(encoding="utf-8"),
                "created concurrently\n",
            )
            self.assertEqual([path.name for path in project.iterdir()], [".gitignore"])

    def test_invalid_metadata_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)

            with self.assertRaisesRegex(init_textbook.ScaffoldError, "single line"):
                init_textbook.build_config(
                    arguments(project, site_description="first line\nsecond line")
                )

            self.assertEqual(list(project.iterdir()), [])

    def test_help_is_non_mutating(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--help"],
                cwd=project,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--dry-run", result.stdout)
            self.assertEqual(list(project.iterdir()), [])

    def test_template_comment_matches_explicit_image_only_hook(self):
        mkdocs = (TEMPLATE_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        hook = (TEMPLATE_ROOT / "plugins" / "social_override.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("overrides og:image and twitter:image only when", mkdocs)
        self.assertIn("a page explicitly declares `image:`", mkdocs)
        self.assertIn('if not image:\n        return html', hook)
        self.assertNotIn("falling back to the site-", mkdocs)


if __name__ == "__main__":
    unittest.main()
