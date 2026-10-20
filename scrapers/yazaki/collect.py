# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Download the Yazaki connector catalog (https://connector.yazaki-group.com/english/) for ``convert.py``.

The catalog is plain server-rendered pages, no login and no script needed:

* ``search.cgi`` -- a POST with ``search_kbn=spec`` and the ``kind`` of part answers with a page that holds the whole
  result set as a JavaScript array (``var mst = [...]``): part number, name, sealed, gender, poles, colour, series,
  tab size and the drawing image.
* ``detail.cgi?part_id=...`` -- one part: dimensions, material, plating, colour, temperature range, the application
  wire sizes, the mating parts and the terminals / seals / plugs it takes, and the links to its drawing.

Output goes to ``scrapers/yazaki/raw/`` (ignored by git):

* ``raw/lists.json``    -- ``{class: [search rows]}``
* ``raw/details.json``  -- ``{part number: parsed detail page}``

(``report_export.py`` next to this file is a different, older way into the same catalog -- the DevExpress report
export; it is not used here.)

Usage::

    python collect.py          # lists, then every detail page not downloaded yet (about 2,500 pages, ~5 minutes)
    python collect.py --lists  # only the lists
"""

import argparse
import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402


BASE = 'https://connector.yazaki-group.com'
SEARCH_URL = BASE + '/cgi-bin/english/search.cgi'
DETAIL_URL = BASE + '/cgi-bin/english/detail.cgi'

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, 'raw')
LISTS_PATH = os.path.join(RAW_DIR, 'lists.json')
DETAILS_PATH = os.path.join(RAW_DIR, 'details.json')

THREADS = 4

INSTALL_KIND = 'CLAMP,COVER,HOLDER,MISC,SHELL,SLEEVE,UNIT,CAP,BUS-BAR'

# (class, ``kind`` form value, extra form fields). "Installation possible parts" has to be asked one sub-group at a
# time to tell holders from covers and caps.
SEARCHES = (
    ('housing', 'CONNECTOR,SOCKET,COAXIAL,HOUSING', {}),
    ('terminal', 'TERMINAL', {}),
    ('wire_seal', 'WIRESEAL', {}),
    ('dummy_plug', 'DUMMY_PLUG', {}),
    ('holder', INSTALL_KIND, {'accessory1': 'HOLDER'}),
    ('cover', INSTALL_KIND, {'accessory2': 'COVER,CAP'}),
    ('clip', INSTALL_KIND, {'accessory3': 'CLAMP'}),
    ('other', INSTALL_KIND, {'accessory4': 'MISC,SHELL,SLEEVE,UNIT,BUS-BAR'}),
    ('eyelet', 'LALE', {}),
)

MST = re.compile(r'var mst\s*=\s*(\[.*?\]);\s*\n', re.S)
CELL = re.compile(r'<(th|td)\b[^>]*>(.*?)</\1>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')
SPACE = re.compile(r'\s+')


def clean(html: str) -> str:
    return SPACE.sub(' ', TAG.sub(' ', html)).replace('&nbsp;', ' ').replace('&amp;', '&').strip()


def parse_detail(html: str) -> dict:
    """The fields of a detail page as ``{label: {"text": ..., "links": [part numbers]}}`` plus its file links."""
    body = html[html.find('<main'):]

    fields = {}
    for row in re.findall(r'<tr\b.*?</tr>', body, re.S | re.I):
        pending = []

        for kind, content in CELL.findall(row):
            if kind.lower() == 'th':
                pending.append(clean(content))
                continue

            if pending:
                links = [x.replace('%2D', '-') for x in re.findall(r'detail\.cgi\?part_id=([^"&]+)', content)]
                fields[pending[-1]] = {'text': clean(content), 'links': links}
                pending = []

    files = {}
    for kind in ('product', 'draw', 'diagram'):
        match = re.search(r'/common/ProductImage/' + kind + r'/[^"\']+', body)
        if match:
            files[kind] = BASE + match.group(0)

    name = ''
    title = re.search(r'<h2>(.*?)</h2>', body, re.S)
    if title:
        name = clean(title.group(1))

    return {'name': name, 'fields': fields, 'files': files}


def collect_lists(session: requests.Session) -> dict[str, list[dict]]:
    lists = {}

    for name, kind, extra in SEARCHES:
        data = {'search_kbn': 'spec', 'kind': kind, **extra}
        html = common.fetch(session, SEARCH_URL, method='POST', data=data, timeout=120).text

        match = MST.search(html)
        rows = []
        if match:
            rows = json.loads(match.group(1))

        lists[name] = rows
        print(f'{name:12} {len(rows)}')

    return lists


def collect_details(session: requests.Session, part_ids: list[str]) -> None:
    details = {}
    if os.path.exists(DETAILS_PATH):
        details = common.load_json(DETAILS_PATH)

    todo = [part_id for part_id in part_ids if part_id not in details]
    print(f'details: {len(details)} on disk, {len(todo)} to download')

    lock = threading.Lock()
    done = [0]

    def work(part_id: str) -> None:
        html = common.fetch(session, DETAIL_URL, params={'part_id': part_id}).text
        detail = parse_detail(html)

        with lock:
            details[part_id] = detail
            done[0] += 1

            if done[0] % 250 == 0:
                common.write_json(DETAILS_PATH, details)
                print(f'details: {done[0]} / {len(todo)}')

    try:
        with ThreadPoolExecutor(max_workers=THREADS) as pool:
            list(pool.map(work, todo))
    finally:
        common.write_json(DETAILS_PATH, details)

    print(f'details: {len(details)} parts saved')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--lists', action='store_true', help='only download the lists')
    args = parser.parse_args()

    session = common.make_session()

    lists = collect_lists(session)
    common.write_json(LISTS_PATH, lists)

    if args.lists:
        return

    part_ids = []
    seen = set()
    for rows in lists.values():
        for row in rows:
            if row['part_id'] not in seen:
                seen.add(row['part_id'])
                part_ids.append(row['part_id'])

    collect_details(session, part_ids)


if __name__ == '__main__':
    main()
