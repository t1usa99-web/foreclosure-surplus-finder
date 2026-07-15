# -*- coding: utf-8 -*-
"""Per-county source + parse configuration for the harvester.
'method': direct (fixed file url) | html (fetch landing page, extract file link) | firecrawl (JS-rendered, budget-capped).
'auto': True lets the harvester overwrite this county's data; False = monitor only (detect source change, do not reparse).
County metadata (office address, statute, etc.) is preserved from the existing data/counties/<slug>.json."""

COUNTIES = [
    {"slug": "coweta-county-ga", "method": "direct", "kind": "pdf", "parser": "coweta", "auto": True,
     "url": "https://www.cowetataxcom.com/resources/sites/cowetacountyga/docs/Excess%20Funds%20List.pdf"},
    {"slug": "hall-county-ga", "method": "html", "kind": "pdf", "parser": "hall", "auto": True,
     "url": "https://hallcountytax.org/property/excess-funds/",
     "link_re": r'href="([^"]+[Ee]xcess[^"]+\.pdf)"'},
    {"slug": "gwinnett-county-ga", "method": "html", "kind": "pdf", "parser": "gwinnett", "auto": True,
     "url": "https://www.gwinnetttaxcommissioner.com/property-tax/tax-sale-excess-funds",
     "link_re": r'href="([^"]*excess-funds-all-years[^"]*)"'},
    {"slug": "cobb-county-ga", "method": "firecrawl", "kind": "xlsx", "parser": "cobb", "auto": True,
     "url": "https://www.cobbtax.gov/property/delinquent_taxes/index.php",
     "note": "xlsx link is JS-injected; needs Firecrawl or Chrome to discover"},
    {"slug": "dekalb-county-ga", "method": "direct", "kind": "pdf", "parser": "dekalb", "auto": True,
     "url": "https://dekalbtax.org/wp-content/uploads/Excess-Funds-List.pdf"},
    {"slug": "clayton-county-ga", "method": "direct", "kind": "pdf", "parser": "clayton", "auto": True,
     "url": "https://publicaccess.claytoncountyga.gov/content/PDF/DQ759GA.pdf"},
    {"slug": "henry-county-ga", "method": "direct", "kind": "pdf", "parser": "henry", "auto": True,
     "url": "https://www.henrycountytax.com/DocumentCenter/View/296/Excess-Funds-List"},
    {"slug": "athens-clarke-county-ga", "method": "direct", "kind": "pdf", "parser": "athens", "auto": True,
     "url": "https://www.accgov.com/DocumentCenter/View/16566"},
]
