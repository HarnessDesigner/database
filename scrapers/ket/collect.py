# © 2025-2026 Kevin G. Schlosser <kevin.g.schlosser@gmail.com>

"""Download the KET (Korea Electric Terminal) product catalog (https://www.ket.com/en/) for ``convert.py``.

ket.com is a Spring site that wants a session cookie (the first request is redirected until it has one), after which:

* ``POST /en/product/feature-search.ket`` (form: ``categoryCd``, ``page``) -- 20 products per page as JSON, each with
  its whole attribute record (``PARTNUMBER``, ``SPSERIES``, ``SPNOOFPOLE``, ``SPMTERMINAL`` -- the terminals it takes --
  ``SPMCONNECTOR`` -- the mating connector -- ...). ``ATTCFILSN`` is the serial of the product picture.
* ``GET /en/product/<group>/<category>/detail-information.ket?partNumber=...`` -- the product page. It is the only
  place that says which downloads a part has: a 2D drawing PDF (``/resources/web/<pn>/<pn>_2d.pdf``), a 3D PDF and
  3D STEP / IGES files (served by ``/cm/fileDownMan.ket?attcFilSn=<serial>``).

Output goes to ``scrapers/ket/raw/`` (ignored by git):

* ``raw/lists/<category>.json`` -- the products of a category, empty attributes dropped
* ``raw/files.json``            -- ``{part number: {"pdf2d": url, "pdf3d": url, "step": url, "igs": url}}``

Usage::

    python collect.py            # every category, then the file links (about 5,400 pages, ~20 minutes)
    python collect.py --lists    # only the lists
"""

import argparse
import math
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402


BASE = 'https://www.ket.com'
HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, 'raw')
LIST_DIR = os.path.join(RAW_DIR, 'lists')
FILES_PATH = os.path.join(RAW_DIR, 'files.json')

PAGE_SIZE = 20
THREADS = 3

# (categoryCd, product page path) -- what the part-wanting categories of https://www.ket.com/en/ are. Left out: rework
# jigs, BDU, fuses, airbag sensors, board-to-board, HDMI and mobile I/O connectors.
CATEGORIES = (
    ('CA01', 'automotive-connectors/wire-to-wire-connector'),
    ('CA02', 'automotive-connectors/pcb-connector'),
    ('CA03', 'automotive-connectors/joint-connector'),
    ('CA04', 'automotive-connectors/automotive-terminal'),
    ('CA05', 'automotive-connectors/lighting-connector'),
    ('CA06', 'automotive-connectors/connector-sub-part'),
    ('CB01', 'e-mobility-systems/high-voltage-connector'),
    ('CD01', 'data-connectivity-systems/fakra-connector'),
    ('CD02', 'data-connectivity-systems/lvds-connector'),
    ('CF02', 'airbag-sensor-connector/airbag-connector'),
    ('CG01', 'electronic-connectors/home-appliance-connectors'),
    ('CG02', 'electronic-connectors/lighting-connector'),
    ('CG05', 'electronic-connectors/electronic-terminal'),
)

ANCHOR = re.compile(r'<a\b[^>]*>[^<]*', re.I)


def open_session() -> requests.Session:
    session = common.make_session()
    session.headers['X-Requested-With'] = 'XMLHttpRequest'

    # the site redirects until it has set its session cookie
    common.fetch(session, BASE + '/kr/changeLang.ket', params={'language': 'en'})

    return session


def fetch_page(session: requests.Session, code: str, page: int) -> dict:
    response = common.fetch(session, BASE + '/en/product/feature-search.ket', method='POST', timeout=120,
                            data={'categoryCd': code, 'page': str(page), 'searchKey': '', 'selectCategory': ''})

    return response.json()['result']


def collect_lists(session: requests.Session) -> dict[str, list[dict]]:
    lists = {}

    for code, _ in CATEGORIES:
        first = fetch_page(session, code, 1)
        total = first['searchInfo']['totalRow']
        items = list(first['list'])

        for page in range(2, math.ceil(total / PAGE_SIZE) + 1):
            items.extend(fetch_page(session, code, page)['list'])

        # most of the 250 attributes of a record are empty for any one part
        items = [{key: value for key, value in item.items() if value not in ('', None)} for item in items]

        numbers = [item['PARTNUMBER'] for item in items]
        if len(set(numbers)) != len(numbers):
            print(f'{code}: {len(numbers) - len(set(numbers))} repeated part numbers while paging')

        if len(items) != total:
            print(f'{code}: got {len(items)} of {total}')

        common.write_json(os.path.join(LIST_DIR, code + '.json'), items)
        lists[code] = items
        print(f'{code} {len(items)}')

    return lists


def parse_downloads(html: str) -> dict:
    """The download buttons of a product page: ``2D PDF`` / ``3D PDF`` (a link) and ``3D STEP`` / ``3D IGS`` (a serial)."""
    files = {}

    for tag in re.finditer(r'<a\b([^>]*)>([^<]*)', html, re.I):
        attrs, label = tag.group(1), tag.group(2).strip()

        if 'download' not in attrs or label not in ('2D PDF', '3D PDF', '3D STEP', '3D IGS'):
            continue

        href = re.search(r'href="([^"]*)"', attrs)
        serial = re.search(r'fileSn="(\d+)"', attrs)

        if label == '2D PDF' and href and href.group(1) not in ('#', ''):
            files['pdf2d'] = BASE + href.group(1)
        elif label == '3D PDF' and href and href.group(1) not in ('#', ''):
            files['pdf3d'] = BASE + href.group(1)
        elif label == '3D STEP' and serial:
            files['step'] = f'{BASE}/cm/fileDownMan.ket?attcFilSn={serial.group(1)}'
        elif label == '3D IGS' and serial:
            files['igs'] = f'{BASE}/cm/fileDownMan.ket?attcFilSn={serial.group(1)}'

    return files


def collect_files(session: requests.Session, lists: dict[str, list[dict]]) -> None:
    files = {}
    if os.path.exists(FILES_PATH):
        files = common.load_json(FILES_PATH)

    paths = dict(CATEGORIES)
    todo = {}
    for code, items in lists.items():
        for item in items:
            part_number = item['PARTNUMBER']

            if part_number not in files and part_number not in todo:
                todo[part_number] = paths[code]

    print(f'files: {len(files)} on disk, {len(todo)} to download')

    lock = threading.Lock()
    done = [0]

    def work(entry: tuple[str, str]) -> None:
        part_number, path = entry
        url = f'{BASE}/en/product/{path}/detail-information.ket'
        html = common.fetch(session, url, params={'partNumber': part_number}, timeout=120).text

        with lock:
            files[part_number] = parse_downloads(html)
            done[0] += 1

            if done[0] % 250 == 0:
                common.write_json(FILES_PATH, files)
                print(f'files: {done[0]} / {len(todo)}')

    try:
        with ThreadPoolExecutor(max_workers=THREADS) as pool:
            list(pool.map(work, todo.items()))
    finally:
        common.write_json(FILES_PATH, files)

    print(f'files: {len(files)} parts saved')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--lists', action='store_true', help='only download the lists')
    args = parser.parse_args()

    session = open_session()

    lists = collect_lists(session)

    if not args.lists:
        collect_files(session, lists)


if __name__ == '__main__':
    main()
