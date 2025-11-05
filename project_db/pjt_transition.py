
from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal


class PJTTransitionsTable(PJTTableBase):
    __table_name__ = 'pjt_transitions'

    def __iter__(self) -> _Iterable["PJTTransition"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTTransition(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTTransition":
        if isinstance(item, int):
            if item in self:
                return PJTTransition(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, center_id: int, branch1_id: int, branch2_id: int, branch3_id: int,
               branch4_id: int | None, branch5_id: int | None, branch6_id: int | None,
               x_angle: _decimal, y_angle: _decimal, z_angle: _decimal, name: str) -> "PJTTransition":

        db_id = PJTTableBase.insert(self, part_id=part_id, name=name, center_id=center_id,
                                    branch1_id=branch1_id, branch2_id=branch2_id,
                                    branch3_id=branch3_id, branch4_id=branch4_id,
                                    branch5_id=branch5_id, branch6_id=branch6_id,
                                    x_angle=float(x_angle), y_angle=float(y_angle), z_angle=float(z_angle))

        return PJTTransition(self, db_id, self.project_id)


class PJTTransition(PJTEntryBase):
    _table: PJTTransitionsTable = None

    @property
    def center(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        center_id = self.center_id
        return self._table.db.pjt_coordinates_3d_table[center_id]

    @property
    def center_id(self) -> int:
        return self._table.select('center_id', id=self._db_id)[0][0]

    @center_id.setter
    def center_id(self, value: int):
        self._table.update(self._db_id, center_id=value)

    @property
    def branch1(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch1_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch1_id(self) -> int:
        return self._table.select('branch1_id', id=self._db_id)[0][0]

    @branch1_id.setter
    def branch1_id(self, value: int):
        self._table.update(self._db_id, branch1_id=value)

    @property
    def branch2(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch2_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch2_id(self) -> int:
        return self._table.select('branch2_id', id=self._db_id)[0][0]

    @branch2_id.setter
    def branch2_id(self, value: int):
        self._table.update(self._db_id, branch2_id=value)
    
    @property
    def branch3(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch3_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch3_id(self) -> int:
        return self._table.select('branch3_id', id=self._db_id)[0][0]

    @branch3_id.setter
    def branch3_id(self, value: int):
        self._table.update(self._db_id, branch3_id=value)

    @property
    def branch4(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch4_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch4_id(self) -> int:
        return self._table.select('branch4_id', id=self._db_id)[0][0]

    @branch4_id.setter
    def branch4_id(self, value: int):
        self._table.update(self._db_id, branch4_coord_id=value)
        
    @property
    def branch5(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch5_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch5_id(self) -> int:
        return self._table.select('branch5_id', id=self._db_id)[0][0]

    @branch5_id.setter
    def branch5_id(self, value: int):
        self._table.update(self._db_id, branch5_id=value)

    @property
    def branch6(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch6_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch6_id(self) -> int:
        return self._table.select('branch6_id', id=self._db_id)[0][0]

    @branch6_id.setter
    def branch6_id(self, value: int):
        self._table.update(self._db_id, branch6_id=value)

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)

    @property
    def x_angle(self) -> _decimal:
        return _decimal(self._table.select('x_angle', id=self._db_id)[0][0])

    @x_angle.setter
    def x_angle(self, value: _decimal):
        self._table.update(self._db_id, x_angle=float(value))

    @property
    def y_angle(self) -> _decimal:
        return _decimal(self._table.select('y_angle', id=self._db_id)[0][0])

    @y_angle.setter
    def y_angle(self, value: _decimal):
        self._table.update(self._db_id, y_angle=float(value))

    @property
    def z_angle(self) -> _decimal:
        return _decimal(self._table.select('z_angle', id=self._db_id)[0][0])

    @z_angle.setter
    def z_angle(self, value: _decimal):
        self._table.update(self._db_id, z_angle=float(value))

    @property
    def part(self) -> "_transition.Transition":
        part_id = self.part_id
        if part_id is None:
            return None
        
        return self._table.db.global_db.transitions_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)


from . import pjt_coordinate_3d as _pjt_coordinate_3d  # NOQA

from ..global_db import transition as _transition  # NOQA
