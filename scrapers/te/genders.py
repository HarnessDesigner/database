# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Find the gender of housings and terminals that TE does not state, from the parts they fit.

    python genders.py --out FOLDER --cache FOLDER [--fetch] [--limit N]

A housing and every terminal that fits it have the same gender (user, 2026-11-04). So a terminal of unknown gender takes the
gender of a housing it fits, a housing of unknown gender takes the gender of a terminal that fits it, and when that part's
gender is not known either, the search goes on from it: its own housings or terminals, and theirs, and so on. It is a
breadth first search that remembers the parts it has been to, so it cannot loop. Everything found in one search is
connected, so all the unknown parts it passed get the gender it ended with.

The links come from TE's related-products answer for a part (``Associated`` parts: terminals of a housing, housings of a
terminal; ``Mating`` parts are the opposite gender and are not used). That answer is downloaded only for the parts the search
needs and kept in ``CACHE/related/``, so a run can be stopped and continued. ``convert.py --cache CACHE`` writes the index this
reads (``tcpn_index.json``) and applies the result (``genders.json``).

Without ``--fetch`` only the answers that are already in the cache are used.
"""

import argparse
import collections
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # NOQA: E402
from collect import Blocked, new_session  # NOQA: E402


RELATED_URL = 'https://api.te.com/api/v1/search/service/product/related-products'
PARAMS = {'c': 'usa', 'l': 'en', 'dist_region': 'North America', 's': 100, 'mediaType': 'jsonns', 'has_ida': 'y',
          'storeid': 'TEUSA'}
DELAY = 0.01
MAX_PAGES = 5            # a part that lists more than 500 related parts and no partner on the first pages is not searched further
GENDERS = ('Male', 'Female')


def safe_name(tcpn: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]', '_', tcpn)


class Related:
    """The related parts of a part, from the cache or (with ``fetch``) from TE.

    An item is ``[tcpn, marketing part number, category, relation]``.
    """

    def __init__(self, cache: str, fetch: bool, delay: float = DELAY) -> None:
        self.folder = os.path.join(cache, 'related')
        self.fetch = fetch
        self.delay = delay
        self.session = new_session()
        self.requests = 0
        self.errors = 0
        self._last = 0.0
        os.makedirs(self.folder, exist_ok=True)

    def _path(self, tcpn: str) -> str:
        return os.path.join(self.folder, safe_name(tcpn) + '.json')

    def _page(self, tcpn: str, offset: int) -> dict:
        params = dict(PARAMS, tcpn=tcpn, o=offset)

        for attempt in (1, 2):
            wait = self.delay - (time.time() - self._last)

            if wait > 0:
                time.sleep(wait)

            try:
                self._last = time.time()
                self.requests += 1
                return common.fetch(self.session, RELATED_URL, params=params, retries=2).json()
            except PermissionError as err:
                if attempt == 2:
                    raise Blocked(str(err)) from err

                print(f'  TE refused the request ({err}); waiting a minute, then one fresh session', flush=True)
                time.sleep(60)
                self.session = new_session()

        raise Blocked('unreachable')

    def get(self, tcpn: str, enough=None) -> list[list] | None:
        """The related parts, or ``None`` when they are not in the cache and fetching is off.

        ``enough(items)`` says whether the items so far are what the caller needs; if not, the next pages (the answer comes
        100 at a time) are read, up to ``MAX_PAGES``.
        """
        path = self._path(tcpn)
        entry = None

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                entry = json.load(f)

        if entry is not None and (enough is None or enough(entry['items']) or entry['pages'] >= MAX_PAGES
                                  or len(entry['items']) >= entry['total'] or not self.fetch):
            return entry['items']

        if not self.fetch:
            return None

        if entry is None:
            entry = dict(total=0, pages=0, items=[])

        while True:
            try:
                data = self._page(tcpn, entry['pages'] * 100)
                content = (data.get('results') or {}).get('compatibleProducts') or {}
            except RuntimeError as err:
                # TE does not know the part (400) or the answer was not usable: remember it, do not ask again
                self.errors += 1
                entry['error'] = str(err)[-120:]
                entry['total'] = len(entry['items'])
                break

            products = content.get('products') or []
            entry['total'] = (content.get('pagingLinks') or {}).get('totalRecords', len(products))
            entry['pages'] += 1
            entry['items'] += [[p.get('tcpn'), p.get('marketingPartNumNormalized'), p.get('parentCategory'),
                                p.get('relationType')] for p in products]

            if not products or len(entry['items']) >= entry['total'] or entry['pages'] >= MAX_PAGES \
                    or (enough is not None and enough(entry['items'])):
                break

        common.write_json(path, entry)
        return entry['items']


def resolve(known: dict[str, str | None], kind: dict[str, str], related: Related, limit: int,
            save=None) -> tuple[dict[str, str], collections.Counter]:
    """The genders of the parts in ``known`` whose gender is not ``Male`` / ``Female``.

    :param known: tcpn -> gender (``None`` / ``Unknown`` when TE does not say) of every housing and terminal.
    :param kind: tcpn -> ``housings`` / ``terminals``.
    :param related: where the related parts come from.
    :param limit: the most downloads one search may use before it is given up (the search is not marked as finished).
    :param save: called now and then with the genders found so far.
    :returns: ``({tcpn: gender}, statistics)``
    """
    adjacency = collections.defaultdict(set)
    loaded = set()
    found: dict[str, str] = {}
    dead: set[str] = set()
    stats = collections.Counter()

    def partner(node: str, item: list) -> bool:
        other = item[0]
        relation = (item[3] or '').lower()
        return other in kind and kind[other] != kind[node] and 'mat' not in relation

    def expand(node: str) -> bool:
        """Read the related parts of ``node`` into the adjacency; ``True`` if it needed a download."""
        if node in loaded:
            return False

        before = related.requests
        items = related.get(node, enough=lambda items: any(partner(node, item) for item in items))
        loaded.add(node)

        if items is None:
            stats['not in the cache'] += 1
            return False

        for item in items:
            if partner(node, item):
                adjacency[node].add(item[0])
                adjacency[item[0]].add(node)

        return related.requests != before

    def gender_of(node: str) -> str | None:
        value = found.get(node) or known.get(node)
        return value if value in GENDERS else None

    starts = sorted(tcpn for tcpn in known if known[tcpn] not in GENDERS)
    done = 0

    for start in starts:
        done += 1

        if start in found or start in dead:
            continue

        seen = {start}
        queue = collections.deque([start])
        result = None
        downloads = 0
        truncated = False

        while queue and result is None:
            node = queue.popleft()

            if node not in loaded:
                if downloads >= limit:
                    truncated = True
                    break

                if expand(node):
                    downloads += 1

            for other in sorted(adjacency[node]):
                if other in seen:
                    continue

                seen.add(other)

                if other in dead:
                    continue

                value = gender_of(other)

                if value:
                    result = value
                    break

                queue.append(other)

        if result:
            for node in seen:
                if gender_of(node) is None:
                    found[node] = result
                    stats[f'{kind[node]} {result}'] += 1
        elif truncated:
            stats['search given up (too many downloads)'] += 1
        else:
            dead |= seen
            stats['no part with a gender found'] += len(seen)

        if done % 200 == 0:
            print(f'  {done}/{len(starts)} parts looked at, {len(found)} genders found, {related.requests} downloads', flush=True)

            if save:
                save(found)

    return found, stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--out', required=True, help='the folder convert.py wrote (housings.json, terminals.json)')
    parser.add_argument('--cache', required=True, help='the folder convert.py --cache wrote; related/ and genders.json go there')
    parser.add_argument('--fetch', action='store_true', help='download the related parts that are not in the cache yet')
    parser.add_argument('--limit', type=int, default=40, help='most downloads for one search (default 40)')
    parser.add_argument('--delay', type=float, default=DELAY)
    args = parser.parse_args()

    with open(os.path.join(args.cache, 'tcpn_index.json'), 'r', encoding='utf-8') as f:
        index = json.load(f)

    genders = {}

    for table in ('housings', 'terminals'):
        with open(os.path.join(args.out, table + '.json'), 'r', encoding='utf-8') as f:
            for row in json.load(f):
                genders[row['part_number']] = row.get('gender')

    known = {}
    kind = {}

    for tcpn, (table, part_number) in index.items():
        if part_number in genders:
            known[tcpn] = genders[part_number]
            kind[tcpn] = table

    unknown = sum(1 for value in known.values() if value not in GENDERS)
    print(f'{len(known)} housings and terminals, {unknown} without a gender')

    by_part = {part_number: tcpn for tcpn, (_table, part_number) in index.items()}
    related = Related(args.cache, args.fetch, args.delay)
    target = os.path.join(args.cache, 'genders.json')

    def save(found: dict[str, str]) -> None:
        common.write_json(target, {index[tcpn][1]: gender for tcpn, gender in sorted(found.items())})

    try:
        found, stats = resolve(known, kind, related, args.limit, save)
    except Blocked as err:
        print(f'stopped: {err}\nrun it again later, it continues from the cache')
        sys.exit(1)

    save(found)
    print(f'\n{len(found)} genders found; {related.requests} downloads, {related.errors} of them refused by TE')

    for name, count in sorted(stats.items()):
        print(f'  {count:7}  {name}')

    print(f'written: {target}')


if __name__ == '__main__':
    main()
