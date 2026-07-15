# Project conventions (surplus funds data engine)

This file is auto-loaded by Claude Code / Cowork sessions working in this repo. Follow it.

## Hard rules

1. **Never use an em dash (—) in any user-facing text.** Pages, meta descriptions, copy, emails, anything a visitor or customer sees. Use commas, colons, parentheses, or reword. The page generator enforces this with `assert "—" not in html`; keep that guard in every generator.
2. **Honest, non-scammy framing.** Consumer copy always leads with "you can claim this yourself, for free, directly from the county." Recovery/attorney referral is offered as optional help, never as required.
3. **Data + referral only.** We do not file claims, represent claimants, or collect debts. No scoring or rating of named individuals (FCRA risk).
4. **Referral monetization is state-gated.** Flag any per-state finder-fee / locator-licensing question for legal review before turning on referral revenue. Prefer flat per-lead pricing over revenue-share.
5. **Provenance on every record.** source_url, source_format, scraped_at. Never publish a record we can't trace to a county source.

## SEO spec for county pages (must beat SurplusFundsList's template)

- Full head tags: title, meta description (with live figures), canonical, OpenGraph, Twitter card, robots, viewport.
- One H1, logical H2/H3 hierarchy.
- Real parsed records rendered on-page (searchable), not just a link to the county file. This is the differentiator.
- JSON-LD: BreadcrumbList + Dataset + FAQPage.
- "Last updated" freshness stamp fed by the harvester.
- Consumer-first above the fold; operator/affiliate CTA below, tagged rel="nofollow sponsored".
- County-accurate claim steps and statute citations.

## Stack

- **GitHub** (t1usa99-web): source of truth. Harvester + generator + generated static pages. Data changes land via commits/PRs.
- **Railway**: scheduled harvester job (cron). Re-scrapes counties, parses to the normalized schema, commits updated data back to the repo.
- **Cloudflare**: Pages/Workers host the static site (CDN, Core Web Vitals). D1 = queryable records DB for consumer search + B2B API (add later). R2 = raw source PDF archive. KV = cache. Cloudflare Registrar + DNS for the domain.
- Parsing: `pdftotext -layout` (poppler) + regex; pandas/openpyxl for spreadsheet counties; Firecrawl for Tier-3 JS-rendered pages.

## Normalized record schema

state, county, holding_office, sale_type, sale_date (ISO), case_or_deed_num, parcel_id, previous_owner, sale_amount, amount_owed, surplus_amount, claim_status, record_type, source_url, source_format, scraped_at

## First build slice

Georgia, tax-commissioner counties. Start with the proven Tier-1/2 sources (Coweta, Hall, Cobb, Gwinnett). Ship the county-page generator + 2-3 live pages before scaling to all 159 counties.
