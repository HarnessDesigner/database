
from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal
from ...geometry import angle as _angle

if TYPE_CHECKING:
    from . import pjt_point_3d as _pjt_point_3d
    from ..global_db import transition as _transition


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

    def insert(self, part_id: int, center_id: int, angle: _angle.Angle, name: str,
               branch1_id: int | None, branch2_id: int | None,
               branch3_id: int | None, branch4_id: int | None,
               branch5_id: int | None, branch6_id: int | None,
               branch1dia: _decimal | None, branch2dia: _decimal | None,
               branch3dia: _decimal | None, branch4dia: _decimal | None,
               branch5dia: _decimal | None, branch6dia: _decimal | None) -> "PJTTransition":

        if branch1dia is not None:
            branch1dia = float(branch1dia)

        if branch2dia is not None:
            branch2dia = float(branch2dia)

        if branch3dia is not None:
            branch3dia = float(branch3dia)

        if branch4dia is not None:
            branch4dia = float(branch4dia)

        if branch5dia is not None:
            branch5dia = float(branch5dia)

        if branch6dia is not None:
            branch6dia = float(branch6dia)

        db_id = PJTTableBase.insert(self, part_id=part_id, center_id=center_id,
                                    angle=str(list(angle.as_float)), name=name,
                                    branch1_id=branch1_id, branch2_id=branch2_id,
                                    branch3_id=branch3_id, branch4_id=branch4_id,
                                    branch5_id=branch5_id, branch6_id=branch6_id,
                                    branch1dia=branch1dia, branch2dia=branch2dia,
                                    branch3dia=branch3dia, branch4dia=branch4dia,
                                    branch5dia=branch5dia, branch6dia=branch6dia)

        return PJTTransition(self, db_id, self.project_id)


class PJTTransition(PJTEntryBase):
    _table: PJTTransitionsTable = None

    _center: "_pjt_point_3d.PJTPoint3D" = None
    _branch1: "_pjt_point_3d.PJTPoint3D" = None
    _branch2: "_pjt_point_3d.PJTPoint3D" = None
    _branch3: "_pjt_point_3d.PJTPoint3D" = None
    _branch4: "_pjt_point_3d.PJTPoint3D" = None
    _branch5: "_pjt_point_3d.PJTPoint3D" = None
    _branch6: "_pjt_point_3d.PJTPoint3D" = None

    @property
    def center(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._center is not None:
            return self._center

        center_id = self.center_id
        self._center = self._table.db.pjt_points_3d_table[center_id]
        return self._center

    @property
    def center_id(self) -> int:
        return self._table.select('center_id', id=self._db_id)[0][0]

    @center_id.setter
    def center_id(self, value: int):
        self._table.update(self._db_id, center_id=value)

    @property
    def branch1(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch1 is not None:
            return self._branch1

        coord_id = self.branch1_id
        return self._table.db.pjt_points_3d_table[coord_id]

    @property
    def branch1_id(self) -> int:
        return self._table.select('branch1_id', id=self._db_id)[0][0]

    @branch1_id.setter
    def branch1_id(self, value: int):
        self._table.update(self._db_id, branch1_id=value)

    @property
    def branch2(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch2 is not None:
            return self._branch2

        coord_id = self.branch2_id
        self._branch2 = self._table.db.pjt_points_3d_table[coord_id]
        return self._branch2

    @property
    def branch2_id(self) -> int:
        return self._table.select('branch2_id', id=self._db_id)[0][0]

    @branch2_id.setter
    def branch2_id(self, value: int):
        self._table.update(self._db_id, branch2_id=value)
    
    @property
    def branch3(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch3 is not None:
            return self._branch3

        coord_id = self.branch3_id
        self._branch3 = self._table.db.pjt_points_3d_table[coord_id]
        return self._branch3

    @property
    def branch3_id(self) -> int:
        return self._table.select('branch3_id', id=self._db_id)[0][0]

    @branch3_id.setter
    def branch3_id(self, value: int):
        self._table.update(self._db_id, branch3_id=value)

    @property
    def branch4(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch4 is not None:
            return self._branch4

        coord_id = self.branch4_id
        if coord_id is None:
            return None

        self._branch4 = self._table.db.pjt_points_3d_table[coord_id]
        return self._branch4

    @property
    def branch4_id(self) -> int:
        return self._table.select('branch4_id', id=self._db_id)[0][0]

    @branch4_id.setter
    def branch4_id(self, value: int):
        self._table.update(self._db_id, branch4_id=value)
        
    @property
    def branch5(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch5 is not None:
            return self._branch5

        coord_id = self.branch5_id
        if coord_id is None:
            return None

        self._branch5 = self._table.db.pjt_points_3d_table[coord_id]
        return self._branch5

    @property
    def branch5_id(self) -> int:
        return self._table.select('branch5_id', id=self._db_id)[0][0]

    @branch5_id.setter
    def branch5_id(self, value: int):
        self._table.update(self._db_id, branch5_id=value)

    @property
    def branch6(self) -> "_pjt_point_3d.PJTPoint3D":
        if self._branch6 is not None:
            return self._branch6

        coord_id = self.branch6_id
        if coord_id is None:
            return None

        self._branch6 = self._table.db.pjt_points_3d_table[coord_id]
        return self._branch6

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

    def _update_angle(self, a: _angle.Angle) -> None:
        self._table.update(self._db_id, x_angle=str(list(a.as_float)))

    _saved_angle: _angle.Angle = None

    @property
    def angle(self) -> _angle.Angle:
        if self._saved_angle is not None:
            return self._saved_angle

        angle = eval(self._table.select('angle', id=self._db_id)[0][0])
        angle = [_decimal(item) for item in angle]
        angle = _angle.Angle(*angle)
        angle.Bind(self._update_angle)
        self._saved_angle = angle
        return angle

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

    @property
    def branch1dia(self) -> _decimal:
        return _decimal(self._table.select('branch1dia', id=self._db_id)[0][0])

    @branch1dia.setter
    def branch1dia(self, value: _decimal):
        self._table.update(self._db_id, branch1dia=float(value))

    @property
    def branch2dia(self) -> _decimal:
        return _decimal(self._table.select('branch2dia', id=self._db_id)[0][0])

    @branch2dia.setter
    def branch2dia(self, value: _decimal):
        self._table.update(self._db_id, branch2dia=float(value))

    @property
    def branch3dia(self) -> _decimal:
        return _decimal(self._table.select('branch3dia', id=self._db_id)[0][0])

    @branch3dia.setter
    def branch3dia(self, value: _decimal):
        self._table.update(self._db_id, branch3dia=float(value))

    @property
    def branch4dia(self) -> _decimal:
        return _decimal(self._table.select('branch4dia', id=self._db_id)[0][0])

    @branch4dia.setter
    def branch4dia(self, value: _decimal):
        self._table.update(self._db_id, branch4dia=float(value))

    @property
    def branch5dia(self) -> _decimal:
        return _decimal(self._table.select('branch5dia', id=self._db_id)[0][0])

    @branch5dia.setter
    def branch5dia(self, value: _decimal):
        self._table.update(self._db_id, branch5dia=float(value))

    @property
    def branch6dia(self) -> _decimal:
        return _decimal(self._table.select('branch6dia', id=self._db_id)[0][0])

    @branch6dia.setter
    def branch6dia(self, value: _decimal):
        self._table.update(self._db_id, branch6dia=float(value))
