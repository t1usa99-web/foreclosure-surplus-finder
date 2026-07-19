# -*- coding: utf-8 -*-
"""Shared site chrome (header, footer, CSS) plus home, state-hub, and trust pages.
Never emits an em dash. All copy is honest, consumer-first framing."""
import html, json, datetime

CONTACT_EMAIL = "contact@yoursurplusfunds.com"


def _money(x):
    return "${:,.2f}".format(x)


SITE_CSS = """
:root{--ink:#1a2230;--muted:#5b6472;--line:#e6e9ef;--brand:#1f6f5c;--brand-d:#155244;--bg:#fff;--soft:#f6f8f7;--gold:#b9761f;--hero:#eaf3f0}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font:16px/1.65 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--brand-d)}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.sitehead{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.sitehead .row{display:flex;align-items:center;justify-content:space-between;height:60px}
.brand{display:flex;align-items:center;gap:9px;font-weight:800;color:var(--brand-d);text-decoration:none;font-size:18px;letter-spacing:-.01em}
.brand .dot{width:22px;height:22px;border-radius:6px;background:var(--brand);display:inline-block}
.nav a{color:var(--ink);text-decoration:none;font-size:15px;margin-left:22px;font-weight:500}
.nav a:hover{color:var(--brand-d)}
@media(max-width:640px){.nav a{margin-left:14px;font-size:14px}.brand{font-size:16px}}
.hero{background:linear-gradient(165deg,var(--hero),#fbfdfc 70%);border-bottom:1px solid var(--line)}
.hero .wrap{padding:56px 20px 48px}
h1{font-size:40px;line-height:1.12;letter-spacing:-.02em;margin:.1em 0 .35em;max-width:15ch}
.hero p.lede{font-size:19px;color:var(--muted);max-width:60ch;margin:0 0 26px}
.btn{display:inline-block;background:var(--brand);color:#fff;text-decoration:none;padding:13px 24px;border-radius:9px;font-weight:600;font-size:16px}
.btn:hover{background:var(--brand-d)}
.btn.ghost{background:#fff;color:var(--brand-d);border:1.5px solid var(--brand)}
.cta-row{display:flex;gap:12px;flex-wrap:wrap}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:38px 0}
.stat{background:var(--soft);border:1px solid var(--line);border-radius:12px;padding:20px}
.stat b{display:block;font-size:26px;color:var(--brand-d);letter-spacing:-.01em}
.stat span{font-size:13px;color:var(--muted)}
section.band{padding:46px 0}
section.band.alt{background:var(--soft);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
h2{font-size:27px;letter-spacing:-.01em;margin:0 0 6px}
.sub{color:var(--muted);margin:0 0 22px;max-width:65ch}
.steps3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px}
.card .n{width:30px;height:30px;border-radius:50%;background:var(--brand);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:10px}
.card h3{margin:.1em 0 .3em;font-size:17px}
.card p{margin:0;color:var(--muted);font-size:14.5px}
.counties{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:8px}
.county{display:flex;justify-content:space-between;align-items:center;gap:12px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.county:hover{border-color:var(--brand);box-shadow:0 1px 0 var(--brand)}
.county b{font-weight:600}
.county .meta{font-size:13px;color:var(--muted);white-space:nowrap}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}.steps3{grid-template-columns:1fr}.counties{grid-template-columns:1fr}h1{font-size:31px}}
.prose{max-width:74ch}
.prose h2{margin-top:30px;font-size:22px}
.prose h3{margin-top:22px;font-size:17px}
.prose p,.prose li{color:#2a3340}
.prose ul{padding-left:20px}
.crumb{font-size:13px;color:var(--muted);padding:16px 0}
details.faq{border-bottom:1px solid var(--line);padding:12px 0}
details.faq summary{font-weight:600;cursor:pointer}
details.faq p{color:var(--muted);margin:.5em 0 0}
.callout{background:var(--soft);border-left:4px solid var(--brand);border-radius:6px;padding:14px 18px;margin:18px 0}
.sitefoot{background:#12211c;color:#c7d3ce;margin-top:8px;padding:40px 0 26px;font-size:14px}
.sitefoot a{color:#dfe9e5;text-decoration:none}
.sitefoot a:hover{text-decoration:underline}
.footcols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:24px}
.footcols h4{color:#fff;font-size:13px;text-transform:uppercase;letter-spacing:.05em;margin:0 0 10px}
.footcols ul{list-style:none;padding:0;margin:0}
.footcols li{margin:6px 0}
.footbrand{font-weight:800;color:#fff;font-size:18px}
.footnote{border-top:1px solid #2a3a34;margin-top:26px;padding-top:18px;color:#8ea39b;font-size:12.5px;line-height:1.6}
@media(max-width:720px){.footcols{grid-template-columns:1fr 1fr}}
.search{position:relative;max-width:560px;margin:6px 0 22px}
.search input{width:100%;padding:15px 16px;border:1.5px solid var(--brand);border-radius:10px;font-size:17px}
.results{position:absolute;left:0;right:0;top:100%;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 8px 28px rgba(20,40,34,.12);margin-top:6px;max-height:360px;overflow:auto;z-index:30}
.results a{display:flex;justify-content:space-between;gap:12px;padding:11px 14px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.results a:last-child{border-bottom:0}
.results a:hover{background:var(--soft)}
.results .nm{font-weight:600}
.results .mt{font-size:13px;color:var(--muted);white-space:nowrap}
.results .empty{padding:12px 14px;color:var(--muted);font-size:14px}
"""


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def _head(title, desc, canonical, brand, extra_ld=None):
    parts = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>{}</title>".format(html.escape(title)),
        '<meta name="description" content="{}">'.format(html.escape(desc)),
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<link rel="canonical" href="{}">'.format(canonical),
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="{}">'.format(html.escape(brand)),
        '<meta property="og:title" content="{}">'.format(html.escape(title)),
        '<meta property="og:description" content="{}">'.format(html.escape(desc)),
        '<meta property="og:url" content="{}">'.format(canonical),
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    for obj in (extra_ld or []):
        parts.append(_ld(obj))
    parts.append("<style>{}</style>".format(SITE_CSS))
    return "\n".join(parts)


def _header(site, brand):
    return (
        '<header class="sitehead"><div class="wrap"><div class="row">'
        '<a class="brand" href="{s}/"><span class="dot"></span>{b}</a>'
        '<nav class="nav"><a href="{s}/">Home</a><a href="{s}/georgia">Georgia</a>'
        '<a href="{s}/about">About</a><a href="{s}/contact">Contact</a></nav>'
        "</div></div></header>"
    ).format(s=site, b=html.escape(brand))


def footer(site, brand):
    year = 2026
    return (
        '<footer class="sitefoot"><div class="wrap">'
        '<div class="footcols">'
        '<div><div class="footbrand">{b}</div>'
        '<p style="max-width:34ch;margin:.6em 0 0">Public-record tax-sale surplus funds, organized by county. '
        "Find out if you are owed money, and claim it yourself for free.</p></div>"
        '<div><h4>Explore</h4><ul>'
        '<li><a href="{s}/">Home</a></li>'
        '<li><a href="{s}/georgia">Georgia counties</a></li>'
        "</ul></div>"
        '<div><h4>Company</h4><ul>'
        '<li><a href="{s}/about">About</a></li>'
        '<li><a href="{s}/contact">Contact</a></li>'
        "</ul></div>"
        '<div><h4>Legal</h4><ul>'
        '<li><a href="{s}/privacy">Privacy Policy</a></li>'
        '<li><a href="{s}/terms">Terms of Service</a></li>'
        '<li><a href="{s}/disclaimer">Disclaimer</a></li>'
        "</ul></div>"
        "</div>"
        '<div class="footnote">{b} is a data and information service. We are not a law firm, not a '
        "financial advisor, not a debt collector, and not affiliated with any county, state, or government "
        "agency. We do not file claims or represent claimants. Information is compiled from public records "
        "and may be out of date, so always verify with the county before filing. Some outbound links to "
        "recovery professionals or attorneys may be paid or affiliate links; see our "
        '<a href="{s}/disclaimer">Disclaimer</a>. Copyright {y} {b}.</div>'
        "</div></footer>"
    ).format(s=site, b=html.escape(brand), y=year)


def page(title, desc, canonical, brand, site, body, extra_ld=None):
    doc = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n{head}\n</head>\n<body>\n{header}\n{body}\n{footer}\n</body>\n</html>\n"
    ).format(head=_head(title, desc, canonical, brand, extra_ld),
             header=_header(site, brand), body=body, footer=footer(site, brand))
    assert "—" not in doc and "&mdash;" not in doc, "em dash in " + canonical
    return doc


# ---------- HOME ----------
def render_home(brand, site, states, totals):
    n_counties, n_records, total = totals
    st = states  # list of dicts: name, slug, counties(list), records, total
    county_cards = []
    for s in st:
        for c in sorted(s["counties"], key=lambda x: -x["total"]):
            county_cards.append(
                '<a class="county" href="{site}/{ss}/{slug}/"><b>{name}, {ab}</b>'
                '<span class="meta">{n} records, {m}</span></a>'.format(
                    site=site, ss=s["slug"], slug=c["slug"], name=html.escape(c["county"]),
                    ab=c["state_abbr"], n=c["records"], m=_money(c["total"])))
    counties_html = "\n".join(county_cards)
    state_links = " ".join(
        '<a class="btn ghost" href="{site}/{ss}">{name} counties</a>'.format(
            site=site, ss=s["slug"], name=html.escape(s["name"])) for s in st)

    faq = [
        ("What are tax sale surplus funds?",
         "When a property is sold at a county tax sale for more than the taxes and costs owed, the leftover "
         "money is called surplus funds, excess funds, or overage. By law it belongs to the former owner or "
         "their heirs, not the county and not the person who bought the property at the sale."),
        ("How do I know if I am owed money?",
         "Pick your county from the directory below and search the published list for your name or the name "
         "of a relative whose property was sold. Each county page shows the owner, the amount, the parcel, "
         "and the sale date, straight from the county's own records."),
        ("Do I have to pay to claim my surplus funds?",
         "No. You can file a claim directly with the county for free, and you should never have to pay anyone "
         "to get your own money. Recovery firms and attorneys can handle the paperwork for a fee if you "
         "prefer help with a complicated estate or lien, but it is always optional."),
        ("Are you a government agency?",
         "No. We are an independent data service. We organize public records so they are easy to search. We "
         "are not affiliated with any county or government office, and we do not file claims for you."),
    ]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
    faq_html = "\n".join('<details class="faq"><summary>{}</summary><p>{}</p></details>'.format(
        html.escape(q), html.escape(a)) for q, a in faq)
    org_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": brand, "url": site + "/",
              "description": "Search county tax-sale surplus and excess funds lists by county."}

    body = """<main>
<section class="hero"><div class="wrap">
  <h1>Are you owed unclaimed surplus funds?</h1>
  <p class="lede">When a home is sold at a county tax sale for more than the taxes owed, the extra money belongs to the former owner. Billions of dollars sit unclaimed. Search your name below, or browse by county, and claim what is yours, for free.</p>
  <div class="search">
    <input type="search" id="namesearch" placeholder="Search your name across all counties..." aria-label="Search all counties by owner name" autocomplete="off">
    <div class="results" id="results" hidden></div>
  </div>
  <div class="cta-row"><a class="btn" href="#browse">Browse by county</a><a class="btn ghost" href="#how">How it works</a></div>
  <div class="stats">
    <div class="stat"><b>{nc}</b><span>counties tracked</span></div>
    <div class="stat"><b>{nr}</b><span>surplus records</span></div>
    <div class="stat"><b>{tot}</b><span>in surplus found</span></div>
    <div class="stat"><b>Free</b><span>to claim yourself</span></div>
  </div>
</div></section>

<section class="band" id="how"><div class="wrap">
  <h2>How it works</h2>
  <p class="sub">Three steps, no signup, no fee.</p>
  <div class="steps3">
    <div class="card"><div class="n">1</div><h3>Find your county</h3><p>Choose the county where the property was sold. We organize each county's official excess funds list into a searchable page.</p></div>
    <div class="card"><div class="n">2</div><h3>Search for your name</h3><p>Look for your name, or a relative's, in the list. Note the parcel number, sale date, and the amount held.</p></div>
    <div class="card"><div class="n">3</div><h3>Claim it from the county</h3><p>Follow the county's claim steps on the page. You can file directly, for free. We also point you to a vetted professional if you want help.</p></div>
  </div>
</div></section>

<section class="band alt"><div class="wrap">
  <h2>Honest by design</h2>
  <p class="sub">Counties warn people about pushy recovery firms, and for good reason. We do it differently.</p>
  <div class="steps3">
    <div class="card"><h3>You can always claim it free</h3><p>Every page shows you how to file the claim yourself, directly with the county, at no cost.</p></div>
    <div class="card"><h3>Data, not pressure</h3><p>We assemble public records into a clean, searchable format. We do not cold-call, and we never collect debts.</p></div>
    <div class="card"><h3>Real records, cited</h3><p>Every figure comes straight from the county's published list, with the source linked, so you can verify it.</p></div>
  </div>
</div></section>

<section class="band" id="browse"><div class="wrap">
  <h2>Browse surplus funds by county</h2>
  <p class="sub">Currently covering {nc} counties, with more on the way. {stlinks}</p>
  <div class="counties">
{counties}
  </div>
</div></section>

<section class="band alt"><div class="wrap">
  <h2>Frequently asked questions</h2>
{faq}
</div></section>
<script>
(function(){{
 var inp=document.getElementById('namesearch'),box=document.getElementById('results'),data=null,loading=false;
 function money(n){{return '$'+Number(n).toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});}}
 function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
 function render(q){{
  var t=q.toLowerCase(),out=[],i,e,seen=0;
  for(i=0;i<data.length&&seen<20;i++){{
   e=data[i];
   if(e.n.toLowerCase().indexOf(t)>-1){{
    seen++;
    out.push('<a href="'+e.u+'?q='+encodeURIComponent(e.n)+'#list"><span class="nm">'+esc(e.n)+'</span><span class="mt">'+esc(e.c)+', '+e.a+' &middot; '+money(e.o)+'</span></a>');
   }}
  }}
  if(!out.length){{out.push('<div class="empty">No matching names found. Try a last name only, or browse by county below.</div>');}}
  box.innerHTML=out.join('');box.hidden=false;
 }}
 function onInput(){{
  var q=inp.value.trim();
  if(q.length<2){{box.hidden=true;box.innerHTML='';return;}}
  if(data){{render(q);return;}}
  if(loading){{return;}} loading=true;
  fetch('/search-index.json').then(function(r){{return r.json();}}).then(function(j){{data=j;render(inp.value.trim());}}).catch(function(){{loading=false;}});
 }}
 inp.addEventListener('input',onInput);
 document.addEventListener('click',function(ev){{if(!box.contains(ev.target)&&ev.target!==inp){{box.hidden=true;}}}});
}})();
</script>
</main>""".format(site=site, nc=n_counties, nr="{:,}".format(n_records), tot=_money(total),
                  stlinks=state_links, counties=counties_html, faq=faq_html)

    return page("Your Surplus Funds: Search Unclaimed Tax Sale Surplus Funds by County",
                "Search county tax-sale surplus and excess funds lists. See if you are owed unclaimed money "
                "from a tax sale, and how to claim it free from the county.",
                site + "/", brand, site, body, [org_ld, faq_ld])


# ---------- STATE HUB ----------
def render_state_hub(brand, site, state):
    name, slug, counties = state["name"], state["slug"], state["counties"]
    records = sum(c["records"] for c in counties)
    total = sum(c["total"] for c in counties)
    canonical = "{}/{}".format(site, slug)
    rows = "\n".join(
        '<a class="county" href="{site}/{ss}/{slug}/"><b>{name} County</b>'
        '<span class="meta">{n} records, {m}</span></a>'.format(
            site=site, ss=slug, slug=c["slug"], name=html.escape(c["county"].replace(" County", "")),
            n=c["records"], m=_money(c["total"]))
        for c in sorted(counties, key=lambda x: -x["total"]))
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": site + "/"},
        {"@type": "ListItem", "position": 2, "name": name + " Surplus Funds", "item": canonical}]}
    law = state.get("law") or {"office": "county tax office", "window_short": "varies",
                               "window": "held by the county for several years before unclaimed funds transfer to the state, so claiming sooner is always better."}
    faq = [
        ("How long do I have to claim surplus funds in " + name + "?",
         "In " + name + ", tax-sale surplus is " + law["window"]),
        ("Who holds surplus funds in " + name + "?",
         "In " + name + ", tax-sale surplus is usually held by the " + law["office"] + " until a valid "
         "claim is filed and approved. Each county page lists the office and address for that county."),
    ]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in faq]}
    faq_html = "\n".join('<details class="faq"><summary>{}</summary><p>{}</p></details>'.format(
        html.escape(q), html.escape(a)) for q, a in faq)

    body = """<main class="wrap">
<nav class="crumb"><a href="{site}/">Home</a> &rsaquo; {name}</nav>
<h1>{name} Excess Funds List by County</h1>
<p class="sub">When a property is sold at a {name} tax sale for more than the taxes owed, the surplus (called excess funds or overage) belongs to the former owner or their heirs. Below is every {name} county we currently track, with the number of records and total surplus on each county's published list. Claiming is free, and each page shows you exactly how.</p>
<div class="stats">
  <div class="stat"><b>{nc}</b><span>counties covered</span></div>
  <div class="stat"><b>{nr}</b><span>surplus records</span></div>
  <div class="stat"><b>{tot}</b><span>total surplus</span></div>
  <div class="stat"><b>{winshort}</b><span>typical claim window</span></div>
</div>
<h2 style="margin-top:34px">Counties</h2>
<div class="counties">
{rows}
</div>
<div class="callout">More {name} counties are being added. If your county is not listed yet, you can still request its excess funds list directly from that county's tax office.</div>
<h2 style="margin-top:30px">Frequently asked questions</h2>
{faq}
</main>""".format(site=site, name=html.escape(name), nc=len(counties),
                  nr="{:,}".format(records), tot=_money(total), rows=rows, faq=faq_html, winshort=law["window_short"])

    return page("{} Excess Funds List by County: Unclaimed Tax Sale Surplus Funds".format(name),
                "See unclaimed {} tax-sale surplus and excess funds by county. {} counties, {} totaling {}. "
                "Check if you are owed money and how to claim it free.".format(
                    name, len(counties), "{:,} records".format(records), _money(total)),
                canonical, brand, site, body, [bc, faq_ld])


# ---------- TRUST PAGES ----------
def _trust(brand, site, slug, title, desc, inner):
    canonical = "{}/{}".format(site, slug)
    body = ('<main class="wrap"><nav class="crumb"><a href="{s}/">Home</a> &rsaquo; {t}</nav>'
            '<div class="prose"><h1>{t}</h1>{inner}</div></main>').format(
                s=site, t=html.escape(title), inner=inner)
    return page("{} | {}".format(title, brand), desc, canonical, brand, site, body)


def render_about(brand, site):
    inner = """
<p><strong>{b}</strong> exists to help everyday people find money that is already theirs. Every year, billions of dollars in tax-sale surplus funds go unclaimed across the United States, simply because former property owners never learn the money exists.</p>
<h2>What we do</h2>
<p>We collect excess funds lists that counties publish as public records, and we organize them into clean, searchable pages, one per county. Each record shows the former owner, the amount held, the parcel, and the sale date, sourced directly from the county. We add clear, county-specific instructions for claiming the money yourself.</p>
<h2>What we are not</h2>
<p>We are a data and information service. We are <strong>not</strong> a law firm, a financial advisor, a debt collector, or a recovery agency, and we are not affiliated with any county, state, or government office. We do not file claims, we do not represent claimants, and we do not take a cut of your money. If you choose to hire a recovery professional or attorney through a link on our site, that is entirely optional, and you can always claim your funds yourself for free.</p>
<h2>Why we built it honestly</h2>
<p>Counties actively warn residents about pushy asset-recovery firms that charge large fees for information that is free and public. We think there is a better way: make the records easy to find, tell people plainly how to claim their money at no cost, and only offer paid help to those who genuinely want it.</p>
<h2>How our data is compiled</h2>
<p>Each county list is parsed from that county's official published document (a PDF, spreadsheet, or web page) and dated to when we last checked it. Balances change as claims are paid, and lists are updated on the county's own schedule, so we always encourage you to verify current status with the county before filing.</p>
<p>Questions or corrections? <a href="{s}/contact">Contact us</a>.</p>
""".format(b=html.escape(brand), s=site)
    return _trust(brand, site, "about", "About Us",
                  "About {}: an independent data service that helps people find and claim unclaimed "
                  "tax-sale surplus funds for free.".format(brand), inner)


def render_contact(brand, site):
    inner = """
<p>We would love to hear from you. Whether you have a question about a listing, a correction to a record, or feedback on the site, send us a note.</p>
<h2>Email</h2>
<p><a href="mailto:{e}">{e}</a></p>
<p>We read every message and aim to reply within a few business days.</p>
<h2>Please note</h2>
<ul>
<li>We are a data service, so we cannot give legal or financial advice, confirm whether a specific claim will be approved, or file a claim on your behalf.</li>
<li>To actually claim surplus funds, you file directly with the county that holds them. Each <a href="{s}/georgia">county page</a> lists that county's office and address.</li>
<li>If you believe a record on our site is inaccurate or out of date, tell us the county and the name or parcel, and we will review it against the county's current list.</li>
</ul>
""".format(e=CONTACT_EMAIL, s=site)
    return _trust(brand, site, "contact", "Contact",
                  "Contact {}. Email us with questions, corrections, or feedback about county surplus funds "
                  "listings.".format(brand), inner)


def render_privacy(brand, site):
    today = datetime.date(2026, 7, 14).strftime("%B %-d, %Y")
    inner = """
<p><em>Last updated {d}.</em></p>
<p>This Privacy Policy explains how {b} (\"we\", \"us\") handles information when you visit our website. We keep data collection to a minimum and we do not sell your personal information.</p>
<h2>Information we collect</h2>
<p>We collect very little. When you visit the site, our hosting and content-delivery providers automatically log standard technical information such as your IP address, browser type, pages viewed, and the time of your visit, which helps us keep the site secure and understand general usage. If you email us, we receive the information you choose to share.</p>
<h2>Cookies and analytics</h2>
<p>We may use privacy-respecting analytics to understand aggregate traffic (for example, which pages are popular). We may also use advertising or affiliate partners whose cookies help measure referrals. You can control cookies through your browser settings. Because our specific analytics and advertising tools may change, this section describes our general practice; contact us if you would like details on the tools currently in use.</p>
<h2>How we use information</h2>
<ul>
<li>To operate, secure, and improve the website.</li>
<li>To respond to messages you send us.</li>
<li>To measure aggregate traffic and the performance of referral links.</li>
</ul>
<h2>Sharing</h2>
<p>We do not sell your personal information. We share limited technical data only with the service providers who help us run the site (such as hosting, analytics, and advertising partners), and only as needed for those services. We may disclose information if required by law.</p>
<h2>Your choices</h2>
<p>Depending on where you live, you may have rights to access, correct, or delete personal information we hold about you, or to opt out of certain data uses. To make a request, email us at <a href="mailto:{e}">{e}</a>. You can also use your browser to block or clear cookies.</p>
<h2>Public records</h2>
<p>The property records shown on this site come from government public records, not from you. If you are named in a public excess funds list and would like to discuss it, contact us and we will review it against the county's current published list.</p>
<h2>Children</h2>
<p>This site is not directed to children under 13, and we do not knowingly collect information from them.</p>
<h2>Changes</h2>
<p>We may update this policy from time to time. The \"last updated\" date above reflects the latest version.</p>
<h2>Contact</h2>
<p>Questions about this policy? Email <a href="mailto:{e}">{e}</a>.</p>
<p style="color:#5b6472;font-size:13px">This policy is provided for general information and is not legal advice.</p>
""".format(d=today, b=html.escape(brand), e=CONTACT_EMAIL)
    return _trust(brand, site, "privacy", "Privacy Policy",
                  "How {} collects, uses, and protects information on our website.".format(brand), inner)


def render_terms(brand, site):
    today = datetime.date(2026, 7, 14).strftime("%B %-d, %Y")
    inner = """
<p><em>Last updated {d}.</em></p>
<p>These Terms of Service (\"Terms\") govern your use of the {b} website. By using the site, you agree to these Terms. If you do not agree, please do not use the site.</p>
<h2>Informational purpose only</h2>
<p>The site provides publicly available information about tax-sale surplus and excess funds, organized for convenience. It is not legal, financial, tax, or professional advice, and using the site does not create an attorney-client or any other professional relationship. Always verify information with the relevant county and consult a qualified professional about your specific situation.</p>
<h2>No warranty on accuracy</h2>
<p>Records are compiled from public sources and may be incomplete, out of date, or contain errors. Balances change as claims are paid. We make no warranty that any listing is current, complete, or accurate, and the site is provided \"as is\" without warranties of any kind.</p>
<h2>You can claim funds yourself</h2>
<p>Surplus funds are claimed directly from the county that holds them, and doing so is free. We do not file claims or represent claimants. You are never required to use any third party to claim funds that belong to you.</p>
<h2>Third-party and affiliate links</h2>
<p>The site may link to third-party recovery professionals, attorneys, or other services. Some of these may be paid or affiliate arrangements, which means we may earn a commission if you engage them, at no additional cost to you. We do not control third parties and are not responsible for their services. A referral is not an endorsement or a guarantee of any outcome.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent permitted by law, {b} is not liable for any loss or damage arising from your use of, or reliance on, the site or its content, including any decision made based on a listing.</p>
<h2>Intellectual property</h2>
<p>The site's design, text, and original compilations are owned by {b}. Underlying public records are the property of their respective government sources. You may view and use listings for personal, lawful purposes.</p>
<h2>Acceptable use</h2>
<p>Do not use the site to harass individuals named in public records, to scrape or resell our compiled data in bulk without permission, or for any unlawful purpose.</p>
<h2>Changes</h2>
<p>We may update these Terms at any time. Continued use of the site after changes means you accept the updated Terms.</p>
<h2>Contact</h2>
<p>Questions about these Terms? Email <a href="mailto:{e}">{e}</a>.</p>
<p style="color:#5b6472;font-size:13px">These Terms are provided for general information and are not legal advice.</p>
""".format(d=today, b=html.escape(brand), e=CONTACT_EMAIL)
    return _trust(brand, site, "terms", "Terms of Service",
                  "The terms that govern your use of the {} website.".format(brand), inner)


def render_disclaimer(brand, site):
    inner = """
<p>{b} provides public-record information for general educational purposes. Please read the following carefully.</p>
<h2>Not legal or financial advice</h2>
<p>Nothing on this site is legal, financial, or tax advice. We are not a law firm or a financial advisor, and no attorney-client or fiduciary relationship is created by using the site. For advice about your specific situation, consult a licensed professional.</p>
<h2>Not a government agency</h2>
<p>We are an independent service and are not affiliated with, endorsed by, or connected to any county, state, or federal government office. Official excess funds are claimed through the county that holds them.</p>
<h2>Accuracy and timeliness</h2>
<p>Listings are compiled from public records and may be incomplete or out of date. Amounts and availability change as claims are processed. Always confirm current status with the county before acting.</p>
<h2>You can claim for free</h2>
<p>You never have to pay anyone to claim surplus funds that belong to you. You can file directly with the county at no cost.</p>
<h2>Affiliate disclosure</h2>
<p>Some links on this site, such as those to recovery professionals or attorneys, may be paid or affiliate links. If you use them, we may earn a commission at no extra cost to you. This never changes the free option to claim funds yourself, and a paid link is not an endorsement or a guarantee of results.</p>
<p>Questions? <a href="{s}/contact">Contact us</a>.</p>
""".format(b=html.escape(brand), s=site)
    return _trust(brand, site, "disclaimer", "Disclaimer",
                  "Important disclaimers for {}: not legal or financial advice, not a government agency, and "
                  "our affiliate disclosure.".format(brand), inner)
