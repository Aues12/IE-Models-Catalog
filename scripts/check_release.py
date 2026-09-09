"""Check the repository's stable SemVer release metadata, optionally a Git tag."""

import argparse
import datetime
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"


def check_release(root: Path, tag: str | None = None) -> str:
    version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
    if not re.fullmatch(VERSION, version):
        raise ValueError(
            "Package version must be a stable SemVer X.Y.Z without leading zeros."
        )
    changelog = (root / "CHANGELOG.md").read_text()
    headings = re.findall(r"^## (.+)$", changelog, re.MULTILINE)
    if not headings or headings[0] != "Unreleased":
        raise ValueError("Changelog must start with an Unreleased section.")
    releases = []
    for heading in headings[1:]:
        match = re.fullmatch(rf"\[({VERSION})\] - (\d{{4}}-\d{{2}}-\d{{2}})", heading)
        if not match:
            raise ValueError(f"Invalid release heading: {heading}")
        datetime.date.fromisoformat(match[2])
        releases.append(match[1])
    if not releases or releases[0] != version:
        raise ValueError("Newest changelog release must match package version.")
    numbers = [tuple(map(int, value.split("."))) for value in releases]
    if any(a <= b for a, b in zip(numbers, numbers[1:])):
        raise ValueError("Changelog versions must be unique and strictly descending.")
    section = changelog.split(f"## [{version}]", 1)[1].split("\n## ", 1)[0]
    if not re.search(r"^[*-] \S", section, re.MULTILINE):
        raise ValueError("Current release must contain change notes.")
    if tag is not None:
        if tag != f"v{version}":
            raise ValueError("Tag must equal v plus the package version.")
        tagged = subprocess.check_output(
            ["git", "rev-parse", f"refs/tags/{tag}^{{commit}}"], cwd=root, text=True
        ).strip()
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        if tagged != head:
            raise ValueError("Release tag must point to HEAD.")
        kind = subprocess.check_output(
            ["git", "cat-file", "-t", f"refs/tags/{tag}"], cwd=root, text=True
        ).strip()
        if kind != "tag":
            raise ValueError("Release tag must be annotated.")
        unreleased = changelog.split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        if re.search(r"^[*-] \S", unreleased, re.MULTILINE):
            raise ValueError("Move pending Unreleased entries into the tagged release.")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tag", help="Existing annotated release tag to verify against HEAD"
    )
    args = parser.parse_args()
    try:
        version = check_release(ROOT, args.tag)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Release check failed: {exc}\n")
    print(
        f"Release metadata is consistent: {version}"
        + (f" ({args.tag})" if args.tag else "")
    )


if __name__ == "__main__":
    main()
