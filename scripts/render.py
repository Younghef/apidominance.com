"""Build script: render content/*.md into dist/<slug>.html via Jinja2 templates.

Vercel runs this as the build command. Local dev: `python scripts/render.py`.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


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


def _build_context(slug: str, content_dir: Path) -> dict[str, Any]:
    """Read all sibling files for slug and produce a merged Jinja context dict."""
    md_path = content_dir / f"{slug}.md"
    fm, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    validate_frontmatter(fm, expected_slug=slug)

    pricing_path = content_dir / f"{slug}.pricing.yaml"
    pricing = yaml.safe_load(pricing_path.read_text(encoding="utf-8")) if pricing_path.exists() else {}

    candidate_path = content_dir / f"{slug}.candidate.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8")) if candidate_path.exists() else {}

    params = fm.get("params") or []
    response = dict(fm.get("response") or {})
    response.setdefault("description", "")
    response.setdefault("example_json", "")

    openapi_path = content_dir / f"{slug}.openapi.json"
    if openapi_path.exists():
        spec = json.loads(openapi_path.read_text(encoding="utf-8"))
        if not params:
            params = extract_params(spec)
        if not response.get("example_json"):
            response["example_json"] = extract_response_example(spec)

    ctx = dict(fm)
    ctx["params"] = params
    ctx["response"] = response
    ctx["pricing"] = pricing
    ctx["candidate"] = candidate
    ctx["body_md"] = body
    return ctx


def render_page(
    *,
    slug: str,
    content_dir: Path,
    templates_dir: Path,
    output_dir: Path,
    candidate_slugs: list[str] | None = None,
) -> Path:
    """Render content/<slug>.* → output_dir/<slug>.html. Returns the output path."""
    ctx = _build_context(slug, content_dir)
    ctx["candidate_slugs"] = candidate_slugs or []

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        keep_trailing_newline=True,
    )
    tpl = env.get_template("page.html.j2")
    html = tpl.render(**ctx)

    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out


def render_index(
    *,
    content_dir: Path,
    templates_dir: Path,
    output_dir: Path,
    candidate_slugs: list[str],
) -> Path:
    """Render content/_index.md → output_dir/index.html."""
    index_path = content_dir / "_index.md"
    if index_path.exists():
        fm, body = parse_frontmatter(index_path.read_text(encoding="utf-8"))
    else:
        fm, body = {}, ""

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        keep_trailing_newline=True,
    )
    tpl = env.get_template("index.html.j2")
    ctx = dict(fm)
    ctx["candidate_slugs"] = sorted(candidate_slugs)
    ctx["body_md"] = body
    html = tpl.render(**ctx)

    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def main():
    """Entry point — Vercel runs this. Walks content/, renders all pages + index."""
    repo_root = Path(__file__).resolve().parents[1]
    content_dir = repo_root / "content"
    templates_dir = repo_root / "_templates"
    output_dir = repo_root / "dist"

    # Discover slugs from content/*.md (excluding _index.md)
    slug_files = [p for p in sorted(content_dir.glob("*.md")) if p.stem != "_index"]
    slugs = [p.stem for p in slug_files]

    for slug in slugs:
        out = render_page(
            slug=slug,
            content_dir=content_dir,
            templates_dir=templates_dir,
            output_dir=output_dir,
            candidate_slugs=slugs,
        )
        print(f"rendered {out.relative_to(repo_root)}")

    out = render_index(
        content_dir=content_dir,
        templates_dir=templates_dir,
        output_dir=output_dir,
        candidate_slugs=slugs,
    )
    print(f"rendered {out.relative_to(repo_root)}")

    # Copy assets/ → dist/assets/
    assets_src = repo_root / "assets"
    assets_dst = output_dir / "assets"
    if assets_dst.exists():
        shutil.rmtree(assets_dst)
    shutil.copytree(assets_src, assets_dst)
    print(f"copied assets/ -> dist/assets/")


if __name__ == "__main__":
    main()
