# Manufacturer part scrapers

Each manufacturer has a folder here with two scripts:

* `collect.py` downloads the manufacturer's catalog into `raw/` (git-ignored, re-created by running it again).
* `convert.py` turns `raw/` into `<Manufacturer>/<table>.json` in the repo root, in the layout the builder's loaders read
  (`housings.json`, `terminals.json`, `seals.json`, `covers.json`, `boots.json`, `tpa_locks.json`, `cpa_locks.json`,
  `splices.json`, `bundles.json`, `wires.json`, `accessories.json`). Every row has exactly the keys of the matching
  `add_<part>()` function.

`common.py` holds what they share: row templates with all of the `add_*` defaults (`new_row` refuses an unknown key),
the checks against the `Universal` lookup tables (a colour, plating, gender, ... that is not in them would make the
builder add a row, so it is reported instead), the `compat_*` linker and the JSON writer.

Run them from their own folder: `python collect.py`, then `python convert.py`. Both print a summary; `convert.py` also
prints a `warning` line for every value it could not map to a lookup table.

## Status

| Manufacturer | Status | Where the data comes from |
|---|---|---|
| Molex | done (50,000+ parts) | `search.molex.com/api/search` JSON (open), part-detail relations for the `compat_*` lists |
| Yazaki | done (2,477 parts) | `connector.yazaki-group.com` search page (the result set is embedded as a script array) and one detail page per part |
| KET | done (5,356 parts) | `ket.com/en/product/feature-search.ket` JSON (needs the session cookie the site sets) and the product pages for the 2D / 3D file links |
| Aptiv, Bosch, TE | older scrapers in `aptiv/`, `bosch/`, `te/` | |
| Amphenol | not runnable | `amphenol/scraper.py` is a set of captured requests for the amphenol-cs.com Magento GraphQL; that site answers the collector's client with 403 (bot protection), which is not worked around |
| JAE, Wurth Elektronik, amphenol.com | blocked | the start pages answer 403 "Access Denied" / a challenge page to plain requests; not worked around |
| Harting | possible, not built | industrial Han connectors; the list pages load further products ("Load more") through `webapi.harting.com`, whose subscription key is part of the page's own configuration |
| Radiall | not built | Magento store of RF, microwave and aerospace parts; no open GraphQL endpoint |
| Rosenberger, ITT Cannon, Glenair | not built | series level pages, configurators and PDF catalogs; no part level listing found |
| FIT / Foxconn Interconnect | not built | part pages exist (`MySpace/PrdInfo.php?sn=fit&pc=...`, with positions, colour, plating) but no page links to them: the lists are filled by the CMS's script |
| Luxshare, BizLink, Foxlink, Lear, Leoni, Sumitomo Electric, YEU (Yamaichi) | nothing to scrape | corporate / solution pages, or harness and cable assembly makers; no parts catalog on the sites' navigation |

## Adding a manufacturer

1. Find the data source (the browser's network tab shows what the part-list pages call).
2. `collect.py`: download to `raw/` and make it resumable; keep to a few threads.
3. `convert.py`: build rows with `common.new_row(table, ...)`, link related parts with `common.fill_compat`, write with
   `common.write_rows(<repo>/<Manufacturer>, rows)` and finish with `common.report(catalog)`.
4. Add the manufacturer to `Universal/manufacturers.json` (the loaders create a blank row otherwise).
5. Build the database once (`python builder/build_database.py --output <scratch folder>`): it must finish without warnings
   and `PRAGMA foreign_key_check` must be empty.
