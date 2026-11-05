# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Download TE's catalog into ``raw/``: one file per page of 100 products.

    python collect.py [--raw FOLDER] [--only all] [--max-pages N] [--verify-only]

By default (``all``) the WHOLE catalog is paged with no category filter, about 167,000 products. That is needed: a listing
by category (``n=<category id>``, still available with ``--only connectors,wire_cable ...``) does not return the parts that
have no category at all (an active seal or a heat shrink part can be ``None > None``), nor the ``derived`` variants of a
family. Each folder gets ``page_<offset>.json`` files (the products of that page, nothing else: the facets that TE sends
with every answer are about 1.3 MB and are dropped) and ``manifest.json``. ``convert.py`` reads the folders.

* No cookie is needed. A plain ``requests`` session gets TE's own ``ak_bmsc`` / ``bm_sv`` cookies from the first answers
  and carries them, which is all the old script's ``handlecookie()`` did by hand. The ``Accept`` and ``Accept-Language``
  headers do matter: TE answered 403 to a request that left ``Accept-Language`` out.
* It waits ``DELAY`` between requests. TE stone-walls a client that is too fast, and about 10 ms is all it needs.
* It is resumable: a page that is already on disk is not fetched again. Pages are written atomically.
* On a 403 / 429 it waits a minute and starts a fresh session ONCE; a second refusal stops the run (run it again later,
  it carries on where it stopped). It does not try to get around a block.
* At the end each category is checked: the number of different parts found has to match the total TE reported.

The raw download is several GB, so put ``--raw`` on a drive with room (the default is ``raw/`` next to this file, which is
git-ignored).
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common  # NOQA: E402


# Seconds between two requests. TE needs only about 10 ms, but not much less.
DELAY = 0.01
PAGE_SIZE = 100

SEARCH_URL = 'https://api.te.com/api/v1/search/service/search/products'
PARAMS = {'ptp': 'y', 'storeid': 'TEUSA', 'c': 'usa', 'l': 'en', 'st': 'web', 'mediaType': 'jsonns',
          'dist_region': 'North America'}

# folder name -> (TE's name, category id for the ``n`` parameter). The ids are the ones in a product's ``crumbTrail``.
# Only the categories that can hold wire harness parts: housings, terminals, seals, covers, boots, locks, splices,
# heat shrink and wire. The resistors, relays, switches, sensors and tooling that make up most of the catalog are left out.
CATEGORIES = {
    'all': ('Every product, no category filter', None),
    'connectors': ('Connectors', '130453'),
    'automotive': ('Automotive Parts', '883095'),
    'terminals_splices': ('Terminals & Splices', '131119'),
    'wire_cable': ('Wire & Cable', '131142'),
    'wire_protection': ('Wire Protection & Management', '130846'),
    'heat_shrink': ('Heat Shrink Tubing', '130872'),
}

DEFAULT_RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')


class Blocked(RuntimeError):
    """TE refused two requests in a row (a fresh session did not help)."""


def new_session():
    session = common.make_session()
    session.headers.update({'Accept': 'application/json, text/plain, */*'})
    return session


def part_key(product: dict) -> str | None:
    """What makes a product one record: TE's internal part number (``tcpn``). Two products can share a marketing part
    number (``marketingPartNumNormalized``) and still be different records, so that cannot be the key."""
    return product.get('tcpn') or product.get('id') or product.get('marketingPartNumNormalized')


def write_atomic(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    os.replace(path + '.tmp', path)


class Collector:

    def __init__(self, raw_dir: str, delay: float = DELAY, page_size: int = PAGE_SIZE) -> None:
        self.raw_dir = raw_dir
        self.page_size = page_size
        self.delay = delay
        self.session = new_session()
        self.requests = 0
        self._last = 0.0

    def get_page(self, node: str | None, offset: int, **extra) -> dict:
        """One page of one category (or of one model's parts, ``model=<tcpn>``). Raises :class:`Blocked` when TE refuses
        twice."""
        params = dict(PARAMS, o=offset, s=self.page_size, **extra)

        if node:
            params['n'] = node

        for attempt in (1, 2):
            wait = self.delay - (time.time() - self._last)

            if wait > 0:
                time.sleep(wait)

            try:
                self._last = time.time()
                self.requests += 1
                response = common.fetch(self.session, SEARCH_URL, params=params)
                return response.json()
            except PermissionError as err:
                if attempt == 2:
                    raise Blocked(str(err)) from err

                print(f'  TE refused the request ({err}); waiting a minute, then one fresh session', flush=True)
                time.sleep(60)
                self.session = new_session()

        raise Blocked('unreachable')

    def collect(self, slug: str, max_pages: int | None = None, folder_name: str | None = None) -> None:
        name, node = CATEGORIES[slug]
        folder = os.path.join(self.raw_dir, folder_name or slug)
        offset = 0
        total = None
        pages = 0
        started = time.time()

        while total is None or offset < total:
            path = os.path.join(folder, f'page_{offset:07d}.json')

            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    page = json.load(f)
            else:
                answer = self.get_page(node, offset)
                results = answer['results']
                products = results.get('products') or []
                page = {'category': name, 'node': node, 'offset': offset,
                        'total': int(results['pagingLinks']['totalRecords']), 'products': products}

                if not products and offset < page['total']:
                    # a page that comes back empty is a gap; do not store it, carry on and let verify() report the hole
                    print(f'  {slug}: offset {offset} came back empty', flush=True)
                else:
                    write_atomic(path, page)

                pages += 1

                if pages % 10 == 0:
                    print(f'  {slug}: {offset + self.page_size}/{page["total"]}  ({self.requests} requests, '
                          f'{time.time() - started:.0f}s)', flush=True)

            total = page['total']
            offset += self.page_size

            if max_pages is not None and pages >= max_pages:
                print(f'  {slug}: stopped after {pages} page(s) (--max-pages)', flush=True)
                break

        write_atomic(os.path.join(folder, 'manifest.json'),
                     {'category': name, 'node': node, 'total': total, 'page_size': self.page_size,
                      'saved': time.strftime('%Y-%m-%d %H:%M:%S')})


def model_families(raw_dir: str) -> list[tuple[str, int]]:
    """``(model tcpn, number of derived parts)`` of every model family found in the whole-catalog folders."""
    families = {}

    for folder in sorted(os.listdir(raw_dir)):
        if not folder.startswith('all'):
            continue

        path = os.path.join(raw_dir, folder)

        for file_name in os.listdir(path):
            if file_name.startswith('page_') and file_name.endswith('.json'):
                with open(os.path.join(path, file_name), 'r', encoding='utf-8') as f:
                    for product in json.load(f)['products']:
                        if product.get('partType') == 'model' and product.get('browsableDerivedPartCnt'):
                            families[product['tcpn']] = product['browsableDerivedPartCnt']

    return sorted(families.items())


def collect_models(collector: 'Collector', max_models: int | None = None) -> bool:
    """The whole-catalog listing returns a family (``partType`` model, ``CAT-...``) but almost none of its ``derived``
    parts; those are what the family page lists (``search/products?model=<tcpn>``). Fetch them per family into
    ``derived/``. Returns True when every family's count matches what TE reported for it."""
    families = model_families(collector.raw_dir)
    folder = os.path.join(collector.raw_dir, 'derived')
    print(f'{len(families)} model families with derived parts', flush=True)
    started = time.time()
    done = 0
    wrong = []

    for index, (model, count) in enumerate(families, 1):
        safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in model)
        offset = 0
        total = None
        parts = 0

        while total is None or offset < total:
            path = os.path.join(folder, f'page_{safe}_{offset:06d}.json')

            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    page = json.load(f)
            else:
                results = collector.get_page('0', offset, model=model)['results']
                products = results.get('products') or []
                page = {'model': model, 'offset': offset, 'total': int(results['pagingLinks']['totalRecords']),
                        'products': products}
                write_atomic(path, page)

            total = page['total']
            parts += len(page['products'])
            offset += collector.page_size

            if not page['products']:
                break

        if parts != total or total < count:
            wrong.append((model, count, total, parts))

        done += 1

        if index % 50 == 0:
            print(f'  models {index}/{len(families)}  ({collector.requests} requests, {time.time() - started:.0f}s)',
                  flush=True)

        if max_models is not None and done >= max_models:
            break

    print(f'families whose parts did not all come back: {len(wrong)}')

    for model, count, total, parts in wrong[:10]:
        print(f'  {model}: family said {count}, search total {total}, got {parts}')

    return not wrong


def main() -> None:
    """Check that every category on disk has all its pages and that its parts match the total TE reported."""
    ok = True

    for slug in slugs:
        name, node = CATEGORIES[slug]
        folder = os.path.join(raw_dir, slug)

        if not os.path.isdir(folder):
            print(f'{slug:18} not downloaded')
            ok = False
            continue

        parts = {}
        duplicates = 0
        marketing = {}
        total = None
        offsets = set()

        for file_name in sorted(os.listdir(folder)):
            if not file_name.startswith('page_') or not file_name.endswith('.json'):
                continue

            with open(os.path.join(folder, file_name), 'r', encoding='utf-8') as f:
                page = json.load(f)

            total = page['total']
            offsets.add(page['offset'])

            for product in page['products']:
                key = part_key(product)

                if key in parts:
                    duplicates += 1

                parts[key] = parts.get(key, 0) + 1
                marketing.setdefault(product.get('marketingPartNumNormalized'), set()).add(key)

        if total is None:
            print(f'{slug:18} no pages')
            ok = False
            continue

        expected = set(range(0, total, PAGE_SIZE))
        missing_pages = sorted(expected - offsets)
        status = 'OK' if not missing_pages and not duplicates and len(parts) == total else 'CHECK'

        if status != 'OK':
            ok = False

        shared = sum(1 for keys in marketing.values() if len(keys) > 1)
        print(f'{slug:18} {status:5} TE total {total:6}  different parts {len(parts):6}  duplicates {duplicates:4}  '
              f'missing pages {len(missing_pages)}  (marketing part numbers shared by several records: {shared})')

        if missing_pages:
            print(f'{"":18} missing offsets: {missing_pages[:8]}{" ..." if len(missing_pages) > 8 else ""}')

    return ok


def verify_union(raw_dir: str) -> bool:
    """All folders of the whole-catalog passes together: do they hold every part TE reported?"""
    parts = set()
    total = None
    folders = [f for f in sorted(os.listdir(raw_dir)) if f.startswith('all')]

    for folder in folders:
        path = os.path.join(raw_dir, folder)

        for file_name in os.listdir(path):
            if file_name.startswith('page_') and file_name.endswith('.json'):
                with open(os.path.join(path, file_name), 'r', encoding='utf-8') as f:
                    page = json.load(f)

                total = page['total']
                parts.update(part_key(p) for p in page['products'])

    if total is None or len(folders) < 2:
        return False

    print(f'union of {", ".join(folders)}: TE total {total}, different parts {len(parts)}, '
          f'still missing {total - len(parts)}')
    return len(parts) >= total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--raw', default=DEFAULT_RAW, help='folder for the downloaded pages')
    parser.add_argument('--only', help='comma separated folder names (' + ', '.join(CATEGORIES) + '); default: all')
    parser.add_argument('--max-pages', type=int, help='stop each category after this many NEW pages (for testing)')
    parser.add_argument('--delay', type=float, default=DELAY, help='seconds between requests')
    parser.add_argument('--page-size', type=int, default=PAGE_SIZE,
                        help='products per request; the paging overlaps a little, so a second pass with another size '
                             '(into another --folder) fills the parts the first one missed')
    parser.add_argument('--folder', help='folder name inside --raw (default: the category name)')
    parser.add_argument('--models', action='store_true', help="fetch the derived parts of every model family found in --raw's whole-catalog folders (into derived/)")
    parser.add_argument('--max-models', type=int, help='with --models: stop after this many families (for testing)')
    parser.add_argument('--verify-only', action='store_true', help='only check what is on disk')
    args = parser.parse_args()

    slugs = [s.strip() for s in args.only.split(',')] if args.only else ['all']

    if args.models:
        try:
            sys.exit(0 if collect_models(Collector(args.raw, args.delay, args.page_size), args.max_models) else 1)
        except Blocked as err:
            sys.exit(f'\nSTOPPED: {err}\nTE is refusing requests. Run this again later; it carries on where it stopped.')

    for slug in slugs:
        if slug not in CATEGORIES:
            sys.exit(f'unknown category {slug!r}; choose from {", ".join(CATEGORIES)}')

    if not args.verify_only:
        collector = Collector(args.raw, args.delay, args.page_size)

        try:
            for slug in slugs:
                print(f'{slug}: {CATEGORIES[slug][0]}', flush=True)
                collector.collect(slug, args.max_pages, args.folder)
        except Blocked as err:
            print(f'\nSTOPPED: {err}\nTE is refusing requests. Run this again later; it carries on where it stopped.')
            verify(args.raw, slugs)
            sys.exit(1)

    print()
    ok = verify(args.raw, slugs)
    union_ok = verify_union(args.raw)
    sys.exit(0 if (ok or union_ok) or args.max_pages else 1)


if __name__ == '__main__':
    main()
