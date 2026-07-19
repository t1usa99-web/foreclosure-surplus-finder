# -*- coding: utf-8 -*-
"""Fetching + file-format helpers for the harvester."""
import re, subprocess, tempfile, os, urllib.parse
import requests

UA = {"User-Agent": "Mozilla/5.0 (compatible; SurplusFundsBot/1.0; +https://yoursurplusfunds.com)"}
TIMEOUT = 45
FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v1/scrape"


def fetch_bytes(url):
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    return r.content


def fetch_text(url):
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def _pick_link(links, link_re, base):
    rx = re.compile(link_re, re.I)
    for L in links:
        if L and rx.search(L):
            return urllib.parse.urljoin(base, L.replace("&amp;", "&"))
    return None


def resolve_file_url(cfg):
    """Return the actual file URL to download for this county (direct or html-linked)."""
    if cfg["method"] == "direct":
        return cfg["url"]
    if cfg["method"] == "html":
        html = fetch_text(cfg["url"])
        m = re.search(cfg["link_re"], html)
        if not m:
            raise RuntimeError("link not found on {} with {}".format(cfg["url"], cfg["link_re"]))
        link = urllib.parse.urljoin(cfg["url"], m.group(1).replace("&amp;", "&"))
        return urllib.parse.quote(link, safe=":/?=&%#")
    raise RuntimeError("unknown method " + cfg["method"])


def firecrawl_links(url, api_key, wait=6000):
    """Render a JS-heavy page via Firecrawl and return the list of discovered links."""
    r = requests.post(
        FIRECRAWL_ENDPOINT,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        json={"url": url, "formats": ["links"], "waitFor": wait},
        timeout=TIMEOUT * 3)
    r.raise_for_status()
    data = r.json().get("data", {}) or {}
    return data.get("links") or []


def firecrawl_resolve_file_url(cfg, api_key):
    """For method='firecrawl' counties: render the page, find the file link (link_re)."""
    links = firecrawl_links(cfg["url"], api_key)
    link_re = cfg.get("link_re", r'\.(xlsx|pdf)(\?|$)')
    url = _pick_link(links, link_re, cfg["url"])
    if not url:
        raise RuntimeError("firecrawl: no file link matched {} on {}".format(link_re, cfg["url"]))
    return urllib.parse.quote(url, safe=":/?=&%#")


def pdf_to_text(data):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(data); path = f.name
    try:
        out = subprocess.run(["pdftotext", "-layout", path, "-"],
                             capture_output=True, text=True, timeout=120)
        return out.stdout
    finally:
        os.unlink(path)


def xlsx_rows(data):
    import openpyxl, io
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    return list(wb.active.iter_rows(values_only=True))
