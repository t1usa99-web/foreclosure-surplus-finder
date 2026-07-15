# -*- coding: utf-8 -*-
"""Fetching + file-format helpers for the harvester."""
import re, subprocess, tempfile, os, urllib.parse
import requests

UA = {"User-Agent": "Mozilla/5.0 (compatible; SurplusFundsBot/1.0; +https://yoursurplusfunds.com)"}
TIMEOUT = 45


def fetch_bytes(url):
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    return r.content


def fetch_text(url):
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def resolve_file_url(cfg):
    """Return the actual file URL to download for this county."""
    if cfg["method"] == "direct":
        return cfg["url"]
    if cfg["method"] == "html":
        html = fetch_text(cfg["url"])
        m = re.search(cfg["link_re"], html)
        if not m:
            raise RuntimeError("link not found on {} with {}".format(cfg["url"], cfg["link_re"]))
        link = m.group(1).replace("&amp;", "&")
        link = urllib.parse.urljoin(cfg["url"], link)
        # encode spaces that some county sites leave raw in hrefs
        return urllib.parse.quote(link, safe=":/?=&%#")
    raise RuntimeError("unknown method " + cfg["method"])


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
