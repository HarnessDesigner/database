from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase
from ...wrappers.decimal import Decimal as _decimal

if TYPE_CHECKING:
    from . import pjt_coordinate_3d as _pjt_coordinate_3d


class PJTBundleLayoutsTable(PJTTableBase):
    __table_name__ = 'pjt_bundle_layouts'

    def __iter__(self) -> _Iterable["PJTBundleLayout"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBundleLayout(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTBundleLayout":
        if isinstance(item, int):
            if item in self:
                return PJTBundleLayout(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, coord_id: int, diameter: _decimal) -> "PJTBundleLayout":
        db_id = PJTTableBase.insert(self, coord_id=coord_id, diameter=float(diameter))

        return PJTBundleLayout(self, db_id, self.project_id)


class PJTBundleLayout(PJTEntryBase):
    _table: PJTBundleLayoutsTable = None

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

    @property
    def diameter(self) -> _decimal:
        diameter = self._table.select('diameter', id=self._db_id)[0][0]
        return _decimal(diameter)

    @diameter.setter
    def diameter(self, value: _decimal):
        self._table.update(self._db_id, diameter=float(value))
