"""Client-side generation of the 128-bit row-id scheme used by the app's
migrated (UUID primary key) tables.

Ported from harness_designer/database/id_generator.py, trimmed to only what
this standalone builder needs: global_db rows (project_id always 0), a
single local writer (no MySQL GET_LOCK-serialized path), and no
harness_designer.config coupling (that module writes through to a live
config.db on import, which is never appropriate for a batch build script).

    [ project_id : 24 ][ timestamp : 64 ][ reserved : 20 ][ version : 4 ][ user_id : 16 ]

project_id is always 0 here (no project to scope a global_db row to).
user_id is always 0 (single-seat placeholder, no local identity system in
this context).

IDS ARE STATIC. A catalog row's id is a counter value assigned the first time the row's NATURAL KEY (its table and
the value(s) that make it unique: a part number, a name, a URL ...) is seen, and remembered in ``row_ids.txt``, so
rebuilding the database gives every row the id it had before, whatever order the rows are inserted in. That is what
lets the app one day download a newer copy of the catalog and merge the rows it does not have yet without disturbing
projects that already refer to the old rows by id. See ``static_row_id`` and the ledger notes below.
"""

import hashlib
import os
import uuid

_PROJECT_ID_BITS = 24
_TIMESTAMP_BITS = 64
_VERSION_BITS = 4
_RESERVED_BITS = 20
_USER_ID_BITS = 16

assert (_PROJECT_ID_BITS + _TIMESTAMP_BITS + _VERSION_BITS
        + _RESERVED_BITS + _USER_ID_BITS) == 128

_USER_ID_SHIFT = 0
_VERSION_SHIFT = _USER_ID_SHIFT + _USER_ID_BITS
_RESERVED_SHIFT = _VERSION_SHIFT + _VERSION_BITS
_TIMESTAMP_SHIFT = _RESERVED_SHIFT + _RESERVED_BITS
_PROJECT_ID_SHIFT = _TIMESTAMP_SHIFT + _TIMESTAMP_BITS

_PROJECT_ID_MASK = (1 << _PROJECT_ID_BITS) - 1
_TIMESTAMP_MASK = (1 << _TIMESTAMP_BITS) - 1
_VERSION_MASK = (1 << _VERSION_BITS) - 1
_USER_ID_MASK = (1 << _USER_ID_BITS) - 1

FORMAT_VERSION = 1

_LOCAL_USER_ID = 0


def _pack_row_id(project_id: int, timestamp_ns: int, user_id: int) -> bytes:
    """Pack a complete 16-byte row id.

    :raises ValueError: if a field's value doesn't fit its allocated bit width.
    """
    if project_id & ~_PROJECT_ID_MASK:
        raise ValueError(f'project_id {project_id} does not fit in {_PROJECT_ID_BITS} bits')
    if timestamp_ns & ~_TIMESTAMP_MASK:
        raise ValueError(f'timestamp_ns {timestamp_ns} does not fit in {_TIMESTAMP_BITS} bits')
    if user_id & ~_USER_ID_MASK:
        raise ValueError(f'user_id {user_id} does not fit in {_USER_ID_BITS} bits')

    value = (
        ((project_id & _PROJECT_ID_MASK) << _PROJECT_ID_SHIFT)
        | ((timestamp_ns & _TIMESTAMP_MASK) << _TIMESTAMP_SHIFT)
        | ((FORMAT_VERSION & _VERSION_MASK) << _VERSION_SHIFT)
        | (user_id & _USER_ID_MASK)
    )
    return value.to_bytes(16, byteorder='big', signed=False)


def pack_global_row_id(timestamp_ns: int, user_id: int) -> bytes:
    """Pack a global_db row id -- project_id fixed at 0."""
    return _pack_row_id(0, timestamp_ns, user_id)


# THE LEDGER. Ids are a counter, assigned the first time a row's natural key is seen and then remembered in
# ``row_ids.txt`` (next to this file; COMMIT IT). A bare counter would only be static if every build inserted the
# same rows in the same order; the ledger is what makes it static when rows are added, removed or re-ordered:
# a key that is in the ledger always gets its recorded number, and a new key gets the next number up, forever.
# Numbers are never reused. They are written into the "timestamp" field of the row-id layout, which cannot clash
# with an id the app issues to a user-created row (those carry ``time.time_ns()``, about 1.8e18, where these are
# small). The ledger is one line per row, ``<number> <fingerprint>``, where the fingerprint is the first 8 bytes of a
# SHA-256 of the table and key (a readable key would make the file tens of megabytes: most keys are long URLs).
# Never edit or re-order the numbers. A row whose natural key changes (a part is renumbered) is a new row.
# Catalog numbers must stay below this. A row the user adds in the app gets the clock (``time.time_ns()``, about
# 1.8e18) in the same field, and the app refuses to issue one at or below this value, so the two never meet. Keep the
# value identical in the app repo's database/id_generator.py (CATALOG_ID_CEILING).
CATALOG_ID_CEILING = 1 << 40

_LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'row_ids.txt')

_ledger = None  # fingerprint -> number; loaded on first use
_next_number = 2  # 1 is NO_COLOR_UUID's
_unsaved = []  # (number, fingerprint) added since the last save_ledger()

# Rows whose id is fixed by hand. NIL_UUID (all zero) is the "id": 0 default row of every lookup table (for colors
# it is "Black", colour code 0 of MIL-STD-681); the seed code uses it directly. NO_COLOR_UUID is the colors row
# "None": a wire with no outer jacket, a conductor with no stripe. It is a separate row because nil is Black. It is
# the layout's global/version-1/user-0 form with a timestamp of 1, and must never change; the app repo's
# database/id_generator.py holds the same value.
NIL_UUID = uuid.UUID(bytes=b'\x00' * 16)
NO_COLOR_UUID = uuid.UUID(bytes=pack_global_row_id(1, 0))


def _encode_key_part(part) -> bytes:
    """A key part as unambiguous bytes: a type tag, a length, then the value (so ('ab', 'c') != ('a', 'bc'))."""
    if part is None:
        data = b''
        tag = b'n'
    elif isinstance(part, bytes):
        data = part
        tag = b'b'
    elif isinstance(part, int):
        data = str(part).encode('ascii')
        tag = b'i'
    else:
        data = str(part).encode('utf-8')
        tag = b's'

    return tag + len(data).to_bytes(4, 'big') + data


def _fingerprint(table: str, key) -> str:
    digest = hashlib.sha256(b''.join(_encode_key_part(part) for part in (table,) + tuple(key))).digest()
    return digest[:8].hex()


_RESERVED_NUMBERS = {
    _fingerprint('colors', ('None',)): 1,
}


def _load_ledger() -> None:
    global _ledger, _next_number

    _ledger = dict(_RESERVED_NUMBERS)
    last_number = 1

    if os.path.exists(_LEDGER_PATH):
        with open(_LEDGER_PATH, 'r', encoding='ascii') as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                number_text, fingerprint = line.split(' ')
                number = int(number_text)

                if number <= last_number:
                    raise ValueError(f'{_LEDGER_PATH}:{line_number}: numbers must increase ({number} after {last_number})')
                if fingerprint in _ledger:
                    raise ValueError(f'{_LEDGER_PATH}:{line_number}: fingerprint {fingerprint} is in the ledger twice')

                _ledger[fingerprint] = number
                last_number = number

    _next_number = last_number + 1


def static_row_id(table: str, *key) -> uuid.UUID:
    """The id of the row of ``table`` whose natural key is ``key``: the same on every build.

    :param table: The table's name.
    :param key: The value(s) that make the row unique in its table -- a part number, a name, a URL, or for a row
        scoped to a manufacturer ``(mfg_id, name)``. Strings, ints, bytes (an id) and None are accepted.
    """
    global _next_number

    if _ledger is None:
        _load_ledger()

    fingerprint = _fingerprint(table, key)
    number = _ledger.get(fingerprint)

    if number is None:
        number = _next_number
        _next_number += 1

        if number >= CATALOG_ID_CEILING:
            raise ValueError(f'the row id ledger is full: {number} is not below {CATALOG_ID_CEILING}')
        _ledger[fingerprint] = number
        _unsaved.append((number, fingerprint))

    return uuid.UUID(bytes=pack_global_row_id(number, _LOCAL_USER_ID))


def save_ledger() -> int:
    """Append the entries added since the last save to ``row_ids.txt``. Call it once, when a build has finished
    successfully, and commit the file. Returns how many entries were written."""
    if not _unsaved:
        return 0

    with open(_LEDGER_PATH, 'a', encoding='ascii', newline='\n') as f:
        for number, fingerprint in _unsaved:
            f.write(f'{number} {fingerprint}\n')

    written = len(_unsaved)
    _unsaved.clear()

    return written
