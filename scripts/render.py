"""Build script: render content/*.md into dist/<slug>.html via Jinja2 templates.

Vercel runs this as the build command. Local dev: `python scripts/render.py`.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FRONTMATTER = {
    "title", "slug", "seo", "accent", "hero", "code_example",
    "features", "use_cases", "response", "cta_section",
}


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split YAML-frontmatter Markdown text into (frontmatter, body)."""
    if not text.startswith("---\n"):
        raise ValueError("file must begin with YAML frontmatter (---)")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed (missing ---)")
    fm_text = text[4:end]
    body = text[end + 5:]
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return fm, body


def validate_frontmatter(fm: dict[str, Any], *, expected_slug: str) -> None:
    """Raise ValueError if frontmatter is missing required keys or slug mismatches."""
    missing = REQUIRED_FRONTMATTER - fm.keys()
    if missing:
        raise ValueError(f"frontmatter missing keys: {sorted(missing)}")
    if fm.get("slug") != expected_slug:
        raise ValueError(
            f"frontmatter slug {fm.get('slug')!r} does not match filename {expected_slug!r}"
        )


def _first_get_op(spec: dict[str, Any]) -> dict[str, Any] | None:
    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        op = methods.get("get") or methods.get("post")
        if op:
            return op
    return None


def extract_params(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Return [{name, type, description, required}] from the first endpoint."""
    op = _first_get_op(spec)
    if not op:
        return []
    out = []
    for p in op.get("parameters") or []:
        out.append({
            "name": p.get("name", ""),
            "type": (p.get("schema") or {}).get("type", "string"),
            "description": p.get("description", ""),
            "required": bool(p.get("required", False)),
        })
    return out


def extract_response_example(spec: dict[str, Any]) -> str:
    """JSON-string example from the first 2xx response of the first endpoint."""
    op = _first_get_op(spec)
    if not op:
        return ""
    for code, resp in (op.get("responses") or {}).items():
        if not str(code).startswith("2"):
            continue
        content = resp.get("content") or {}
        for media, body in content.items():
            ex = body.get("example")
            if ex is not None:
                return json.dumps(ex, indent=2)
            examples = body.get("examples") or {}
            for _, ex_obj in examples.items():
                if "value" in ex_obj:
                    return json.dumps(ex_obj["value"], indent=2)
    return ""


def main():
    """Entry point. Walks content/, renders pages, writes to dist/."""
    raise NotImplementedError("rendering pipeline lands in later tasks")


if __name__ == "__main__":
    main()
