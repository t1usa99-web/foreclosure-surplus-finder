# -*- coding: utf-8 -*-
"""Render one county excess-funds page from a county data dict.
Beats the SurplusFundsList template on record depth. Never emits an em dash."""
import html, json, datetime


def _money(x):
    return "${:,.2f}".format(x)


def _nice_date(iso):
    try:
        return datetime.datetime.strptime(iso, "%Y-%m-%d").strftime("%b %d, %Y").replace(" 0", " ")
    except (ValueError, TypeError):
        return iso


def _pretty_updated(iso):
    return datetime.datetime.strptime(iso, "%Y-%m-%d").strftime("%B %d, %Y").replace(" 0", " ")


def render_county_page(c, brand, site_url):
    recs = c["records"]
    n = len(recs)
    total = sum(r["overage"] for r in recs)
    unclaimed = [r for r in recs if r.get("status", "Unclaimed") == "Unclaimed"]
    total_unclaimed = sum(r["overage"] for r in unclaimed)
    largest = max(recs, key=lambda r: r["overage"])
    updated = _pretty_updated(c["updated"])
    canonical = "{}/{}/{}".format(site_url, c["state_slug"], c["slug"])
    county = c["county"]
    state = c["state"]

    title = "{}, {} Excess Funds List: Unclaimed Tax Sale Surplus Funds".format(county, c["state_abbr"])
    metadesc = ("See {}, {} unclaimed tax-sale surplus funds: {} excess-funds records totaling {}. "
                "Check if you are owed money and how to claim it free from the county.").format(
                    county, state, n, _money(total))

    # optional middle column: property address if any, else sale amount if any, else none
    has_addr = any(r.get("property_address") for r in recs)
    has_sale = any(r.get("sale_amount") is not None for r in recs)
    opt = "addr" if has_addr else ("sale" if has_sale else None)
    opthead = ('<th class="opt">Property address</th>' if opt == "addr"
               else ('<th class="opt">Sale amount</th>' if opt == "sale" else ""))
    rows = []
    for r in sorted(recs, key=lambda r: r["overage"], reverse=True):
        status = r.get("status", "Unclaimed")
        badge = "unclaimed" if status == "Unclaimed" else ("filed" if "Claim" in status else "interpleader")
        if opt == "addr":
            optcell = '<td class="opt">{}</td>'.format(html.escape(r.get("property_address", "")))
        elif opt == "sale":
            optcell = '<td class="opt">{}</td>'.format(_money(r["sale_amount"]) if r.get("sale_amount") is not None else "")
        else:
            optcell = ""
        rows.append(
            '      <tr data-owner="{ol}" data-status="{b}">\n'
            '        <td class="owner">{o}</td>\n'
            '        <td class="ov">{ov}</td>\n'
            '        <td>{p}</td>\n'
            '        {opt}\n'
            '        <td>{d}</td>\n'
            '        <td><span class="badge {b}">{s}</span></td>\n'
            '      </tr>'.format(
                ol=html.escape(r["previous_owner"].lower()), b=badge,
                o=html.escape(r["previous_owner"].title()), ov=_money(r["overage"]),
                p=html.escape(r["parcel"]), opt=optcell, d=_nice_date(r["sale_date"]),
                s=html.escape(status)))
    rows_html = "\n".join(rows)

    claim_form_line = ("{} requires no claim form.".format(county) if c.get("no_claim_form")
                       else "Request the claim form from the {}.".format(c["holding_office"]))
    faq = [
        ("Are there really unclaimed surplus funds in {}, {}?".format(county, state),
         ("Yes. As of {}, the published excess funds list for {} shows {} tax-sale surplus records "
          "totaling {}, of which about {} across {} records is still unclaimed. Surplus (excess) funds "
          "are created when a property sells at a tax sale for more than the taxes and costs owed; the "
          "difference legally belongs to the former owner or their heirs.").format(
              updated, county, n, _money(total), _money(total_unclaimed), len(unclaimed))),
        ("How do I claim excess funds from a {} tax sale?".format(county),
         ("{} Submit a written, signed, and notarized claim to the {} stating the basis of your claim, "
          "along with a valid photo ID, at {}. Include supporting documents such as deeds, assignments, "
          "or powers of attorney.").format(claim_form_line, c["holding_office"], c["office_address"])),
        ("How long do I have to claim surplus funds in {}?".format(state),
         ("In {}, tax-sale excess funds are generally held by the county for up to {} years before they "
          "transfer to the state unclaimed property division. Claiming sooner is always better.").format(
              state, c.get("hold_years", 5))),
        ("Do I have to pay a recovery company to claim my money?",
         ("No. You can file a claim directly with the county for free. Recovery firms and attorneys can "
          "handle the paperwork for a fee (commonly 10% to 30%), which some owners prefer for estate, "
          "lien, or interpleader situations, but it is never required.")),
        ("What does \"interpleader filed\" mean on the list?",
         ("When there are competing or conflicting claims, the county may file an interpleader action with "
          "the Superior Court, and a judge decides how the funds are distributed. Reasonable attorney fees "
          "and court costs are paid from the excess funds first.")),
    ]
    faq_html = "\n".join(
        '    <details class="faq"><summary>{}</summary><p>{}</p></details>'.format(
            html.escape(q), html.escape(a)) for q, a in faq)

    def ld(obj):
        return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

    breadcrumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url + "/"},
        {"@type": "ListItem", "position": 2, "name": state + " Surplus Funds",
         "item": "{}/{}".format(site_url, c["state_slug"])},
        {"@type": "ListItem", "position": 3, "name": county, "item": canonical}]}
    dataset_ld = {"@context": "https://schema.org", "@type": "Dataset",
                  "name": "{}, {} Tax Sale Excess Funds List".format(county, c["state_abbr"]),
                  "description": "Parsed list of {} tax-sale surplus (excess funds) records in {}, {}, totaling {}.".format(
                      n, county, state, _money(total)),
                  "spatialCoverage": "{}, {}, USA".format(county, state),
                  "dateModified": c["updated"], "isAccessibleForFree": True,
                  "creator": {"@type": "Organization", "name": brand},
                  "license": "https://www.usa.gov/government-works"}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{metadesc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{brand}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{metadesc}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{metadesc}">
{bc}
{ds}
{fq}
<style>
 :root{{--ink:#1a2230;--muted:#5b6472;--line:#e6e9ef;--brand:#1f6f5c;--brand-d:#155244;--bg:#fff;--soft:#f6f8f7;--gold:#b9761f;}}
 *{{box-sizing:border-box}}
 body{{margin:0;font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}}
 .wrap{{max-width:960px;margin:0 auto;padding:0 20px}}
 a{{color:var(--brand-d)}}
 nav.crumb{{font-size:13px;color:var(--muted);padding:14px 0}}
 header.hero{{background:linear-gradient(160deg,#f0f6f4,#fbfdfc);border-bottom:1px solid var(--line)}}
 h1{{font-size:30px;line-height:1.2;margin:.2em 0 .3em}}
 .sub{{color:var(--muted);font-size:15px;margin-top:0}}
 .updated{{display:inline-block;font-size:12px;color:var(--brand-d);background:#e4f0ec;border-radius:20px;padding:3px 12px;margin-bottom:8px}}
 .cta-row{{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0 26px}}
 .btn{{display:inline-block;background:var(--brand);color:#fff;text-decoration:none;padding:11px 20px;border-radius:8px;font-weight:600;font-size:15px}}
 .btn.ghost{{background:#fff;color:var(--brand-d);border:1.5px solid var(--brand)}}
 .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}
 .stat{{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:16px}}
 .stat b{{display:block;font-size:22px;color:var(--brand-d)}}
 .stat span{{font-size:12.5px;color:var(--muted)}}
 h2{{font-size:22px;margin:34px 0 10px;padding-top:8px}}
 .toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}}
 input[type=search]{{flex:1;min-width:220px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;font-size:15px}}
 table{{width:100%;border-collapse:collapse;font-size:14px;margin-top:6px}}
 th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
 th{{background:var(--soft);font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}}
 td.owner{{font-weight:600}}
 td.ov{{color:var(--brand-d);font-weight:700;white-space:nowrap}}
 .badge{{font-size:11px;padding:2px 8px;border-radius:20px;white-space:nowrap}}
 .badge.unclaimed{{background:#e4f0ec;color:var(--brand-d)}}
 .badge.interpleader{{background:#fdeede;color:var(--gold)}}
 .badge.filed{{background:#eef0f4;color:var(--muted)}}
 ol.steps{{padding-left:18px}} ol.steps li{{margin:8px 0}}
 .callout{{background:var(--soft);border-left:4px solid var(--brand);border-radius:6px;padding:14px 16px;margin:16px 0}}
 details.faq{{border-bottom:1px solid var(--line);padding:10px 0}}
 details.faq summary{{font-weight:600;cursor:pointer}}
 .other{{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
 .other a{{background:var(--soft);border:1px solid var(--line);border-radius:20px;padding:5px 12px;font-size:13px;text-decoration:none}}
 footer{{border-top:1px solid var(--line);margin-top:40px;padding:22px 0;color:var(--muted);font-size:12.5px}}
 .disc{{font-size:12px;color:var(--muted);margin-top:18px}}
 @media(max-width:640px){{.stats{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:24px}}.opt{{display:none}}}}
</style>
</head>
<body>
<header class="hero">
 <div class="wrap">
  <nav class="crumb" aria-label="Breadcrumb"><a href="{site}/">Home</a> &rsaquo; <a href="{site}/{sslug}">{state} Surplus Funds</a> &rsaquo; {county}</nav>
  <span class="updated">Last updated {updated}</span>
  <h1>{county}, {abbr} Excess Funds List: Unclaimed Tax Sale Surplus Funds</h1>
  <p class="sub">Were you the owner of a property sold at a {county} tax sale? You may be owed <strong>surplus funds</strong>, and you can claim them yourself, for free, directly from the county.</p>
  <div class="cta-row">
   <a class="btn" href="#list">See the {n} records &darr;</a>
   <a class="btn ghost" href="#claim">How to claim (free) &rarr;</a>
  </div>
 </div>
</header>
<main class="wrap">
 <section class="stats" aria-label="{county} surplus funds by the numbers">
  <div class="stat"><b>{n}</b><span>excess-funds records on file</span></div>
  <div class="stat"><b>{total}</b><span>total surplus on the list</span></div>
  <div class="stat"><b>{tunc}</b><span>still unclaimed ({nunc} records)</span></div>
  <div class="stat"><b>{lg}</b><span>largest single overage</span></div>
 </section>
 <p>When a property is sold at a {county} tax sale for more than the delinquent taxes, penalties, and costs owed, the leftover money (called <strong>excess funds</strong>, surplus funds, or overage) is held in escrow by the {office}. Under <a href="{stat_url}" rel="nofollow">{stat_label}</a>, that money legally belongs to the former owner (or their heirs and certain lienholders), not the county and not the tax-sale buyer. Below is every record from the county's current published list.</p>
 <h2 id="list">{county} excess funds list ({updated})</h2>
 <div class="toolbar">
  <input type="search" id="q" placeholder="Search by former owner name..." aria-label="Search records by owner name">
  <span id="count" class="sub"></span>
 </div>
 <div style="overflow-x:auto">
 <table id="tbl">
  <thead><tr><th>Former owner</th><th>Overage owed</th><th>Parcel / Map #</th>{opthead}<th>Sale date</th><th>Status</th></tr></thead>
  <tbody>
{rows}
  </tbody>
 </table>
 </div>
 <p class="sub">Source: {office}, Excess Funds List. Amounts are the county-published overage at time of sale; balances change as claims are paid. Verify current status with the county before filing.</p>
 <h2 id="claim">How to claim excess funds in {county}</h2>
 <ol class="steps">
  <li><strong>Confirm you are on the list.</strong> Find your name (or the prior owner's, if you are an heir) in the table above and note the parcel and sale date.</li>
  <li><strong>Write your claim.</strong> Prepare a written statement of the basis of your claim: that you were the owner at the time of sale (or an heir or lienholder with a recorded interest).</li>
  <li><strong>Sign and notarize it,</strong> and gather a valid government-issued <strong>photo ID</strong> plus supporting documents (warranty deed, security deed, assignments, power of attorney).</li>
  <li><strong>Submit to the {office}</strong> at {addr}.</li>
  <li><strong>Respond to any follow-up.</strong> Claims are reviewed by counsel; you may be asked for additional documentation before disbursement.</li>
 </ol>
 <div class="callout"><strong>Competing claims?</strong> If more than one party claims the same funds, the county may file an <em>interpleader</em> with the Superior Court, and a judge decides. Reasonable attorney fees and court costs are paid from the excess funds first.</div>
 <h2>Do it yourself, or get help?</h2>
 <p>Most straightforward owner claims can be filed directly with the county for <strong>free</strong>, and you never have to pay anyone to get your own money. For estates, tangled liens, out-of-state heirs, or interpleader cases, some people prefer a surplus-recovery specialist or attorney who handles the paperwork for a fee (commonly 10% to 30%).</p>
 <div class="cta-row">
  <a class="btn ghost" href="#claim">File it yourself (free)</a>
  <a class="btn" href="#" rel="nofollow sponsored">Connect with a vetted {abbr} recovery attorney &rarr;</a>
 </div>
 <h2>Frequently asked questions</h2>
{faq}
 <p class="disc"><strong>Disclaimer:</strong> This page is for informational purposes only and is not legal or financial advice. Records are compiled from publicly available {office} filings and may be out of date; balances change as claims are processed. Always verify current status directly with the county. We are a data service and do not file claims, represent claimants, or collect funds.</p>
</main>
<footer><div class="wrap">{brand}: public-record tax-sale surplus, organized by county. Data source: {office}. Not affiliated with any county or government agency.</div></footer>
<script>
(function(){{
 var q=document.getElementById('q'),tbl=document.getElementById('tbl'),
     rows=[].slice.call(tbl.tBodies[0].rows),count=document.getElementById('count');
 function upd(){{
  var t=q.value.trim().toLowerCase(),shown=0;
  rows.forEach(function(r){{
   var hit=!t||r.getAttribute('data-owner').indexOf(t)>-1;
   r.style.display=hit?'':'none'; if(hit)shown++;
  }});
  count.textContent=shown+' of '+rows.length+' records';
 }}
 q.addEventListener('input',upd); upd();
}})();
</script>
</body>
</html>""".format(
        title=html.escape(title), metadesc=html.escape(metadesc), canonical=canonical,
        brand=html.escape(brand), bc=ld(breadcrumb_ld), ds=ld(dataset_ld), fq=ld(faq_ld),
        site=site_url, sslug=c["state_slug"], state=html.escape(state), county=html.escape(county),
        abbr=c["state_abbr"], updated=updated, n=n, total=_money(total), tunc=_money(total_unclaimed),
        nunc=len(unclaimed), lg=_money(largest["overage"]), office=html.escape(c["holding_office"]),
        stat_url=c["statute_url"], stat_label=html.escape(c["statute_label"]),
        addr=html.escape(c["office_address"]), rows=rows_html, faq=faq_html, opthead=opthead)

    assert "—" not in doc, "em dash found in output for " + c["slug"]
    return doc
