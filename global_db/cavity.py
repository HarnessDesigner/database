from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase

from .mixins import NameMixin

if TYPE_CHECKING:
    from . import housing as _housing

from ...geometry import point as _point
from ...wrappers.decimal import Decimal as _decimal


class CavitiesTable(TableBase):
    __table_name__ = 'cavities'

    def __iter__(self) -> _Iterable["Cavity"]:
        for db_id in TableBase.__iter__(self):
            yield Cavity(self, db_id)

    def insert(self, housing_id: int, idx: int, name: str, size: float, point_2d: _point.Point,
               point_3d: _point.Point, x_angle: _decimal, y_angle: _decimal, z_angle: _decimal) -> "Cavity":

        db_id = TableBase.insert(self, housing_id=housing_id, idx=idx, name=name, size=size,
                                 point_2d=str(list(point_2d.as_float()[:-1])),
                                 point_3d=str(list(point_3d.as_float())),
                                 rotation_3d=str([float(x_angle), float(y_angle), float(z_angle)]))

        return Cavity(self, db_id)


class Cavity(EntryBase, NameMixin):
    _table: CavitiesTable = None

    @property
    def housing(self) -> "_housing.Housing":
        from .housing import Housing

        housing_id = self.housing_id
        return Housing(self._table.db.housings_table, housing_id)

    @property
    def housing_id(self) -> int:
        return self._table.select('housing_id', id=self._db_id)[0][0]

    @property
    def idx(self) -> int:
        return self._table.select('idx', id=self._db_id)[0][0]

    @idx.setter
    def idx(self, value: int):
        self._table.update(self._db_id, idx=value)
    
    @property
    def size(self) -> float:
        return self._table.select('size', id=self._db_id)[0][0]

    @size.setter
    def size(self, value: float):
        self._table.update(self._db_id, size=value)

    @property
    def point_2d(self) -> _point.Point:
        point = eval(self._table.select('point_2d', id=self._db_id)[0][0])
        return _point.Point(_decimal(point[0]), _decimal(point[1]), _decimal(0.0))

    @point_2d.setter
    def point_2d(self, value: _point.Point):
        self._table.update(self._db_id, point_2d=str(list(value.as_float()[:-1])))

    @property
    def point_3d(self) -> _point.Point:
        point = eval(self._table.select('point_3d', id=self._db_id)[0][0])
        return _point.Point(_decimal(point[0]), _decimal(point[1]), _decimal(point[2]))

    @point_3d.setter
    def point_3d(self, value: _point.Point):
        self._table.update(self._db_id, point_3d=str(list(value.as_float())))

    @property
    def rotation_3d(self) -> tuple[_decimal, _decimal, _decimal]:
        rotation = eval(self._table.select('rotation_3d', id=self._db_id)[0][0])
        return _decimal(rotation[0]), _decimal(rotation[1]), _decimal(rotation[2])

    @rotation_3d.setter
    def rotation_3d(self, value: tuple[_decimal, _decimal, _decimal]):
        self._table.update(self._db_id, rotation_3d=str([float(item) for item in value]))
