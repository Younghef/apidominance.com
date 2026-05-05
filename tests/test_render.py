"""Tests for scripts/render.py — frontmatter parsing, validation, rendering."""

import json
import shutil
from pathlib import Path

import pytest

# Allow `scripts/` to be importable
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import render


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_frontmatter_returns_dict_and_body():
    text = (FIXTURES / "content" / "sample.md").read_text(encoding="utf-8")
    fm, body = render.parse_frontmatter(text)
    assert fm["title"] == "Sample API"
    assert fm["slug"] == "sample"
    assert fm["accent"]["primary"] == "#2563eb"
    assert "# Sample API" in body


def test_parse_frontmatter_rejects_no_opening_delimiter():
    with pytest.raises(ValueError, match="frontmatter"):
        render.parse_frontmatter("title: foo\n---\nbody")


def test_parse_frontmatter_rejects_unclosed_frontmatter():
    with pytest.raises(ValueError, match="closed"):
        render.parse_frontmatter("---\ntitle: foo\nbody")


def test_validate_frontmatter_passes_with_all_keys():
    text = (FIXTURES / "content" / "sample.md").read_text(encoding="utf-8")
    fm, _ = render.parse_frontmatter(text)
    render.validate_frontmatter(fm, expected_slug="sample")  # no exception


def test_validate_frontmatter_rejects_missing_required_keys():
    fm = {"title": "X", "slug": "x"}
    with pytest.raises(ValueError, match="missing keys"):
        render.validate_frontmatter(fm, expected_slug="x")


def test_validate_frontmatter_rejects_slug_mismatch():
    text = (FIXTURES / "content" / "sample.md").read_text(encoding="utf-8")
    fm, _ = render.parse_frontmatter(text)
    with pytest.raises(ValueError, match="does not match filename"):
        render.validate_frontmatter(fm, expected_slug="other")


def test_extract_params_from_openapi():
    spec = json.loads((FIXTURES / "content" / "sample.openapi.json").read_text())
    params = render.extract_params(spec)
    assert params == [
        {"name": "query", "type": "string", "description": "Search query", "required": True},
        {"name": "limit", "type": "integer", "description": "Max results", "required": False},
    ]


def test_extract_response_example_from_openapi():
    spec = json.loads((FIXTURES / "content" / "sample.openapi.json").read_text())
    out = render.extract_response_example(spec)
    parsed = json.loads(out)
    assert parsed == {"results": [{"id": 1, "name": "Item"}], "total": 1}


def test_extract_params_with_no_paths():
    assert render.extract_params({"openapi": "3.0.0", "paths": {}}) == []


def test_extract_response_example_with_no_example():
    spec = {"paths": {"/x": {"get": {"responses": {"200": {"description": "x", "content": {}}}}}}}
    assert render.extract_response_example(spec) == ""


def test_render_page_writes_html(tmp_path):
    content_dir = FIXTURES / "content"
    templates_dir = FIXTURES / "_templates"
    output = render.render_page(
        slug="sample",
        content_dir=content_dir,
        templates_dir=templates_dir,
        output_dir=tmp_path,
    )
    assert output == tmp_path / "sample.html"
    html = output.read_text(encoding="utf-8")
    assert "Sample API | API Dominance" in html
    assert "Real-Time Sample Data via API" in html


def test_render_page_uses_openapi_fallback_for_params(tmp_path):
    content_dir = FIXTURES / "content"
    templates_dir = FIXTURES / "_templates"
    output = render.render_page(
        slug="sample",
        content_dir=content_dir,
        templates_dir=templates_dir,
        output_dir=tmp_path,
    )
    html = output.read_text(encoding="utf-8")
    # sample.md sets params: [], so render.py derives from sample.openapi.json
    assert "query" in html
    assert "limit" in html


def test_render_page_uses_openapi_fallback_for_response(tmp_path):
    content_dir = FIXTURES / "content"
    templates_dir = FIXTURES / "_templates"
    output = render.render_page(
        slug="sample",
        content_dir=content_dir,
        templates_dir=templates_dir,
        output_dir=tmp_path,
    )
    html = output.read_text(encoding="utf-8")
    # sample.md sets response.example_json: "", so render.py derives from openapi.json
    assert "Item" in html


def test_render_index_writes_html(tmp_path):
    content_dir = FIXTURES / "content"
    templates_dir = FIXTURES / "_templates"
    output = render.render_index(
        content_dir=content_dir,
        templates_dir=templates_dir,
        output_dir=tmp_path,
        candidate_slugs=["sample", "another"],
    )
    assert output == tmp_path / "index.html"
    html = output.read_text(encoding="utf-8")
    assert "API Dominance — High-Performance APIs" in html
    assert "sample" in html
    assert "another" in html
