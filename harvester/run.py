# -*- coding: utf-8 -*-
"""Harvester entry point. For each county in the registry: fetch the source, skip if unchanged,
parse, sanity-check, and (if auto and sane) rewrite data/counties/<slug>.json preserving metadata.
Designed to run in CI monthly; the workflow opens a PR with any changes.

Env:
  FIRECRAWL_API_KEY  optional; only needed for method='firecrawl' counties.
  MAX_FIRECRAWL      optional int cap on firecrawl calls per run (default 5).
"""
import os, sys, json, hashlib, datetime, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import registry, adapters, parsers

DATA = os.path.join(ROOT, "data", "counties")
STATE = os.path.join(HERE, "state.json")
TODAY = datetime.date.today().isoformat()
MAX_FIRECRAWL = int(os.environ.get("MAX_FIRECRAWL", "5"))


def load_state():
    return json.load(open(STATE)) if os.path.exists(STATE) else {}


def write_county(slug, records):
    p = os.path.join(DATA, slug + ".json")
    doc = json.load(open(p, encoding="utf-8"))
    doc["records"] = records
    doc["updated"] = TODAY
    head = {k: doc[k] for k in doc if k != "records"}
    lines = ["{"]
    for k, v in head.items():
        lines.append(" " + json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False) + ",")
    lines.append(' "records": [')
    for i, r in enumerate(records):
        lines.append("  " + json.dumps(r, ensure_ascii=False) + ("," if i < len(records) - 1 else ""))
    lines += [" ]", "}"]
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def sane(slug, records):
    """Reject obviously-broken parses so bad data never overwrites good data."""
    p = os.path.join(DATA, slug + ".json")
    prev = len(json.load(open(p, encoding="utf-8"))["records"]) if os.path.exists(p) else 0
    problems = []
    if len(records) < 3:
        problems.append("only %d records" % len(records))
    if prev and len(records) < 0.5 * prev:
        problems.append("record count dropped from %d to %d" % (prev, len(records)))
    if any(not r["previous_owner"] or len(r["previous_owner"]) < 3 for r in records):
        problems.append("empty/short owner name present")
    if any(r["overage"] is None or r["overage"] <= 0 for r in records):
        problems.append("non-positive overage present")
    return problems


def fetch_records(cfg, firecrawl_budget):
    """Resolve + download + parse one county. Returns (records, firecrawl_consumed)."""
    consumed = 0
    if cfg["method"] == "firecrawl":
        key = os.environ.get("FIRECRAWL_API_KEY")
        if not key:
            raise RuntimeError("__skip__ firecrawl: no FIRECRAWL_API_KEY")
        if firecrawl_budget <= 0:
            raise RuntimeError("__skip__ firecrawl: budget reached")
        consumed = 1
        file_url = adapters.firecrawl_resolve_file_url(cfg, key)
    else:
        file_url = adapters.resolve_file_url(cfg)
    data = adapters.fetch_bytes(file_url)
    if cfg["kind"] == "xlsx":
        records = parsers.PARSERS[cfg["parser"]](adapters.xlsx_rows(data))
    else:
        records = parsers.PARSERS[cfg["parser"]](adapters.pdf_to_text(data))
    records.sort(key=lambda r: -r["overage"])
    return records, consumed


def main():
    state = load_state()
    firecrawl_used = 0
    changed, skipped, warned, errored = [], [], [], []

    for cfg in registry.COUNTIES:
        slug = cfg["slug"]
        try:
            records, consumed = fetch_records(cfg, MAX_FIRECRAWL - firecrawl_used)
            firecrawl_used += consumed

            h = hashlib.sha256(json.dumps(records, ensure_ascii=False).encode("utf-8")).hexdigest()
            if state.get(slug) == h and cfg.get("auto"):
                skipped.append(slug + " (unchanged)")
                continue

            probs = sane(slug, records)
            if probs:
                warned.append("%s: %s (kept existing data)" % (slug, "; ".join(probs)))
                continue
            if not cfg.get("auto"):
                warned.append("%s: source changed but auto=False (needs manual reparse)" % slug)
                state[slug] = h
                continue

            write_county(slug, records)
            state[slug] = h
            total = sum(r["overage"] for r in records)
            changed.append("{}: {} records, ${:,.2f}".format(slug, len(records), total))
        except Exception as e:
            msg = "%s: %s" % (slug, e)
            if "__skip__" in str(e):
                skipped.append("%s (%s)" % (slug, str(e).split("__skip__", 1)[1].strip()))
            elif "link not found" in str(e) or "HTTPError" in type(e).__name__ or "Timeout" in type(e).__name__ or "Connection" in type(e).__name__:
                skipped.append(msg + " (fetch/link issue, kept existing data)")
            else:
                errored.append(msg); traceback.print_exc()

    json.dump(state, open(STATE, "w"), indent=1)

    print("\n===== HARVEST SUMMARY (%s) =====" % TODAY)
    for label, items in [("CHANGED", changed), ("SKIPPED", skipped), ("WARNINGS", warned), ("ERRORS", errored)]:
        print("\n%s (%d):" % (label, len(items)))
        for it in items:
            print("  - " + it)

    open(os.path.join(HERE, "last_run.json"), "w").write(json.dumps(
        {"date": TODAY, "changed": changed, "skipped": skipped, "warnings": warned, "errors": errored}, indent=1))
    if errored:
        sys.exit(1)


if __name__ == "__main__":
    main()
