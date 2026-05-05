# apidominance.com

Marketing site for API Dominance, hosted on Vercel.

## Local development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/render.py
python -m http.server -d dist 8000
# Open http://localhost:8000
```

## Adding a new page

A page is a set of files in `content/`:

- `<slug>.md` — frontmatter (hero, features, params, etc.)
- `<slug>.pricing.yaml` — pricing tiers
- `<slug>.candidate.json` — id, title, marketplace links
- `<slug>.openapi.json` *(optional)* — used as fallback for params + response example when frontmatter omits them

Push a PR. Vercel renders a preview URL on the PR. Merge → live at `apidominance.com/<slug>.html`.

## Architecture

See `https://github.com/Younghef/api_dominance/blob/main/docs/superpowers/specs/2026-05-04-marketing-site-extraction-design.md`.
