from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal
from ...geometry import point as _point


class PJTCoordinates2DTable(PJTTableBase):
    __table_name__ = 'pjt_coordinates_2d'
    __points__ = {}

    def __iter__(self) -> _Iterable["PJTCoordinate2D"]:

        for db_id in PJTTableBase.__iter__(self):
            if db_id in self.__points__:
                yield self.__points__[db_id]
            else:
                point = PJTCoordinate2D(self, db_id, self.project_id)
                self.__points__[db_id] = point
                yield point

    def __getitem__(self, item) -> "PJTCoordinate2D":
        if isinstance(item, int):
            if item in self:
                return PJTCoordinate2D(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def delete(self, db_id: int):
        if db_id in self.__points__:
            del self.__points__[db_id]

        PJTTableBase.delete(self, db_id)

    def insert(self, x: float, y: float) -> "PJTCoordinate2D":
        db_id = PJTTableBase.insert(self, x=x, y=y)
        return PJTCoordinate2D(self, db_id, self.project_id)


class PJTCoordinate2D(PJTEntryBase):
    _table: PJTCoordinates2DTable = None

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
    def point(self) -> _point.Point:
        point = _point.Point(self.x, self.y, project_id=self._table.project_id, point_id=self._db_id)
        point.Bind(self.__on_update)
        return point

    def __on_update(self, point: _point.Point) -> None:
        self._table.update(self.db_id, x=float(point.x), y=float(point.y))




