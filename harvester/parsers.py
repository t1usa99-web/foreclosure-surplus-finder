# -*- coding: utf-8 -*-
"""Per-county parsers. Each returns a list of record dicts:
{sale_date, parcel, previous_owner, property_address, overage, status}.
Parsers aim to be robust; the harvester runs sanity checks and opens a PR for human review,
so minor artifacts are caught before anything goes live."""
import re, datetime

MONEY = re.compile(r'\$\s*([\d,]+\.\d{2})')
DATE_MDY = re.compile(r'\b(\d{1,2}/\d{1,2}/\d{4})\b')


def _f(x):
    return float(x.replace(",", ""))


def _iso(d):
    """M/D/YYYY -> YYYY-MM-DD (passthrough if not that shape)."""
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', d.strip())
    if not m:
        return d.strip()
    mo, da, yr = m.groups()
    return "%04d-%02d-%02d" % (int(yr), int(mo), int(da))


# ---------------- COWETA (direct pdf) ----------------
def coweta(text):
    """Columns: Sale Date | Map # | Property Owner | Buyer | Minimum Bid | Sale Amt | Overage | Status.
    Owner/buyer/map# are space-padded columns; the three money amounts anchor the right side."""
    dstart = re.compile(r'^(\d{1,2}/\d{1,2}/\d{4})\b')
    out = []
    for line in text.split("\n"):
        s = line.strip()
        m = dstart.match(s)
        if not m:
            continue
        matches = list(MONEY.finditer(s))
        if len(matches) < 3:
            continue
        min_bid = _f(matches[0].group(1))
        sale_amount = _f(matches[1].group(1))
        overage = _f(matches[2].group(1))
        status = s[matches[2].end():].strip() or "Unclaimed"
        middle = s[m.end():matches[0].start()].strip()
        parts = [p for p in re.split(r"\s{2,}", middle) if p]
        if len(parts) >= 3:
            parcel, buyer, owner = parts[0], parts[-1], " ".join(parts[1:-1])
        elif len(parts) == 2:
            # map# and owner collapsed (single-spaced); split at first pure-alpha token
            toks = parts[0].split()
            i = 0
            while i < len(toks) and (any(c.isdigit() for c in toks[i]) or "-" in toks[i]):
                i += 1
            parcel, owner, buyer = " ".join(toks[:i]), " ".join(toks[i:]), parts[1]
        else:
            parcel, owner, buyer = "", (parts[0] if parts else ""), ""
        if owner.count("(") > owner.count(")"):
            owner = owner + ")"   # close truncated "(LIFE ESTATE)" style notes
        if not owner or overage <= 0:
            continue
        out.append(dict(sale_date=_iso(m.group(1)), parcel=parcel.strip(),
                        previous_owner=owner.strip(), buyer=buyer.strip(),
                        min_bid=round(min_bid, 2), sale_amount=round(sale_amount, 2),
                        overage=round(overage, 2), status=status))
    return out


# ---------------- HALL (html -> pdf) ----------------
def hall(text):
    amt_re = re.compile(r'\$\s*([\d,]+\.\d{2})\s*$')
    map_re = re.compile(r'^(\d{5}[A-Z]?\s?\d{6}[A-Z]?|M\d{7,8}|P\d{5,6})$')

    def is_hdr(l):
        return ('HALL COUNTY TAX' in l or 'TAX SALE DATE' in l
                or l.strip() in ('EXCESS', 'FUNDS', 'EX', 'FU') or 'Information current' in l)
    blocks, buf = [], []
    for l in text.split("\n"):
        if not l.strip() or is_hdr(l):
            continue
        buf.append(l)
        if amt_re.search(l):
            blocks.append(" ".join(buf)); buf = []
    out = []
    for block in blocks:
        m = amt_re.search(block)
        ov = _f(m.group(1)) if m else None
        b = amt_re.sub("", block).replace("$", "")
        f = [x for x in re.split(r"\s{2,}", b.strip()) if x]
        mi = next((i for i, x in enumerate(f) if map_re.match(x)), None)
        if mi is None or ov is None:
            continue
        rest = f[mi + 1:]
        if len(rest) >= 3:
            owner, addr, city = " ".join(rest[:-2]), rest[-2], rest[-1]
        elif len(rest) == 2:
            owner, addr, city = rest[0], "", rest[1]
        elif len(rest) == 1:
            owner, addr, city = rest[0], "", ""
        else:
            owner, addr, city = "", "", ""
        owner = re.sub(r'^(?:\d{5}[A-Z]?\s?\d{6}[A-Z]?|M\d{7,8}|P\d{5,6})\s+', "", owner).strip()
        m2 = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', f[0]) if f else None
        sd = m2.group(0) if m2 else (f[0] if f else "")
        if not owner or ov <= 0:
            continue
        out.append(dict(sale_date=sd, parcel=f[mi], previous_owner=owner,
                        property_address=", ".join([x for x in [addr, city] if x]),
                        overage=round(ov, 2), status="Unclaimed"))
    return out


# ---------------- GWINNETT (html -> pdf) ----------------
def gwinnett(text):
    gamt = re.compile(r'^\$[\d,]+\.\d{2}$')
    gpar = re.compile(r'^[RH]\d{3,4}[A-Z]?\s?[A-Z]?\d{2,3}[A-Z]?$')

    def skip(l):
        s = l.strip()
        return (not s or 'Gwinnett County' in l or s == 'Excess Funds' or 'NAME OF BUYER' in l
                or 'Highlighted' in l or 'MONTH/YEAR' in l or 'TAX SALE' in l
                or re.match(r'^[A-Z]( [A-Z])+$', s) or re.match(r'^\d{1,3}$', s))
    buf, recs = [], []
    for l in text.split("\n"):
        if skip(l):
            continue
        buf.append(l.strip())
        if re.search(r'\$[\d,]+\.\d{2}', l):
            recs.append(" ".join(buf)); buf = []
    out = []
    for block in recs:
        f = [x for x in re.split(r"\s{2,}", block.strip()) if x]
        if f and re.match(r'^\d{1,3}$', f[0]):
            f = f[1:]
        pi = next((i for i, x in enumerate(f) if gpar.match(x)), None)
        ai = next((i for i, x in enumerate(f) if gamt.match(x)), None)
        if pi is None or ai is None or ai <= pi:
            continue
        mid = f[pi + 1:ai]
        owner = " ".join(mid[:-1]) if len(mid) >= 2 else (mid[0] if mid else "")
        situs = mid[-1] if len(mid) >= 2 else ""
        ov = _f(f[ai].replace("$", ""))
        date = " ".join(f[ai + 1:]) if ai + 1 < len(f) else ""
        if not owner or ov <= 0:
            continue
        out.append(dict(sale_date=date, parcel=f[pi], previous_owner=owner,
                        property_address=situs, overage=round(ov, 2), status="Unclaimed"))
    return out


# ---------------- COBB (html -> xlsx) ----------------
def cobb(rows):
    hdr_i = next((i for i, r in enumerate(rows) if r and "Owner" in [str(c) for c in r]), None)
    if hdr_i is None:
        return []
    hdr = [str(c).strip() if c else "" for c in rows[hdr_i]]
    idx = {n: hdr.index(n) for n in ["Date of Sale", "Purchaser", "Owner", "Parcel ID", "Excess Funds", "Pending Claim"] if n in hdr}
    out = []
    for r in rows[hdr_i + 1:]:
        if not r or r[idx["Owner"]] is None or r[idx["Excess Funds"]] is None:
            continue
        try:
            ov = float(r[idx["Excess Funds"]])
        except (TypeError, ValueError):
            continue
        if ov <= 0:
            continue
        d = r[idx["Date of Sale"]]
        sd = d.strftime("%Y-%m-%d") if isinstance(d, datetime.datetime) else (str(d) if d else "")
        pend = str(r[idx.get("Pending Claim", -1)]).strip().lower() if "Pending Claim" in idx else "no"
        out.append(dict(sale_date=sd, parcel=str(r[idx["Parcel ID"]] or "").strip(),
                        previous_owner=str(r[idx["Owner"]]).strip(),
                        buyer=str(r[idx.get("Purchaser", -1)] or "").strip() if "Purchaser" in idx else "",
                        property_address="",
                        overage=round(ov, 2), status="Claim pending" if pend == "yes" else "Unclaimed"))
    return out


# ---------------- DEKALB (direct pdf) ----------------
def dekalb(text):
    out = []
    for l in text.split("\n"):
        if 'EXCESS FUNDS' in l or 'As of' in l or 'PARCEL ID' in l or not l.strip():
            continue
        f = [x for x in re.split(r"\s{2,}", l.strip()) if x]
        if len(f) < 6 or not f[1].startswith("$"):
            continue
        try:
            ov = _f(f[1].replace("$", ""))
        except ValueError:
            continue
        if ov <= 0:
            continue
        parcel, sd, zipc, city, situs = f[0], f[2], f[-1], f[-2], f[-3]
        owner = " ".join(f[3:-3]).strip()
        if not owner:
            owner, situs = situs, ""
        out.append(dict(sale_date=sd, parcel=parcel, previous_owner=owner,
                        property_address=", ".join([x for x in [situs, city] if x]),
                        overage=round(ov, 2), status="Unclaimed"))
    return out


# ---------------- CLAYTON (direct pdf) ----------------
def clayton(text):
    dr = re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4}$')
    out = []
    for l in text.split("\n"):
        s = l.strip()
        if 'CLAYTON COUNTY' in s or 'EXCESS FUNDS' in s or re.match(r'^[A-Z]+\s+\d{4}$', s) or not s:
            continue
        f = [x for x in re.split(r"\s{2,}", s) if x]
        if len(f) < 3 or not dr.match(f[-1]):
            continue
        mi = next((i for i, x in enumerate(f) if re.match(r'^\$?\s*[\d,]+\.\d{2}$', x)), None)
        if mi is None:
            continue
        ov = _f(f[mi].replace("$", ""))
        if ov <= 0:
            continue
        name = f[0]
        parcel = " ".join(f[1:mi]).replace("$", "").strip()
        out.append(dict(sale_date=f[-1], parcel=parcel, previous_owner=name,
                        property_address="", overage=round(ov, 2), status="Unclaimed"))
    return out


# ---------------- HENRY (direct pdf) ----------------
def henry(text):
    a_re = re.compile(r'\$\s*([\d,]+\.\d{2})')
    out = []
    for l in text.split("\n"):
        if 'PARCEL ID' in l or not l.strip() or 'REDEEMED' in l.upper():
            continue
        dm = DATE_MDY.search(l); am = a_re.search(l)
        if not dm or not am:
            continue
        parcel = l.strip().split()[0]
        start = l.find(parcel) + len(parcel)
        mid = l[start:dm.start()].strip()
        parts = [x for x in re.split(r"\s{2,}", mid) if x]
        owner = parts[0] if parts else ""
        address = " ".join(parts[1:]) if len(parts) > 1 else ""
        ov = _f(am.group(1))
        if not owner or ov <= 0:
            continue
        out.append(dict(sale_date=dm.group(1), parcel=parcel, previous_owner=owner.strip(),
                        property_address=address.strip(), overage=round(ov, 2), status="Unclaimed"))
    return out


# ---------------- ATHENS-CLARKE (direct pdf) ----------------
def athens(text):
    dstart = re.compile(r'^(\d{1,2}/\d{1,2}/\d{4})\b')
    out = []
    for line in text.split("\n"):
        s = line.strip()
        m = dstart.match(s)
        if not m:
            continue
        amts = MONEY.findall(s)
        if len(amts) < 4:   # BID, TAXES, EXCESS, (CLAIMED), BALANCE
            continue
        balance = _f(amts[-1])
        if balance <= 0:
            continue
        partial = "(" in s   # a claimed amount is shown in parentheses
        f = [x for x in re.split(r"\s{2,}", s) if x]
        owner = f[1] if len(f) > 1 else ""
        propdesc = f[2] if len(f) > 2 else ""
        if not propdesc or propdesc.startswith("$"):
            continue   # columns did not separate cleanly (e.g. a defendant name containing a slash)
        if " / " in propdesc:
            addr, parcel = propdesc.rsplit(" / ", 1)
        else:
            addr, parcel = propdesc, ""
        if not owner:
            continue
        out.append(dict(sale_date=m.group(1), parcel=parcel.strip(), previous_owner=owner.strip(),
                        property_address=addr.strip(), overage=round(balance, 2),
                        status="Partially claimed" if partial else "Unclaimed"))
    return out


# ---------------- VOLUSIA (direct pdf, FL tax-deed surplus) ----------------
def volusia(text):
    """FL clerk 'Tax Deed Surplus' sheet. Owner names wrap across lines; the row's date
    sits on the last line. We key on the trailing 'remaining balance + remit date'."""
    dstart = re.compile(r'^(\d{1,2}/\d{1,2}/\d{4})\b')
    cert = re.compile(r'\b(\d{2,5}-\d{2})\b')
    tail = re.compile(r'([\d,]+\.\d{2}|-)\s+\d{1,2}/\d{1,2}/\d{4}\s*$')
    namey = re.compile(r"^[A-Z0-9 ./&'\-]+$")
    out, buf = [], []
    for raw in text.split("\n"):
        st = raw.strip()
        m = dstart.match(st)
        if m:
            tm = tail.search(st); cm = cert.search(st)
            if not tm or not cm:
                buf = []; continue
            remaining = 0.0 if tm.group(1) == "-" else _f(tm.group(1))
            owner = re.sub(r"\s{2,}", " ", " ".join(buf + [st[m.end():cm.start()].strip()]).strip())
            buf = []
            if remaining <= 0 or not owner:
                continue
            out.append(dict(sale_date=_iso(m.group(1)), parcel=cm.group(1), previous_owner=owner,
                            property_address="", overage=round(remaining, 2), status="Unclaimed"))
        elif not st:
            buf = []
        else:
            if ("CLERK OF THE CIRCUIT" not in st and "TAX DEED SURPLUS" not in st and namey.match(st)
                    and not cert.search(st) and not re.search(r'\d{1,3}(,\d{3})*\.\d{2}', st)
                    and sum(c.isalpha() for c in st) >= 3):
                buf.append(st)
            else:
                buf = []
    return out

PARSERS = {"coweta": coweta, "hall": hall, "gwinnett": gwinnett, "cobb": cobb,
           "dekalb": dekalb, "clayton": clayton, "henry": henry, "athens": athens, "volusia": volusia}
