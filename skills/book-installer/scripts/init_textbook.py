#!/usr/bin/env python3
"""Create the canonical intelligent-textbook scaffold without overwrites."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


TEMPLATE_ROOT = Path(__file__).parents[1] / "assets" / "init-textbook"
TOKEN_PATTERN = re.compile(r"\{\{([A-Z_]+)\}\}")
GITHUB_USERNAME_PATTERN = re.compile(
    r"(?!.*--)[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?"
)
REPO_NAME_PATTERN = re.compile(r"[A-Za-z0-9._-]+")
BINARY_TEMPLATES = {
    Path("docs/img/cover.png"),
    Path("docs/img/license.png"),
}
SAFE_DIR_FD_SUPPORTED = (
    hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and all(
        function in os.supports_dir_fd
        for function in (os.open, os.mkdir, os.stat, os.unlink, os.rmdir)
    )
)
EMPTY_DIRECTORIES = (Path("docs/js"),)
REQUIRED_TEMPLATES = {
    Path(".gitignore"),
    Path("docs/about.md"),
    Path("docs/chapters/index.md"),
    Path("docs/contact.md"),
    Path("docs/course-description.md"),
    Path("docs/css/extra.css"),
    Path("docs/img/cover.png"),
    Path("docs/img/license.png"),
    Path("docs/index.md"),
    Path("docs/learning-graph/index.md"),
    Path("docs/license.md"),
    Path("docs/sims/index.md"),
    Path("mkdocs.yml"),
    Path("plugins/social_override.py"),
    Path("project.code-workspace"),
}


class ScaffoldError(ValueError):
    """Raised when validation or safe scaffold publication cannot complete."""


@dataclass(frozen=True)
class ScaffoldConfig:
    project_dir: Path
    site_name: str
    site_description: str
    site_author: str
    github_username: str
    repo_name: str
    linkedin_url: str
    primary_color: str
    accent_color: str
    year: str

    @property
    def values(self) -> dict[str, str]:
        return {
            "SITE_NAME": self.site_name,
            "SITE_DESCRIPTION": self.site_description,
            "SITE_AUTHOR": self.site_author,
            "GITHUB_USERNAME": self.github_username,
            "REPO_NAME": self.repo_name,
            "LINKEDIN_URL": self.linkedin_url,
            "PRIMARY_COLOR": self.primary_color,
            "ACCENT_COLOR": self.accent_color,
            "YEAR": self.year,
        }


def one_line(name: str, value: str) -> str:
    value = value.strip()
    if not value:
        raise ScaffoldError(f"{name} must not be empty")
    if any(character in value for character in ("\n", "\r", "\x00")):
        raise ScaffoldError(f"{name} must be a single line")
    return value


def validate_url(name: str, value: str) -> str:
    value = one_line(name, value)
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ScaffoldError(f"{name} must be an absolute http(s) URL")
    return value


def build_config(args: argparse.Namespace) -> ScaffoldConfig:
    requested_project_dir = args.project_dir.expanduser()
    if requested_project_dir.is_symlink():
        raise ScaffoldError("project-dir must not be a symbolic link")
    project_dir = requested_project_dir.resolve()
    if not project_dir.exists() or not project_dir.is_dir():
        raise ScaffoldError("project-dir must be an existing directory")

    github_username = one_line("github-username", args.github_username)
    if not GITHUB_USERNAME_PATTERN.fullmatch(github_username):
        raise ScaffoldError("github-username is not a valid GitHub account name")

    repo_name = one_line("repo-name", args.repo_name or project_dir.name)
    if repo_name in {".", ".."} or not REPO_NAME_PATTERN.fullmatch(repo_name):
        raise ScaffoldError(
            "repo-name must be more than dots and may contain only letters, "
            "numbers, '.', '_', and '-'"
        )

    year = one_line("year", args.year)
    if not re.fullmatch(r"\d{4}", year):
        raise ScaffoldError("year must contain exactly four digits")

    return ScaffoldConfig(
        project_dir=project_dir,
        site_name=one_line("site-name", args.site_name),
        site_description=one_line("site-description", args.site_description),
        site_author=one_line("site-author", args.site_author),
        github_username=github_username,
        repo_name=repo_name,
        linkedin_url=validate_url("linkedin-url", args.linkedin_url),
        primary_color=one_line("primary-color", args.primary_color),
        accent_color=one_line("accent-color", args.accent_color),
        year=year,
    )


def destination_relative_path(source: Path, config: ScaffoldConfig) -> Path:
    relative = source.relative_to(TEMPLATE_ROOT)
    if relative == Path("project.code-workspace"):
        return Path(f"{config.repo_name}.code-workspace")
    return relative


def template_files() -> list[Path]:
    if not TEMPLATE_ROOT.is_dir():
        raise ScaffoldError(f"template root is missing: {TEMPLATE_ROOT}")
    files = sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())
    present = {path.relative_to(TEMPLATE_ROOT) for path in files}
    missing = sorted(REQUIRED_TEMPLATES - present)
    if missing:
        raise ScaffoldError(
            "canonical template is incomplete: " + ", ".join(map(str, missing))
        )
    return files


def render_yaml_scalars(text: str, values: dict[str, str]) -> str:
    # Escape substitutions anywhere inside a single-quoted YAML scalar. This
    # covers both scalar-only tokens and interpolated values such as copyright.
    rendered_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        match = re.match(r"^(\s*[^#\n][^:\n]*:\s*)'(.*)'(\s*(?:#.*)?)(\r?\n)?$", line)
        if match:
            prefix, scalar, suffix, newline = match.groups()
            for key, value in values.items():
                scalar = scalar.replace(f"{{{{{key}}}}}", value.replace("'", "''"))
            line = f"{prefix}'{scalar}'{suffix}{newline or ''}"
        rendered_lines.append(line)
    return "".join(rendered_lines)


def render_text(
    text: str,
    values: dict[str, str],
    *,
    yaml: bool = False,
    markdown_frontmatter: bool = False,
) -> str:
    if yaml:
        text = render_yaml_scalars(text, values)
    elif markdown_frontmatter and text.startswith("---"):
        match = re.match(r"\A(---\r?\n)(.*?)(\r?\n---(?:\r?\n|\Z))", text, re.DOTALL)
        if match:
            text = (
                match.group(1)
                + render_yaml_scalars(match.group(2), values)
                + match.group(3)
                + text[match.end() :]
            )

    # The same tokens can also appear as ordinary Markdown or Python text.
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def planned_destinations(config: ScaffoldConfig) -> list[Path]:
    files = [
        config.project_dir / destination_relative_path(source, config)
        for source in template_files()
    ]
    directories = [config.project_dir / relative for relative in EMPTY_DIRECTORIES]
    return files + directories


def preflight(config: ScaffoldConfig) -> list[Path]:
    destinations = planned_destinations(config)
    collisions = [path for path in destinations if path.exists() or path.is_symlink()]

    unsafe_parents: set[Path] = set()
    for destination in destinations:
        parent = destination.parent
        while parent != config.project_dir:
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                unsafe_parents.add(parent)
            parent = parent.parent

    if collisions or unsafe_parents:
        paths = sorted({*collisions, *unsafe_parents})
        rendered = "\n".join(f"  - {path}" for path in paths)
        raise ScaffoldError(f"refusing to overwrite or traverse existing output paths:\n{rendered}")
    return destinations


def render_stage(config: ScaffoldConfig, stage: Path) -> list[Path]:
    rendered_paths: list[Path] = []
    for source in template_files():
        source_relative = source.relative_to(TEMPLATE_ROOT)
        relative = destination_relative_path(source, config)
        destination = stage / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source_relative in BINARY_TEMPLATES:
            shutil.copyfile(source, destination)
        else:
            try:
                text = source.read_text(encoding="utf-8")
            except UnicodeDecodeError as error:
                raise ScaffoldError(
                    f"nonbinary template is not valid UTF-8: {source_relative}"
                ) from error
            rendered = render_text(
                text,
                config.values,
                yaml=source.suffix in {".yml", ".yaml"},
                markdown_frontmatter=source.suffix == ".md",
            )
            unresolved = sorted(set(TOKEN_PATTERN.findall(rendered)))
            if unresolved:
                raise ScaffoldError(
                    f"unresolved placeholders in {relative}: {', '.join(unresolved)}"
                )
            destination.write_text(rendered, encoding="utf-8")
        rendered_paths.append(relative)
    for relative in EMPTY_DIRECTORIES:
        (stage / relative).mkdir(parents=True, exist_ok=False)
    return rendered_paths


def commit_stage(config: ScaffoldConfig, stage: Path, relative_paths: list[Path]) -> None:
    if not SAFE_DIR_FD_SUPPORTED:
        raise ScaffoldError(
            "safe publication requires directory-relative, no-follow filesystem support"
        )

    def identity(stat_result: os.stat_result) -> tuple[int, int]:
        return (stat_result.st_dev, stat_result.st_ino)

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        root_fd = os.open(config.project_dir, directory_flags)
    except OSError as error:
        raise ScaffoldError(f"could not open project directory safely: {error}") from error

    root_identity = identity(os.fstat(root_fd))
    directory_fds: dict[Path, int] = {Path("."): root_fd}
    directory_identities: dict[Path, tuple[int, int]] = {
        Path("."): root_identity
    }
    written: list[tuple[int, str, tuple[int, int]]] = []
    created_directories: list[tuple[int, str, tuple[int, int]]] = []

    def open_directory(relative: Path) -> int:
        relative = Path(".") if not relative.parts else relative
        if relative in directory_fds:
            return directory_fds[relative]

        current_relative = Path(".")
        current_fd = root_fd
        for part in relative.parts:
            next_relative = Path(part) if current_relative == Path(".") else current_relative / part
            if next_relative in directory_fds:
                current_relative = next_relative
                current_fd = directory_fds[next_relative]
                continue

            created_identity: tuple[int, int] | None = None
            try:
                os.mkdir(part, dir_fd=current_fd)
            except FileExistsError:
                pass
            else:
                created_stat = os.stat(
                    part, dir_fd=current_fd, follow_symlinks=False
                )
                created_identity = identity(created_stat)
                created_directories.append(
                    (current_fd, part, created_identity)
                )

            try:
                next_fd = os.open(part, directory_flags, dir_fd=current_fd)
            except OSError as error:
                raise ScaffoldError(
                    f"unsafe output directory appeared during write: {next_relative}"
                ) from error
            next_identity = identity(os.fstat(next_fd))
            if created_identity is not None and next_identity != created_identity:
                os.close(next_fd)
                raise ScaffoldError(
                    f"output directory changed while being created: {next_relative}"
                )
            directory_fds[next_relative] = next_fd
            directory_identities[next_relative] = next_identity
            current_relative = next_relative
            current_fd = next_fd
        return current_fd

    def verify_published_paths() -> None:
        try:
            current_root = config.project_dir.lstat()
        except FileNotFoundError as error:
            raise ScaffoldError("project directory disappeared during write") from error
        if config.project_dir.is_symlink() or identity(current_root) != root_identity:
            raise ScaffoldError("project directory changed during write")

        for relative, expected in directory_identities.items():
            if relative == Path("."):
                continue
            current_fd = root_fd
            opened: list[int] = []
            try:
                for part in relative.parts:
                    current_fd = os.open(
                        part, directory_flags, dir_fd=current_fd
                    )
                    opened.append(current_fd)
                if identity(os.fstat(current_fd)) != expected:
                    raise ScaffoldError(
                        f"output directory changed during write: {relative}"
                    )
            except OSError as error:
                raise ScaffoldError(
                    f"output directory became unsafe during write: {relative}"
                ) from error
            finally:
                for fd in reversed(opened):
                    os.close(fd)

        for parent_fd, name, expected in written:
            try:
                current = os.stat(
                    name, dir_fd=parent_fd, follow_symlinks=False
                )
            except FileNotFoundError as error:
                raise ScaffoldError(
                    f"output file disappeared during write: {name}"
                ) from error
            if identity(current) != expected:
                raise ScaffoldError(f"output file changed during write: {name}")

    failure: Exception | None = None
    try:
        for relative in relative_paths:
            source = stage / relative
            parent_fd = open_directory(relative.parent)
            fd = os.open(
                relative.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                source.stat().st_mode & 0o777,
                dir_fd=parent_fd,
            )
            created = os.fstat(fd)
            written.append((parent_fd, relative.name, identity(created)))
            try:
                output = os.fdopen(fd, "wb")
            except Exception:
                os.close(fd)
                raise
            with source.open("rb") as input_file, output:
                shutil.copyfileobj(input_file, output)
        for relative in EMPTY_DIRECTORIES:
            open_directory(relative)
        verify_published_paths()
    except Exception as error:
        failure = error
        for parent_fd, name, expected in reversed(written):
            try:
                current = os.stat(
                    name, dir_fd=parent_fd, follow_symlinks=False
                )
            except FileNotFoundError:
                continue
            if identity(current) == expected:
                os.unlink(name, dir_fd=parent_fd)
        for parent_fd, name, expected in reversed(created_directories):
            try:
                current = os.stat(
                    name, dir_fd=parent_fd, follow_symlinks=False
                )
            except FileNotFoundError:
                continue
            if identity(current) != expected:
                continue
            try:
                os.rmdir(name, dir_fd=parent_fd)
            except OSError:
                # Preserve a directory populated concurrently by another actor.
                continue
    finally:
        for relative, fd in reversed(list(directory_fds.items())):
            if relative != Path("."):
                os.close(fd)
        os.close(root_fd)

    if failure is not None:
        if isinstance(failure, ScaffoldError):
            raise failure
        raise ScaffoldError(f"could not publish scaffold safely: {failure}") from failure


def scaffold(config: ScaffoldConfig, dry_run: bool = False) -> list[Path]:
    destinations = preflight(config)
    # A project can be a writable mount inside a read-only parent. For a real
    # write, stage on the project's own filesystem; previews use system temp
    # so the documented non-mutation contract includes the project directory.
    stage_parent = config.project_dir if not dry_run else None
    with tempfile.TemporaryDirectory(
        prefix=".init-textbook-", dir=stage_parent
    ) as directory:
        stage = Path(directory)
        relative_paths = render_stage(config, stage)
        if dry_run:
            return destinations
        # Repeat immediately before the write boundary to catch a race with a
        # cooperating process that created a destination after initial preflight.
        preflight(config)
        commit_stage(config, stage, relative_paths)
    return destinations


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Create a fail-closed intelligent-textbook scaffold."
    )
    command.add_argument("--project-dir", type=Path, required=True)
    command.add_argument("--site-name", required=True)
    command.add_argument("--site-description", required=True)
    command.add_argument("--site-author", required=True)
    command.add_argument("--github-username", required=True)
    command.add_argument("--repo-name")
    command.add_argument(
        "--linkedin-url",
        default="https://www.linkedin.com/in/danmccreary/",
    )
    command.add_argument("--primary-color", default="indigo")
    command.add_argument("--accent-color", default="orange")
    command.add_argument("--year", default=str(dt.date.today().year))
    command.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and collisions, then print outputs without writing.",
    )
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config = build_config(args)
        paths = scaffold(config, dry_run=args.dry_run)
    except ScaffoldError as error:
        print(f"init-textbook: {error}", file=sys.stderr)
        return 2

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(paths)} paths in {config.project_dir}")
    for path in paths:
        print(f"  {path.relative_to(config.project_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
