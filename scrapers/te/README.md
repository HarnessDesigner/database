# TE Connectivity scraper (rewrite started 2026-11-04)

Status: done. `collect.py` downloads, `convert.py` writes `TE/<table>.json`, `genders.py` fills gender from related parts. The
old scripts (`te_step1.py`, `te_step2.py`, `map_json.py`, `wires.py`, `housings.py`, `terminals.py` and the other per category
scripts) were removed on 2026-11-04; they are in the git history. The list below is the history of why they were replaced.

## The pipeline

1. `collect.py` downloads the harness related categories of TE's catalog into a raw folder (`--raw`, several GB, put it on a
   drive with room). One file per page of 100 products, resumable, verified at the end.
2. `convert.py` reads that folder, decides what each product is, and writes `TE/<table>.json` with
   `common.new_row`, the lookup checks and `common.write_rows`.

## Collecting (what was learned)

* TE's search API: `https://api.te.com/api/v1/search/service/search/products?ptp=y&n=<category id>&o=<offset>&s=100&storeid=TEUSA&c=usa&l=en&st=web&mediaType=jsonns&dist_region=North America`.
  `n` is a category id (the ids are in each product's `crumbTrail`); `o` is the offset. Every answer carries about 1.3 MB of
  facets that are dropped before saving. A product is about 30 KB.
* No cookie has to be pasted. A plain `requests` session receives TE's own `ak_bmsc` / `bm_sv` cookies and carries them. The
  `Accept` and `Accept-Language` headers matter: a request without `Accept-Language` got a 403.
* About 10 ms between requests is enough. The whole download (780 requests) took a few minutes. On a 403 / 429 the collector
  waits a minute, makes one fresh session and then stops; it never works around a block.
* Result (2026-11-04): 77,893 products in six categories, every one verified (the number of different records equals TE's total,
  no missing pages, no duplicates):

| folder | TE category (id) | products |
|---|---|---|
| connectors | Connectors (130453) | 52,447 |
| automotive | Automotive Parts (883095) | 7,078 |
| terminals_splices | Terminals & Splices (131119) | 6,802 |
| wire_cable | Wire & Cable (131142) | 6,713 |
| wire_protection | Wire Protection & Management (130846) | 3,556 |
| heat_shrink | Heat Shrink Tubing (130872) | 1,297 |

The rest of the catalog (about 90,000 resistors, relays, switches, sensors, tooling, antennas ...) is not wire harness material and
is not downloaded.

## Why the old data was wrong

* It was INCOMPLETE. The old download had 3,641 wire products against 6,713 now (hook up wire 1,538 against 2,990, twisted pair cable
  1,497 against 3,019). A resumable pager that adds a guessed offset after an interruption loses pages.
* `te_step2.py` sorted products by `parentCategory` alone, but one category holds several kinds of part (602 of the
  "Standard Rectangular Connectors" are caps, "Connector Hardware" holds latches, position assurance and mounting parts...).
  Everything it did not recognise went to a 4 GB `generic` pile. The CPA lock file ended with 0 rows.
* The per category scripts took the first value they met, ignored units, left `compat_*` empty, never set splice wire sizes,
  strands or wire types, and `Number of Conductors` was read from one place only with a test that could never be true
  (every TE wire had 1 conductor).

## What TE's JSON looks like (be careful)

* A field is identified by its attribute `code` AND unit, not its label. `Wire Size` is three fields (mm² `901888`, AWG `901889`,
  CMA `905460`) and `Operating Voltage` two (VAC, V). The mm² one can be empty while AWG is filled.
* The same field appears in `primaryFeatures` and again in a `featureGroups` entry. For the same field id the values never
  disagree (0 conflicts in 39,264 instances); some fields exist in only one of the two places (`Number of Conductors` is mostly
  only in a group). Fields are optional: every lookup needs a default, and a field can exist for one part and not another.
* DIFFERENT fields of one part do disagree: AWG against mm² (115 of 779 differ by more than 12%, the AWG is a rounded stand-in
  for a metric size, trust mm²); conductor count against the colour list (colours are a sorted set, the order is in the part
  number's colour code); `Shielded` missing on parts that have a shield material.
* `partType` is `regular`, `derived` or `model`. A `model` is a family page (its part number starts `CAT-`, its dimensions are a
  list of sizes) and is not a part.
* Two records can share a marketing part number (`marketingPartNumNormalized`) with different `tcpn` (TE's internal number):
  287 in Wire & Cable, 10 in Wire Protection, 2 in Connectors, 1 in Heat Shrink. A record is identified by `tcpn`.
* TE's `Centerline (Pitch)` and `Cable Insulation Width` are present for ribbon cable (0.64 mm and 12.7 mm on 20WBY00001).

## Proposed classification (separate by the product's own features, never the category alone)

| table | what goes in |
|---|---|
| housings | `Automotive Housings`, `Data Connectivity Housings`, `Crimp Terminal Housings`, `Standard Rectangular / Circular / D-Shaped / Circular Power / Coax / Ribbon Cable` connectors whose `Connector & Housing Type` is a housing, plug, receptacle, jack, tab housing or hermaphroditic, `Rectangular Connector Hoods & Bases` (Base Housing) |
| covers | `Connector & Housing Type` = Cap (in any connector category), `Automotive Connector Caps & Covers`, `Connector Caps & Covers`, `Rectangular Connector Hoods & Bases` (Hood, Cover), `Connector Backshells` |
| terminals | `Automotive Terminals`, `Connector Contacts`, `RF Contacts`, `Ring / Spade / Magnet Wire / Power / Special Purpose` terminals, `Quick Disconnects`, `Crimp Wire Pins, Tabs & Ferrules` |
| splices | `Splices`, `Junction Splices`, `Cable-to-Cable Splicing`, `SolderSleeve Shield Terminators` (Splice Type / Interconnect Device Splice Type) |
| seals | `Connector Seals & Cavity Plugs`, `Cable Entry Seals` |
| tpa_locks | `Connector & Contact Retention Accessory Type` = TPA, Secondary Lock, Retainer, Double Lock Plate (and Connector Hardware with Position Assurance for terminals) |
| cpa_locks | the same field = CPA, Latch Arm (and Connector Hardware Position Assurance for connectors) |
| boots | `Heat Shrink Boots`, `EMI Shielded Boots`, `Connector Strain Relief` |
| bundles | `Heat Shrink Tubing`, `Heat Shrink Kits`, `Cable Braids`, tapes, `Sealing Sleeves`, `Cable Conduit`, `Wiring Ducts` |
| wires | `Twisted Pair Cable`, `Hook Up Wire`, `Power Cable`, `High Speed Digital & Data Cable`, `Sensor Cable`, `Primary Wire`, `Multicore Cable`, `Ribbon & Flat Cable` (not `Oriented Wire`, an EMI gasket) |
| accessories | `Connector Hardware` (latching, mounting, keying, guide), `Other Automotive Connector Accessories`, `Automotive Connector EMC Shielding`, `Cable Ties`, `Cable Tie Mounts` |
| not built | `model` records, everything outside a table above |

## Decisions (user, 2026-11-04)

* BOARD LEVEL PARTS: "if it mates to a board connector keep it, if it doesn't remove it". Read as: keep a connector that takes part
  in a wire or cable to board connection (its `Connector System` has a Wire / Cable / Bus Bar side: Wire-to-Board, Cable-to-Board,
  Wire-to-Wire ...), on either side (the wire connector and the header it plugs into); leave out board-to-board connectors, sockets
  (DIMM, DIP, SIM ...), edge and backplane connectors and anything else with no wire or cable side. (Interpretation, to be
  confirmed.)
* SAME MARKETING PART NUMBER, DIFFERENT `tcpn`: keep the part number. When another record has the same number, compare the DATA
  (the converted rows without the part number): if it is the same, drop the duplicate; if it is not, append the other record's
  number to the part number with a `-` (`PN-<tcpn>`). The record with the lowest `tcpn` keeps the plain number, so the result
  does not depend on the download order. The report counts both cases.
* TRANSITIONS: check each `Cable Transitions & Breakouts` part against `Universal/transitions.json`. A part number that is already
  there is removed from the list; one that is not is written, with its data, to a separate file for later inspection (it is not
  loaded by the builder).

* SPLICE OR TERMINAL: a part that joins wires with the connection in the middle of one of them is a splice, any other part fitted
  to a wire is a terminal. So `Compression Connectors` are terminals (types Splice, Sleeve and Branch Connector are splices),
  `Joints & Splices` and `Wedge Connectors` are splices (a live end seal or motor connection kit is a terminal, a link box is left
  out), `SolderSleeve Shield Terminators` that are not SolderSleeves are terminals, and a `Power Cable Termination` is a terminal for
  one core and a housing for two or more (no core count: terminal). `Rectangular Contact Inserts` (the contact carrier of
  a Raychem MTC or Deutsch connector, pin or socket) are housings.
* MANUFACTURER: TE's `brand` is the manufacturer (Raychem, AMP, Deutsch, Simel, ERNI ...), each one its own row in
  `Universal/manufacturers.json`, whose description says it is a TE Connectivity company. A terminal's colour stays empty (it
  follows the material).
* GENDER: a housing and the terminals that fit it have the same gender. `genders.py` fills the gender TE does not state by a
  breadth first search over the related-products answers (housing -> terminals -> their housings ...) that remembers the parts it
  has visited. Run `convert.py --cache C`, then `genders.py --out OUT --cache C --fetch`, then `convert.py --cache C` again.

## Open

* A twisted pair's turns per inch (`tpi`): TE gives the style (Twisted Pair / Triple) but not the lay, so it stays 0 until the
  user decides.
