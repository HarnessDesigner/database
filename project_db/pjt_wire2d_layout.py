
from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_point_2d as _pjt_point_2d


class PJTWire2DLayoutsTable(PJTTableBase):
    __table_name__ = 'pjt_wire2d_layouts'

    def __iter__(self) -> _Iterable["PJTWire2DLayout"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTWire2DLayout(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTWire2DLayout":
        if isinstance(item, int):
            if item in self:
                return PJTWire2DLayout(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, point_id: int) -> "PJTWire2DLayout":
        db_id = PJTTableBase.insert(self, point_id=point_id)
        return PJTWire2DLayout(self, db_id, self.project_id)


class PJTWire2DLayout(PJTEntryBase):
    _table: PJTWire2DLayoutsTable = None

    @property
    def table(self) -> PJTWire2DLayoutsTable:
        return self._table

    @property
    def point(self) -> "_pjt_point_2d.PJTPoint2D":
        point_id = self.point_id
        return self._table.db.pjt_points_2d_table[point_id]

    @property
    def point_id(self) -> int:
        return self._table.select('point_id', id=self._db_id)[0][0]

    @point_id.setter
    def point_id(self, value: int):
        self._table.update(self._db_id, point_id=value)
        self._process_callbacks()
