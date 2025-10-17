
from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal


class PJTTransitionsTable(PJTTableBase):
    __table_name__ = 'pjt_transitions'

    def __iter__(self) -> _Iterable["PJTTransition"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTTransition(self, db_id, self.project_id)

    def insert(self, part_id: int, branch1_coord_id: int, branch2_coord_id: int, branch3_coord_id: int,
               branch4_coord_id: int | None, branch5_coord_id: int | None, branch6_coord_id: int | None,
               x_angle: _decimal, y_angle: _decimal, z_angle: _decimal, name: str) -> "PJTTransition":

        db_id = PJTTableBase.insert(self, part_id=part_id, name=name,
                                    branch1_coord_id=branch1_coord_id, branch2_coord_id=branch2_coord_id,
                                    branch3_coord_id=branch3_coord_id, branch4_coord_id=branch4_coord_id,
                                    branch5_coord_id=branch5_coord_id, branch6_coord_id=branch6_coord_id,
                                    x_angle=float(x_angle), y_angle=float(y_angle), z_angle=float(z_angle))

        return PJTTransition(self, db_id, self.project_id)


class PJTTransition(PJTEntryBase):
    _table: PJTTransitionsTable = None

    @property
    def branch1_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch1_coord_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch1_coord_id(self) -> int:
        return self._table.select('branch1_coord_id', id=self._db_id)[0][0]

    @branch1_coord_id.setter
    def branch1_coord_id(self, value: int):
        self._table.update(self._db_id, branch1_coord_id=value)

    @property
    def branch2_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch2_coord_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch2_coord_id(self) -> int:
        return self._table.select('branch2_coord_id', id=self._db_id)[0][0]

    @branch2_coord_id.setter
    def branch2_coord_id(self, value: int):
        self._table.update(self._db_id, branch2_coord_id=value)
    
    @property
    def branch3_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch3_coord_id
        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch3_coord_id(self) -> int:
        return self._table.select('branch3_coord_id', id=self._db_id)[0][0]

    @branch3_coord_id.setter
    def branch3_coord_id(self, value: int):
        self._table.update(self._db_id, branch3_coord_id=value)

    @property
    def branch4_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch4_coord_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch4_coord_id(self) -> int:
        return self._table.select('branch4_coord_id', id=self._db_id)[0][0]

    @branch4_coord_id.setter
    def branch4_coord_id(self, value: int):
        self._table.update(self._db_id, branch4_coord_id=value)
        
    @property
    def branch5_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch5_coord_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch5_coord_id(self) -> int:
        return self._table.select('branch5_coord_id', id=self._db_id)[0][0]

    @branch5_coord_id.setter
    def branch5_coord_id(self, value: int):
        self._table.update(self._db_id, branch5_coord_id=value)

    @property
    def branch6_point(self) -> "_pjt_coordinate_3d.PJTCoordinate3D":
        coord_id = self.branch6_coord_id
        if coord_id is None:
            return None

        return self._table.db.pjt_coordinates_3d_table[coord_id]

    @property
    def branch6_coord_id(self) -> int:
        return self._table.select('branch6_coord_id', id=self._db_id)[0][0]

    @branch6_coord_id.setter
    def branch6_coord_id(self, value: int):
        self._table.update(self._db_id, branch6_coord_id=value)

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

from ..global_db.protection import transition as _transition  # NOQA
