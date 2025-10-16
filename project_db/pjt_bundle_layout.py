from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTBundleLayoutsTable(PJTTableBase):
    __table_name__ = 'pjt_bundle_layouts'

    def __iter__(self) -> _Iterable["PJTBundleLayout"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBundleLayout(self, db_id, self.project_id)

    def insert(self, coord_id: int) -> "PJTBundleLayout":
        db_id = PJTTableBase.insert(self, project_id=self.project_id, coord_id=coord_id)
        return PJTBundleLayout(self, db_id, self.project_id)


class PJTBundleLayout(PJTEntryBase):
    _table: PJTBundleLayoutsTable = None

    @property
    def coord(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.coord_id
        return self._table.db.pjt_coordinate_3d[coord_id]

    @property
    def coord_id(self) -> int:
        return self._table.select('coord_id', id=self._db_id)[0][0]

    @coord_id.setter
    def coord_id(self, value: int):
        self._table.update(self._db_id, coord_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d
