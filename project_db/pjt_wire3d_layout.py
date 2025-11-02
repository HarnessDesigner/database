
from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTWire3DLayoutsTable(PJTTableBase):
    __table_name__ = 'pjt_wire3d_layouts'

    def __iter__(self) -> _Iterable["PJTWire3DLayout"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTWire3DLayout(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTWire3DLayout":
        if isinstance(item, int):
            if item in self:
                return PJTWire3DLayout(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, coord_id: int) -> "PJTWire3DLayout":
        db_id = PJTTableBase.insert(self, coord_id=coord_id)
        return PJTWire3DLayout(self, db_id, self.project_id)


class PJTWire3DLayout(PJTEntryBase):
    _table: PJTWire3DLayoutsTable = None

    @property
    def point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.coord_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def coord_id(self) -> int:
        return self._table.select('coord_id', id=self._db_id)[0][0]

    @coord_id.setter
    def coord_id(self, value: int):
        self._table.update(self._db_id, coord_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d  # NOQA
