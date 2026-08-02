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
this context). Uniqueness comes from a monotonic nanosecond clock that
bumps forward by 1 on a tie or a backward clock jump, never from randomness.
"""

import threading
import time
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


class _LocalMonotonicClock:

    """Process-wide, lock-protected monotonic timestamp source.

    Guards only against this process's own threads racing each other -- a
    single build script has exactly one writer, so no cross-process
    coordination is needed.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._last_issued = 0

    def next_timestamp(self) -> int:
        """Return a timestamp strictly greater than every value previously returned."""
        with self._lock:
            now = time.time_ns()
            if now <= self._last_issued:
                now = self._last_issued + 1
            self._last_issued = now
            return now


_local_clock = _LocalMonotonicClock()


def generate_global_row_id() -> uuid.UUID:
    """Generate a new row id for a global_db table row (no project scoping)."""
    timestamp_ns = _local_clock.next_timestamp()
    row_bytes = pack_global_row_id(timestamp_ns, _LOCAL_USER_ID)
    return uuid.UUID(bytes=row_bytes)


NIL_UUID = uuid.UUID(bytes=b'\x00' * 16)
