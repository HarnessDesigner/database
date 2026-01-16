
from typing import TYPE_CHECKING, Iterable as _Iterable

import numpy as np

from . import PJTEntryBase, PJTTableBase

from ...wrappers.decimal import Decimal as _decimal
from ...geometry import angle as _angle

if TYPE_CHECKING:
    from . import pjt_point3d as _pjt_point3d
    from . import pjt_transition_branch as _pjt_transition_branch
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

    def insert(self, part_id: int, center_id: int, angle: _angle.Angle, name: str) -> "PJTTransition":

        db_id = PJTTableBase.insert(self, part_id=part_id, center_id=center_id,
                                    angle=str(list(angle.as_float)), name=name)

        return PJTTransition(self, db_id, self.project_id)


class PJTTransition(PJTEntryBase):
    _table: PJTTransitionsTable = None
    _center: "_pjt_point3d.PJTPoint3D" = None

    @property
    def table(self) -> PJTTransitionsTable:
        return self._table

    @property
    def center(self) -> "_pjt_point3d.PJTPoint3D":
        if self._center is not None:
            return self._center

        center_id = self.center_id
        self._center = self._table.db.pjt_points3d_table[center_id]
        return self._center

    @property
    def center_id(self) -> int:
        return self._table.select('center_id', id=self._db_id)[0][0]

    @center_id.setter
    def center_id(self, value: int):
        self._table.update(self._db_id, center_id=value)
        self._process_callbacks()

    @property
    def branch1(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_id = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=1)[0][0]

        return self.table.db.pjt_transition_branches_table[db_id]

    @property
    def branch2(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_ids = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=2)

        if not db_ids:
            return None

        return self.table.db.pjt_transition_branches_table[db_ids[0][0]]

    @property
    def branch3(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_ids = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=3)

        if not db_ids:
            return None

        return self.table.db.pjt_transition_branches_table[db_ids[0][0]]

    @property
    def branch4(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_ids = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=4)

        if not db_ids:
            return None

        return self.table.db.pjt_transition_branches_table[db_ids[0][0]]

    @property
    def branch5(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_ids = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=5)

        if not db_ids:
            return None

        return self.table.db.pjt_transition_branches_table[db_ids[0][0]]

    @property
    def branch6(self) -> "_pjt_transition_branch.PJTTransitionBranch":
        db_ids = self.table.db.pjt_transition_branches_table.select(
            'id', transition_id=self.db_id, branch_id=6)

        if not db_ids:
            return None

        return self.table.db.pjt_transition_branches_table[db_ids[0][0]]

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)
        self._process_callbacks()

    def _update_angle(self, a: _angle.Angle) -> None:
        self.quat = a.as_quat

    _saved_angle: _angle.Angle = None

    @property
    def angle(self) -> _angle.Angle:
        if self._saved_angle is not None:
            return self._saved_angle

        quat = self.quat

        angle = _angle.Angle.from_quat(quat)
        angle.Bind(self._update_angle)
        self._saved_angle = angle
        return angle

    @property
    def quat(self) -> np.ndarray:
        quat = eval(self._table.select('quat', id=self._db_id)[0][0])
        return np.array(quat, dtype=np.dtypes.Float64DType)

    @quat.setter
    def quat(self, value: np.ndarray):
        value = value.tolist()
        self._table.update(self._db_id, quat=str(value))
        self._process_callbacks()

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
        self._process_callbacks()
