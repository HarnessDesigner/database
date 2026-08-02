"""Entry point: builds build/harness_designer.db.

Run as: python builder/build_database.py [--repo-root PATH] [--output PATH]

Feeds the repo root (or a given data path) into every ported create_database
module's generic add_records(con, data_path) -- each one auto-discovers
Aptiv/Bosch/TE/Universal subdirectories containing its own JSON file, so one
call per table covers every manufacturer. Bosch needs one thing beyond
that: its cad/datasheet get nulled, and its model3d (where a matching local
.stp exists) gets pointed at that file's own raw.githubusercontent.com URL
instead of being converted at build time -- see builder/bosch_models.py for
why (a full converted-mesh set runs close to 450MB, too big to bundle into
this database's download alongside everything else). No separate
conversion pre-pass runs before housings/covers/cpa_locks seed anymore;
Bosch's model3d flows through the same URL-only path every other
manufacturer's does.
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder import sqlite_connector as _sqlite_connector  # noqa: E402
from builder.create_database import (  # noqa: E402
    manufacturers, families, series, colors, materials, platings, directions,
    genders, shapes, protections, cavity_locks, seal_types, splice_types,
    cpa_lock_types, temperatures, adhesives, transition_series, file_types,
    ip_fluids, ip_solids, ip_supps, ip_ratings, images, cads, datasheets,
    models3d, accessories, cavities, transition_branches, settings,
    housings, covers, cpa_locks, boots, tpa_locks, terminals, seals,
    transitions, wire_markers, splices, bundle_covers, wires,
)  # noqa: E501

_log = logging.getLogger('builder')

# Every module that defines a global `table` (create the schema for). Order
# doesn't matter for SQLite -- REFERENCES clauses aren't validated against
# an existing target table at CREATE TABLE time, only enforced later if
# PRAGMA foreign_keys=ON is set.
TABLE_MODULES = [
    manufacturers, families, series, colors, materials, platings, directions,
    genders, shapes, protections, cavity_locks, seal_types, splice_types,
    cpa_lock_types, temperatures, adhesives, transition_series, file_types,
    ip_fluids, ip_solids, ip_supps, ip_ratings, images, cads, datasheets,
    models3d, accessories, cavities, transition_branches, settings,
    housings, covers, cpa_locks, boots, tpa_locks, terminals, seals,
    transitions, wire_markers, splices, bundle_covers, wires,
]

# Two different add_records() shapes exist in the ORIGINAL upstream code
# (not something introduced by this port): most manufacturer part-table
# loaders (housings, covers, etc.) walk every immediate subdirectory of
# data_path looking for their JSON file, so passing the repo root lets one
# call pick up Aptiv/Bosch/TE/Universal automatically. A handful of
# Universal-only lookup-table loaders never got that treatment upstream --
# they read `os.path.join(data_path, 'X.json')` directly, so they need
# data_path to already BE the Universal folder.
WALKING_SEED_MODULES = [
    wire_markers, transitions, wires,
    housings, terminals, covers, seals, tpa_locks, cpa_locks, boots,
    splices, bundle_covers,
]

# data_path is the Universal folder directly (or unused entirely -- some of
# these, like accessories/ip_solids/ip_fluids/ip_supps/ip_ratings, seed
# hardcoded data and ignore the arg). ip_solids/ip_fluids/ip_supps must run
# before ip_ratings -- it resolves their rows by name.
DIRECT_SEED_MODULES = [
    manufacturers, colors, platings, seal_types, splice_types, temperatures,
    file_types, accessories, ip_solids, ip_fluids, ip_supps, ip_ratings,
]


def build(repo_root: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    db_path = os.path.join(output_dir, 'harness_designer.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    con = _sqlite_connector.Connector(db_path)

    _log.info('creating %d tables', len(TABLE_MODULES))
    for module in TABLE_MODULES:
        module.table.add_to_db(con)

    _log.info('seeding settings (appdata=%s)', output_dir)
    settings.add_records(con, output_dir)

    universal_dir = os.path.join(repo_root, 'Universal')

    for module in DIRECT_SEED_MODULES:
        _log.info('seeding %s', module.__name__)
        module.add_records(con, universal_dir)

    for module in WALKING_SEED_MODULES:
        _log.info('seeding %s', module.__name__)
        module.add_records(con, repo_root)

    _log.info('build complete: %s', db_path)

    con.execute('SELECT name FROM sqlite_master WHERE type="table";')
    table_names = sorted(row[0] for row in con.fetchall())
    for name in table_names:
        con.execute(f'SELECT COUNT(*) FROM "{name}";')
        count = con.fetchone()[0]
        _log.info('  %-24s %d rows', name, count)

    con.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--repo-root', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help='Root containing Aptiv/Bosch/TE/Universal (defaults to this repo\'s root).'
    )
    parser.add_argument(
        '--output', default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build'),
        help='Output directory for the built database + file tree (default: ./build).'
    )
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(name)s: %(message)s',
        stream=sys.stdout,
    )

    build(args.repo_root, args.output)


if __name__ == '__main__':
    main()
