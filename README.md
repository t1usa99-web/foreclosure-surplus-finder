# Surplus Funds Data Engine

County tax-sale and foreclosure **surplus funds** (excess funds / overages), parsed from public county
sources into a normalized dataset and rendered as SEO-optimized, consumer-first county pages.

Data + referral business, not a recovery operation. See `CLAUDE.md` for the hard rules (including: never
use an em dash in user-facing text) and the SEO spec.

## Layout
```
config.py               Domain + brand (swap SITE_URL after registration)
data/coverage_map.csv   County source directory (office, tier, format, provenance)
data/counties/*.json    Parsed records per county (the dataset)
generator/template.py   Renders one county page (record table + JSON-LD + em-dash guard)
generator/build.py      Builds site/ from data/, plus sitemap.xml, robots.txt, homepage
site/                   Generated static output (served by Cloudflare Pages)
```

## Build
```
python generator/build.py     # run from repo root; writes to site/
```

## Stack
- **GitHub** source of truth. **Railway** runs the scheduled harvester (cron) and commits fresh data.
- **Cloudflare Pages** serves `site/`; D1 (records DB), R2 (raw PDF archive), KV (cache) added later.

## Adding a county
1. Add its source row to `data/coverage_map.csv`.
2. Parse it to `data/counties/<slug>.json` (schema mirrors `coweta-county-ga.json`).
3. `python generator/build.py`.

## Status
Phase 1: Georgia. Proof county live: Coweta (Tier 1, direct PDF, 36 records).
