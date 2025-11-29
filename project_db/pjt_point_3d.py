from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal
from ...geometry import point as _point


class PJTPoints3DTable(PJTTableBase):
    __table_name__ = 'pjt_points_3d'
    __points__ = {}

    def __iter__(self) -> _Iterable["PJTPoint3D"]:

        for db_id in PJTTableBase.__iter__(self):
            if db_id in self.__points__:
                yield self.__points__[db_id]
            else:
                point = PJTPoint3D(self, db_id, self.project_id)
                self.__points__[db_id] = point
                yield point

    def __getitem__(self, item) -> "PJTPoint3D":
        if isinstance(item, int):
            if item in self:
                return PJTPoint3D(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def delete(self, db_id: int):
        if db_id in self.__points__:
            del self.__points__[db_id]

        PJTTableBase.delete(self, db_id)

    def insert(self, x: _decimal, y: _decimal, z: _decimal) -> "PJTPoint3D":
        db_id = PJTTableBase.insert(self, x=float(x), y=float(y), z=float(z))
        return PJTPoint3D(self, db_id, self.project_id)


class PJTPoint3D(PJTEntryBase):
    _table: PJTPoints3DTable = None

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

    _saved_point: _point.Point = None

    @property
    def point(self) -> _point.Point:
        if self._saved_point is not None:
            return self._saved_point

        self._saved_point = _point.Point(self.x, self.y, self.z, db_obj=self)
        self._saved_point.Bind(self._update_point)

        return self._saved_point

    def _update_point(self, point: _point.Point) -> None:
        self._table.update(self.db_id, x=float(point.x), y=float(point.y), z=float(point.z))
