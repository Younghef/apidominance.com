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
