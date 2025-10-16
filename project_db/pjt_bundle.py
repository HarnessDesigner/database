from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTBundlesTable(PJTTableBase):
    __table_name__ = 'pjt_bundles'

    def __iter__(self) -> _Iterable["PJTBundle"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBundle(self, db_id, self.project_id)

    def insert(self, part_id: int, start_coord_id: int, stop_coord_id: int) -> "PJTBundle":
        db_id = PJTTableBase.insert(self, project_id=self.project_id, part_id=part_id,
                                    start_coord_id=start_coord_id, stop_coord_id=stop_coord_id)
        return PJTBundle(self, db_id, self.project_id)


class PJTBundle(PJTEntryBase):
    _table: PJTBundlesTable = None

    @property
    def start_coord(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.start_coord_id
        return self._table.db.pjt_coordinate_3d[coord_id]

    @property
    def start_coord_id(self) -> int:
        return self._table.select('start_coord_id', id=self._db_id)[0][0]

    @start_coord_id.setter
    def start_coord_id(self, value: int):
        self._table.update(self._db_id, start_coord_id=value)

    @property
    def stop_coord(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.stop_coord_id
        return self._table.db.pjt_coordinate_3d[coord_id]

    @property
    def stop_coord_id(self) -> int:
        return self._table.select('stop_coord_id', id=self._db_id)[0][0]

    @stop_coord_id.setter
    def stop_coord_id(self, value: int):
        self._table.update(self._db_id, stop_coord_id=value)

    @property
    def part(self) -> "_bundle.BundleCover":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.bundle_covers_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d
from ..global_db.protection import bundle as _bundle
