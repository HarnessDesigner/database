from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_point_3d as _pjt_point_3d

    from ..global_db import bundle_cover as _bundle_cover


class PJTBundlesTable(PJTTableBase):
    __table_name__ = 'pjt_bundles'

    def __iter__(self) -> _Iterable["PJTBundle"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBundle(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTBundle":
        if isinstance(item, int):
            if item in self:
                return PJTBundle(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, start_coord_id: int, stop_coord_id: int) -> "PJTBundle":
        db_id = PJTTableBase.insert(self, part_id=part_id, start_coord_id=start_coord_id,
                                    stop_coord_id=stop_coord_id)

        return PJTBundle(self, db_id, self.project_id)


class PJTBundle(PJTEntryBase):
    _table: PJTBundlesTable = None

    @property
    def table(self) -> PJTBundlesTable:
        return self._table

    @property
    def start_point(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.start_point_id
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def start_point_id(self) -> int:
        return self._table.select('start_point_id', id=self._db_id)[0][0]

    @start_point_id.setter
    def start_point_id(self, value: int):
        self._table.update(self._db_id, start_point_id=value)
        self._process_callbacks()

    @property
    def stop_point(self) -> "_pjt_point_3d.PJTPoint3D":
        point_id = self.stop_point_id
        return self._table.db.pjt_points_3d_table[point_id]

    @property
    def stop_point_id(self) -> int:
        return self._table.select('stop_point_id', id=self._db_id)[0][0]

    @stop_point_id.setter
    def stop_point_id(self, value: int):
        self._table.update(self._db_id, stop_point_id=value)
        self._process_callbacks()

    @property
    def part(self) -> "_bundle_cover.BundleCover":
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
        self._process_callbacks()

