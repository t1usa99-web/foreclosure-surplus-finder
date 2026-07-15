# -*- coding: utf-8 -*-
"""Build the static site from data/counties/*.json.
Usage: python generator/build.py   (run from repo root)"""
import os, sys, glob, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from template import render_county_page, _money
import config

DATA = os.path.join(ROOT, "data", "counties")
OUT = os.path.join(ROOT, "site")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    counties = []
    for fp in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        c = json.load(open(fp, encoding="utf-8"))
        page = render_county_page(c, config.BRAND, config.SITE_URL)
        out = os.path.join(OUT, c["state_slug"], c["slug"], "index.html")
        write(out, page)
        total = sum(r["overage"] for r in c["records"])
        counties.append((c, total))
        print("built /{}/{}/  ({} records, {})".format(
            c["state_slug"], c["slug"], len(c["records"]), _money(total)))

    # sitemap.xml
    urls = "".join(
        "  <url><loc>{}/{}/{}/</loc><lastmod>{}</lastmod></url>\n".format(
            config.SITE_URL, c["state_slug"], c["slug"], c["updated"])
        for c, _ in counties)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + '  <url><loc>{}/</loc></url>\n'.format(config.SITE_URL) + urls + "</urlset>\n")
    write(os.path.join(OUT, "sitemap.xml"), sitemap)

    # robots.txt
    write(os.path.join(OUT, "robots.txt"),
          "User-agent: *\nAllow: /\nSitemap: {}/sitemap.xml\n".format(config.SITE_URL))

    # simple homepage index
    items = "\n".join(
        '   <li><a href="/{}/{}/">{}, {}</a> ({} records, {} in surplus)</li>'.format(
            c["state_slug"], c["slug"], html.escape(c["county"]), c["state_abbr"],
            len(c["records"]), _money(t))
        for c, t in counties)
    index = ("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
             "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
             "<title>{brand}: County Tax Sale Surplus Funds</title>"
             "<meta name=\"description\" content=\"Search county tax-sale surplus and excess funds lists. "
             "See if you are owed money and how to claim it free.\">"
             "<link rel=\"canonical\" href=\"{site}/\"></head>"
             "<body style=\"font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;max-width:820px;"
             "margin:40px auto;padding:0 20px;color:#1a2230\">"
             "<h1>{brand}</h1><p>Public-record tax-sale surplus funds, organized by county. "
             "Find out if you are owed money, and claim it yourself for free.</p>"
             "<h2>Counties</h2><ul>\n{items}\n</ul></body></html>").format(
                 brand=html.escape(config.BRAND), site=config.SITE_URL, items=items)
    write(os.path.join(OUT, "index.html"), index)

    # guards
    joined = "".join(open(os.path.join(dp, f), encoding="utf-8").read()
                     for dp, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
    for _bad in ("—", "&mdash;", "&#8212;"):
        assert _bad not in joined, "em dash form found in generated HTML: " + _bad
    print("\nOK: {} county page(s), sitemap.xml, robots.txt, index.html. No em dashes.".format(len(counties)))


if __name__ == "__main__":
    main()
