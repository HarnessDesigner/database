# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Download the raw Molex part data that ``convert.py`` turns into the ``Molex/*.json`` files.

The part lists on molex.com (https://www.molex.com/en-us/part-list/<name>) are drawn from a public JSON search API at
search.molex.com. It answers plain requests (no cookies, no browser), so nothing here needs a web driver:

* ``products-per-category`` -- the rows of a part list. ``q`` is the last part of the part-list address
  (``connector-housings``, ``crimp-terminals`` ...) and ``fq=taxonomyPathValueLast:"..."`` narrows a broad list such
  as ``connectors`` down to one of its categories. A page can hold 2000 rows.
* ``productdetails`` -- one part. It carries what the list does not: the parts a part is used with
  (``useWithProduct`` -- terminals, seals, locks ...) and the parts it mates with (``matesWithProduct``).

Output goes to ``scrapers/molex/raw/`` (ignored by git):

* ``raw/<slug>.json``          -- every row of a category, as the API returns it
* ``raw/details/<slug>.json``  -- ``{part number: the useful part of its productdetails}`` for the categories that
                                  ask for it (see ``CATEGORIES``)

Usage (from anywhere)::

    python collect.py                  # every category, list rows only
    python collect.py --details        # also the per-part details (about 11,000 requests, a few minutes)
    python collect.py --only crimp_terminals splices --details

A download that is interrupted can simply be run again: details already on disk are skipped.
"""

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests


API = 'https://search.molex.com/api/search/'
LIST_ENDPOINT = 'products-per-category'
DETAIL_ENDPOINT = 'productdetails'

# Only parts Molex has published are listed on the website; the website adds this filter to every request.
PROMOTABLE = 'materialMaster.promotable:("true")'

PAGE_SIZE = 1000
DETAIL_THREADS = 6
RETRIES = 5

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, 'raw')
DETAIL_DIR = os.path.join(RAW_DIR, 'details')

# (slug, part-list address used as ``q``, ``taxonomyPathValueLast`` to filter on or None, download details?)
#
# Housings, accessories and terminals get details because the parts they are used with are what fill the
# ``compat_*`` columns. PCB headers and the cable categories do not: there are ~39,000 of them and nothing in the
# database refers to what they are used with.
#
# Left out on purpose (still reachable through the ``connectors`` list if they are ever wanted): I/O, board-to-board,
# FFC/FPC, RF/coaxial, D-Sub, backplane, memory and card-edge connectors, terminal blocks, heavy-duty and circular
# connectors, EMI cages -- none of those are wire-harness parts.
CATEGORIES = (
    ('connector_housings', 'connector-housings', None, True),
    ('pcb_headers', 'pcb-headers-and-receptacles', None, False),
    ('crimp_terminals', 'crimp-terminals', None, True),
    ('ring_spade_terminals', 'connectors', 'Ring and Spade Terminals', True),
    ('quick_disconnects', 'connectors', 'Quick Disconnects', True),
    ('splices', 'connectors', 'Splices', True),
    ('connector_accessories', 'connectors', 'Connector Accessories', True),
    ('wire_and_cable', 'wire-and-cable', None, False),
)

# What of a productdetails answer is kept in raw/details.
DETAIL_KEYS = ('useWithProduct', 'matesWithProduct', 'useWithSeries', 'matesWithSeries')
PRODUCT_KEYS = ('admin', 'digitalAssets', 'engineeringDocs')

_session = requests.Session()
_session.headers.update({'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0 (HarnessDesigner part collector)'})


def get_json(endpoint: str, params: list[tuple[str, str | int]]) -> dict:
    """GET ``endpoint`` and return the decoded JSON, retrying on network errors and server errors."""
    last_error = None

    for attempt in range(RETRIES):
        try:
            response = _session.get(API + endpoint, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as err:
            last_error = err
            time.sleep(2 ** attempt)

    raise RuntimeError(f'{endpoint} {params}: {last_error}')


def fetch_category(q: str, taxonomy: str | None) -> list[dict]:
    """Return every row of one part list, paging in ``PAGE_SIZE`` steps."""
    docs = []
    start = 0
    total = None

    while total is None or start < total:
        params = [('q', q), ('rows', PAGE_SIZE), ('start', start), ('sort', 'id asc'), ('fq', PROMOTABLE)]
        if taxonomy is not None:
            params.append(('fq', f'taxonomyPathValueLast:("{taxonomy}")'))

        product = get_json(LIST_ENDPOINT, params)['product']
        response = product['response']

        total = response['numFound']
        docs.extend(response['docs'])
        start += PAGE_SIZE

        print(f'    {len(docs)} / {total}')

    return docs


def fetch_detail(part_number: str) -> dict:
    """Return the useful part of the productdetails answer for one part."""
    data = get_json(DETAIL_ENDPOINT, [('q', part_number)])

    detail = {}
    for key in DETAIL_KEYS:
        detail[key] = data.get(key, [])

    products = data.get('products', [])
    if products:
        detail['product'] = {key: products[0].get(key, {}) for key in PRODUCT_KEYS}

    return detail


def write_json(path: str, data: list | dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    os.replace(path + '.tmp', path)


def collect_details(slug: str, docs: list[dict]) -> None:
    """Download the productdetails of every part in ``docs`` that is not on disk yet."""
    path = os.path.join(DETAIL_DIR, slug + '.json')

    details = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            details = json.load(f)

    todo = [doc['id'] for doc in docs if doc['id'] not in details]
    print(f'    details: {len(details)} on disk, {len(todo)} to download')

    lock = threading.Lock()
    done = [0]

    def work(part_number: str) -> None:
        detail = fetch_detail(part_number)

        with lock:
            details[part_number] = detail
            done[0] += 1

            if done[0] % 500 == 0:
                write_json(path, details)
                print(f'    details: {done[0]} / {len(todo)}')

    try:
        with ThreadPoolExecutor(max_workers=DETAIL_THREADS) as pool:
            list(pool.map(work, todo))
    finally:
        # keep what was downloaded even if one request gave up
        write_json(path, details)

    print(f'    details: {len(details)} parts saved')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--details', action='store_true', help='also download the per-part details')
    parser.add_argument('--only', nargs='+', metavar='SLUG', help='only these categories')
    args = parser.parse_args()

    slugs = [slug for slug, *_ in CATEGORIES]
    if args.only:
        unknown = [slug for slug in args.only if slug not in slugs]
        if unknown:
            sys.exit(f'unknown category {unknown}; choose from {slugs}')

    for slug, q, taxonomy, wants_details in CATEGORIES:
        if args.only and slug not in args.only:
            continue

        print(f'{slug}: q={q!r} taxonomy={taxonomy!r}')

        docs = fetch_category(q, taxonomy)
        if len({doc['id'] for doc in docs}) != len(docs):
            raise RuntimeError(f'{slug}: the API returned duplicate part numbers while paging')

        write_json(os.path.join(RAW_DIR, slug + '.json'), docs)

        if args.details and wants_details:
            collect_details(slug, docs)


if __name__ == '__main__':
    main()
