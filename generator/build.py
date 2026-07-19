# -*- coding: utf-8 -*-
"""Build the static site from data/counties/*.json.
Usage: python generator/build.py   (run from repo root)"""
import os, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from template import render_county_page, _money
import sitegen
import config

DATA = os.path.join(ROOT, "data", "counties")
OUT = os.path.join(ROOT, "site")
STATE_NAMES = {"georgia": "Georgia", "florida": "Florida", "california": "California"}
STATE_LAW = {
    "georgia": {"office": "county tax commissioner", "window_short": "5 yrs",
                "window": "held by the county for up to five years, after which unclaimed funds transfer to the Georgia unclaimed property program and become harder to recover, so claiming sooner is always better."},
    "florida": {"office": "Clerk of the Circuit Court", "window_short": "1-2 yrs",
                "window": "held by the Clerk of the Circuit Court, which notifies parties of interest. Unclaimed surplus is later reported to the Florida Department of Financial Services as unclaimed property, so it is important to claim promptly."},
    "california": {"office": "county tax collector", "window_short": "1 yr",
                   "window": "held by the county tax collector, and under California Revenue and Taxation Code section 4675 a claim generally must be filed within one year of the tax deed being recorded, so acting quickly is essential."},
}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    SITE = config.SITE_URL
    BRAND = config.BRAND
    counties = []          # raw county dicts
    urls = []              # (loc, lastmod) for sitemap
    index = []             # site-wide search index (one entry per record)

    for fp in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        c = json.load(open(fp, encoding="utf-8"))
        page = render_county_page(c, BRAND, SITE)
        write(os.path.join(OUT, c["state_slug"], c["slug"], "index.html"), page)
        c["_records"] = len(c["records"])
        c["_total"] = sum(r["overage"] for r in c["records"])
        counties.append(c)
        urls.append(("{}/{}/{}/".format(SITE, c["state_slug"], c["slug"]), c["updated"]))
        cu = "/{}/{}/".format(c["state_slug"], c["slug"])
        for r in c["records"]:
            index.append({"n": r["previous_owner"].title(), "c": c["county"],
                          "a": c["state_abbr"], "u": cu,
                          "o": round(r["overage"], 2), "s": r.get("status", "Unclaimed")})
        print("built /{}/{}/  ({} records, {})".format(
            c["state_slug"], c["slug"], c["_records"], _money(c["_total"])))

    # group into states
    states = []
    for slug in sorted(set(c["state_slug"] for c in counties)):
        cs = [c for c in counties if c["state_slug"] == slug]
        states.append({
            "name": STATE_NAMES.get(slug, cs[0]["state"]), "slug": slug,
            "counties": [{"slug": c["slug"], "county": c["county"], "state_abbr": c["state_abbr"],
                          "records": c["_records"], "total": c["_total"]} for c in cs],
            "law": STATE_LAW.get(slug, STATE_LAW["georgia"]),
        })

    totals = (len(counties), sum(c["_records"] for c in counties), sum(c["_total"] for c in counties))

    # site-wide search index (sorted biggest overage first so top matches are meaningful)
    index.sort(key=lambda e: -e["o"])
    write(os.path.join(OUT, "search-index.json"),
          json.dumps(index, ensure_ascii=False, separators=(",", ":")))

    # home
    write(os.path.join(OUT, "index.html"), sitegen.render_home(BRAND, SITE, states, totals))
    urls.append((SITE + "/", None))

    # state hubs
    for s in states:
        write(os.path.join(OUT, s["slug"], "index.html"), sitegen.render_state_hub(BRAND, SITE, s))
        urls.append(("{}/{}".format(SITE, s["slug"]), None))

    # trust pages
    trust = {"about": sitegen.render_about, "contact": sitegen.render_contact,
             "privacy": sitegen.render_privacy, "terms": sitegen.render_terms,
             "disclaimer": sitegen.render_disclaimer}
    for slug, fn in trust.items():
        write(os.path.join(OUT, slug, "index.html"), fn(BRAND, SITE))
        urls.append(("{}/{}".format(SITE, slug), None))

    # sitemap
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        sm.append("  <url><loc>{}</loc>{}</url>".format(
            loc, "<lastmod>{}</lastmod>".format(lastmod) if lastmod else ""))
    sm.append("</urlset>")
    write(os.path.join(OUT, "sitemap.xml"), "\n".join(sm) + "\n")
    write(os.path.join(OUT, "robots.txt"),
          "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(SITE))

    # guard: no em dash anywhere in generated HTML
    joined = "".join(open(os.path.join(dp, f), encoding="utf-8").read()
                     for dp, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
    for bad in ("—", "&mdash;", "&#8212;"):
        assert bad not in joined, "em dash form found in generated HTML: " + bad
    print("\nOK: {} counties, {} states, {} trust pages, home, sitemap, {} search records. No em dashes.".format(
        len(counties), len(states), len(trust), len(index)))


if __name__ == "__main__":
    main()
