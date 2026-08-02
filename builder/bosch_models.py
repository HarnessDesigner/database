"""Bosch-only special handling for the housings/covers/cpa_locks seed loaders.

Bosch is the one manufacturer folder in this repo that needs anything beyond
the generic name-driven create_database loaders:

- Its `cad`/`datasheet` fields are local, login-gated PDFs bundled in
  Bosch/data/ (not remote URLs like every other manufacturer) -- those must
  never be embedded in the built database, so they're forced to None before
  the row reaches add_housing/add_cover/add_cpa_lock.
- Its `model3d` field is always null in the source JSON, but ~97 of its
  parts have a matching local .stp file in Bosch/data/ (filename = part
  number). Those are NOT converted at build time -- a full mesh conversion
  set runs close to 450MB on top of the ~100MB database itself, too big for
  a single GitHub download. Instead Bosch rows get treated exactly like
  every other manufacturer's model3d field: a plain URL string, stored
  as-is by get_model3d_id()'s existing http-branch. The URL points at the
  .stp file's own location in this repo on GitHub, so downloading (and, if
  ever wanted, converting) it becomes the consuming app's problem -- same
  as it already is for any other manufacturer's model3d URL. See
  builder/mesh_convert.py and builder/bosch_convert_all.py for the
  conversion code this intentionally no longer calls; kept in place in case
  build-time conversion is wanted again later.

Called inline from the ported housings.py/covers.py/cpa_locks.py add_records
loops -- see maybe_handle_bosch_row().
"""

import logging
import os
import urllib.parse

_log = logging.getLogger('builder.bosch_models')

# Pinned to main -- if Bosch/data/ is ever reorganized on main, URLs already
# baked into a previously-built database would break. Move to a release tag
# or commit SHA if that stability matters more than always tracking main.
_RAW_BASE_URL = 'https://raw.githubusercontent.com/HarnessDesigner/database/main'


def maybe_handle_bosch_row(con, item: dict, dir_name: str, dir_path: str):
    """Mutate ``item`` in place for a Bosch-sourced row.

    :param item: the raw row dict about to be passed to add_housing/add_cover/add_cpa_lock.
    :param dir_name: the subdirectory name add_records is currently iterating
        (e.g. ``'Bosch '`` -- note the trailing space the original loop appends).
    :param dir_path: absolute path to that subdirectory (e.g. .../Bosch).
    """
    if dir_name.strip() != 'Bosch':
        return

    item['cad'] = None
    item['datasheet'] = None

    part_number = item.get('part_number')
    if not part_number:
        return

    stp_path = os.path.join(dir_path, 'data', f'{part_number}.stp')
    if not os.path.exists(stp_path):
        return

    item['model3d'] = f'{_RAW_BASE_URL}/Bosch/data/{urllib.parse.quote(part_number)}.stp'
