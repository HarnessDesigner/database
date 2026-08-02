"""Parallel pre-conversion of every Bosch .stp file, run once before any
table seeding starts.

Walks Bosch/data/*.stp directly (not through housings.json/covers.json/
cpa_locks.json) and converts all of them in parallel via
multiprocessing.Pool -- each worker does the CPU-heavy OCP triangulation +
normals computation and writes its own .npy file (safe: every worker writes
to a distinct path), returning only lightweight metadata. The main process
then does the actual models3d INSERTs sequentially (id generation isn't
multiprocessing-safe, and DB writes are cheap compared to triangulation).

pool.map() blocks until every worker finishes, so by the time this function
returns, every Bosch part_number's model3d row (if it had a matching .stp)
already exists -- housings.py/covers.py/cpa_locks.py's add_records loops
(via bosch_models.maybe_handle_bosch_row) just look it up by path afterward,
no conversion happens inline anymore.
"""

import logging
import multiprocessing
import os

_log = logging.getLogger('builder.bosch_convert_all')


def _convert_worker(args):
    stp_path, models_output_dir = args

    import uuid as _uuid
    import numpy as np
    from . import mesh_convert as _mesh_convert

    try:
        packed, vertex_count, aabb, obb = _mesh_convert.convert_stp(stp_path)
    except Exception as err:  # NOQA
        return {'stp_path': stp_path, 'error': repr(err)}

    file_uuid = str(_uuid.uuid4())
    out_dir = os.path.join(models_output_dir, file_uuid[:2])
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, f'{file_uuid}.npy'), packed)

    return {
        'stp_path': stp_path,
        'file_uuid': file_uuid,
        'vertex_count': vertex_count,
        'aabb': aabb,
        'obb': obb,
    }


def convert_all_bosch_models(con, bosch_data_dir: str, models_output_dir: str,
                             max_workers: int | None = None):
    """Convert every Bosch/data/*.stp file in parallel and insert its models3d row.

    Idempotent: rows already present (by path) are skipped, same as the old
    inline convert_and_insert() did.
    """
    from . import id_generator as _id_generator

    stp_paths = sorted(
        os.path.join(bosch_data_dir, f)
        for f in os.listdir(bosch_data_dir)
        if f.lower().endswith('.stp')
    )

    if not stp_paths:
        _log.info('no Bosch .stp files found in %s', bosch_data_dir)
        return

    con.execute('SELECT id FROM file_types WHERE extension=?;', ('stp',))
    ft_row = con.fetchall()
    file_type_id = ft_row[0][0] if ft_row else None

    # Skip files that already have a models3d row (idempotent re-run).
    pending = []
    for stp_path in stp_paths:
        con.execute('SELECT id FROM models3d WHERE path=?;', (stp_path,))
        if not con.fetchall():
            pending.append(stp_path)

    if not pending:
        _log.info('all %d Bosch models already converted', len(stp_paths))
        return

    workers = max_workers or os.cpu_count() or 4
    _log.info('converting %d Bosch STP files across %d worker process(es)...',
              len(pending), workers)

    args = [(p, models_output_dir) for p in pending]

    with multiprocessing.Pool(processes=workers) as pool:
        results = pool.map(_convert_worker, args)  # blocks until all workers finish

    converted = 0
    for res in results:
        if 'error' in res:
            _log.error('failed to convert %s: %s', res['stp_path'], res['error'])
            continue

        new_id = _id_generator.generate_global_row_id().bytes
        con.execute(
            'INSERT INTO models3d (id, uuid, file_type_id, vertex_count, aabb, obb, path) '
            'VALUES (?, ?, ?, ?, ?, ?, ?);',
            (new_id, res['file_uuid'], file_type_id, res['vertex_count'],
             str(res['aabb']), str(res['obb']), res['stp_path'])
        )
        _log.info('converted %s -> models3d %s (%d verts)',
                  res['stp_path'], new_id.hex(), res['vertex_count'])
        converted += 1

    con.commit()
    _log.info('Bosch model conversion complete: %d/%d succeeded', converted, len(pending))
