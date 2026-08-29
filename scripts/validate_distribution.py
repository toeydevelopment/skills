#!/usr/bin/env python3
"""Validate cross-agent skill and plugin distribution metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "toeydevelopment-skills"
SKILLS_DIR = PLUGIN_ROOT / "skills"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
LINK = re.compile(r"\[[^]]*]\(([^)]+)\)")


class ValidationError(Exception):
    pass


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing {relative_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{relative_path} must contain a JSON object")
    return value


def frontmatter_name(skill_file: Path) -> str:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValidationError(f"{skill_file.relative_to(ROOT)} has no YAML frontmatter")
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    raise ValidationError(f"{skill_file.relative_to(ROOT)} has no frontmatter name")


def skill_names() -> list[str]:
    if not SKILLS_DIR.is_dir():
        raise ValidationError("missing plugins/toeydevelopment-skills/skills/ directory")
    names: list[str] = []
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        directory_name = skill_file.parent.name
        declared_name = frontmatter_name(skill_file)
        if declared_name != directory_name:
            raise ValidationError(
                f"{skill_file.relative_to(ROOT)} declares {declared_name!r}, "
                f"expected {directory_name!r}"
            )
        names.append(directory_name)
    if not names:
        raise ValidationError("plugin skills directory contains no <name>/SKILL.md files")
    if len(names) != len(set(names)):
        raise ValidationError("duplicate skill names found")
    return names


def validate_links() -> None:
    for markdown in sorted(SKILLS_DIR.glob("**/*.md")):
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LINK.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("#", "/", "mailto:")):
                continue
            resolved = (markdown.parent / target).resolve()
            if ROOT not in resolved.parents and resolved != ROOT:
                raise ValidationError(
                    f"{markdown.relative_to(ROOT)} links outside the repository: {raw_target}"
                )
            if not resolved.exists():
                raise ValidationError(
                    f"{markdown.relative_to(ROOT)} has missing link target: {raw_target}"
                )


def validate_manifests(names: list[str]) -> None:
    codex = load_json("plugins/toeydevelopment-skills/.codex-plugin/plugin.json")
    claude = load_json("plugins/toeydevelopment-skills/.claude-plugin/plugin.json")
    codex_market = load_json(".agents/plugins/marketplace.json")
    claude_market = load_json(".claude-plugin/marketplace.json")

    bundle_name = codex.get("name")
    if not isinstance(bundle_name, str) or not bundle_name:
        raise ValidationError("Codex plugin manifest needs a non-empty name")
    if claude.get("name") != bundle_name:
        raise ValidationError("Codex and Claude plugin names must match")
    if claude.get("version") != codex.get("version"):
        raise ValidationError("Codex and Claude plugin versions must match")
    if codex_market.get("name") != bundle_name or claude_market.get("name") != bundle_name:
        raise ValidationError("both marketplace names must match the bundle name")

    for label, manifest in (("Codex", codex), ("Claude", claude)):
        version = manifest.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            raise ValidationError(f"{label} plugin version is not valid semver")
        if manifest.get("skills") != "./skills/":
            raise ValidationError(f"{label} plugin must load ./skills/")

    codex_entries = codex_market.get("plugins")
    if not isinstance(codex_entries, list) or len(codex_entries) != 1:
        raise ValidationError("Codex marketplace must expose exactly one bundle entry")
    codex_entry = codex_entries[0]
    if codex_entry.get("name") != bundle_name:
        raise ValidationError("Codex marketplace bundle name does not match manifest")
    if codex_entry.get("source") != {
        "source": "local",
        "path": "./plugins/toeydevelopment-skills",
    }:
        raise ValidationError("Codex marketplace bundle must point at the plugin directory")
    if codex_entry.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        raise ValidationError("Codex marketplace policy is incomplete")
    if not codex_entry.get("category"):
        raise ValidationError("Codex marketplace bundle needs a category")

    claude_entries = claude_market.get("plugins")
    if not isinstance(claude_entries, list):
        raise ValidationError("Claude marketplace plugins must be an array")
    by_name = {
        entry.get("name"): entry
        for entry in claude_entries
        if isinstance(entry, dict) and isinstance(entry.get("name"), str)
    }
    expected = set(names) | {bundle_name}
    missing = sorted(expected - set(by_name))
    if missing:
        raise ValidationError(f"Claude marketplace is missing: {', '.join(missing)}")
    expected_bundle_source = {
        "source": "github",
        "repo": "toeydevelopment/skills",
        "path": "plugins/toeydevelopment-skills",
    }
    if by_name[bundle_name].get("source") != expected_bundle_source:
        raise ValidationError("Claude marketplace bundle source is wrong")
    for name in names:
        individual = load_json(
            f"plugins/toeydevelopment-skills/skills/{name}/.claude-plugin/plugin.json"
        )
        if individual.get("name") != name:
            raise ValidationError(f"Claude plugin manifest name is wrong for {name}")
        if individual.get("version") != claude.get("version"):
            raise ValidationError(f"Claude plugin version is out of sync for {name}")
        source = by_name[name].get("source")
        expected_source = {
            "source": "github",
            "repo": "toeydevelopment/skills",
            "path": f"plugins/toeydevelopment-skills/skills/{name}",
        }
        if source != expected_source:
            raise ValidationError(f"Claude marketplace source is wrong for {name}")


def main() -> int:
    try:
        names = skill_names()
        validate_links()
        validate_manifests(names)
    except ValidationError as exc:
        print(f"distribution validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"distribution valid: {len(names)} skills, Codex bundle, Claude bundle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
