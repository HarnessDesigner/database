
from typing import Iterable as _Iterable, TYPE_CHECKING

from . import EntryBase, TableBase
from .mixins import (PartNumberMixin, SeriesMixin, MaterialMixin, FamilyMixin,
                     ManufacturerMixin, DescriptionMixin, ColorMixin, ProtectionMixin,
                     AdhesiveMixin, ResourceMixin, TemperatureMixin, WeightMixin)


if TYPE_CHECKING:
    from . import transition_branch as _transition_branch
    from . import shape as _shape


class TransitionsTable(TableBase):
    __table_name__ = 'transitions'

    def __iter__(self) -> _Iterable["Transition"]:
        for db_id in TableBase.__iter__(self):
            yield Transition(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, color_id: int, material_id: int, branch_count: int,
               shape_id: int, protection_ids: list[int], adhesive_ids: list[int],
               cad_id: int, datasheet_id: int, image_id: int, min_temp_id: int,
               max_temp_id: int, weight: float) -> "Transition":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, color_id=color_id,
                                 material_id=material_id, branch_count=branch_count, shape_id=shape_id,
                                 protection_ids=str(protection_ids), adhesive_ids=str(adhesive_ids),
                                 cad_id=cad_id, datasheet_id=datasheet_id, image_id=image_id,
                                 min_temp_id=min_temp_id, max_temp_id=max_temp_id, weight=weight)

        return Transition(self, db_id)


class Transition(EntryBase, PartNumberMixin, SeriesMixin, MaterialMixin, FamilyMixin,
                 ManufacturerMixin, DescriptionMixin, ColorMixin, ProtectionMixin, AdhesiveMixin,
                 ResourceMixin, TemperatureMixin, WeightMixin):
    
    _table: TransitionsTable = None

    @property
    def branch_count(self) -> int:
        return self._table.select('branch_count', id=self._db_id)[0][0]

    @branch_count.setter
    def branch_count(self, value: int):
        self._table.update(self._db_id, branch_count=value)

    @property
    def branches(self) -> list["_transition_branch.TransitionBranch"]:
        from .transition_branch import TransitionBranch

        res = [None] * self.branch_count

        branch_ids = self._table.db.transition_branches_table.select('id', transition_id=self._db_id)

        for branch_id in branch_ids:
            branch = TransitionBranch(self, branch_id[0])
            res[branch.idx - 1] = branch

        return res

    @property
    def shape(self) -> "_shape.Shape":
        shape_id = self.shape_id
        from .shape import Shape

        return Shape(self._table.db.shapes_table, shape_id)

    @shape.setter
    def shape(self, value: "_shape.Shape"):
        self._table.update(self._db_id, shape_id=value.db_id)

    @property
    def shape_id(self) -> int:
        return self._table.select('shape_id', id=self._db_id)[0][0]

    @shape_id.setter
    def shape_id(self, value: int):
        self._table.update(self._db_id, shape_id=value)

