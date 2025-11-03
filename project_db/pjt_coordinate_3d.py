from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal
from ...geometry import point as _point


class PJTCoordinates3DTable(PJTTableBase):
    __table_name__ = 'pjt_coordinates_3d'
    __points__ = {}

    def __iter__(self) -> _Iterable["PJTCoordinate3D"]:

        for db_id in PJTTableBase.__iter__(self):
            if db_id in self.__points__:
                yield self.__points__[db_id]
            else:
                point = PJTCoordinate3D(self, db_id, self.project_id)
                self.__points__[db_id] = point
                yield point

    def __getitem__(self, item) -> "PJTCoordinate3D":
        if isinstance(item, int):
            if item in self:
                return PJTCoordinate3D(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def delete(self, db_id: int):
        if db_id in self.__points__:
            del self.__points__[db_id]

        PJTTableBase.delete(self, db_id)

    def insert(self, x: _decimal, y: _decimal, z: _decimal) -> "PJTCoordinate3D":
        db_id = PJTTableBase.insert(self, x=float(x), y=float(y), z=float(z))
        return PJTCoordinate3D(self, db_id, self.project_id)


class PJTCoordinate3D(PJTEntryBase):
    _table: PJTCoordinates3DTable = None

    @property
    def x(self) -> _decimal:
        return _decimal(self._table.select('x', id=self._db_id)[0][0])

    @x.setter
    def x(self, value: _decimal):
        self._table.update(self._db_id, x=float(value))

    @property
    def y(self) -> _decimal:
        return _decimal(self._table.select('y', id=self._db_id)[0][0])

    @y.setter
    def y(self, value: _decimal):
        self._table.update(self._db_id, y=float(value))

    @property
    def z(self) -> _decimal:
        return _decimal(self._table.select('z', id=self._db_id)[0][0])

    @z.setter
    def z(self, value: _decimal):
        self._table.update(self._db_id, z=float(value))

    @property
    def point(self) -> _point.Point:
        point = _point.Point(self.x, self.y, self.z, db_obj=self)
        point.Bind(self)
        return point

    def __call__(self, point: _point.Point) -> None:
        self._table.update(self.db_id, x=float(point.x), y=float(point.y), z=float(point.z))
