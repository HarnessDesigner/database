
from typing import Iterable as _Iterable

from ... import EntryBase, TableBase
from ...mixins import NameMixin, DescriptionMixin, ManufacturerMixin, TemperatureMixin

from . import material as _material
from . import family as _family
from . import protection as _protection
from . import shape as _shape
from . import layout as _layout


class TransitionSeriesTable(TableBase):
    __table_name__ = 'transition_series'

    def __iter__(self) -> _Iterable["TransitionSeries"]:
        for db_id in TableBase.__iter__(self):
            yield TransitionSeries(self, db_id)

    def insert(self, name: str) -> "TransitionSeries":

        db_id = TableBase.insert(self, name=name)

        return TransitionSeries(self, db_id)


class TransitionSeries(EntryBase, NameMixin, DescriptionMixin, ManufacturerMixin, TemperatureMixin):
    _table: TransitionSeriesTable = None

    @property
    def code(self) -> str:
        return self._table.select('code', id=self._db_id)[0][0]

    @code.setter
    def code(self, value: str):
        self._table.update(self._db_id, code=value)
        
    @property
    def material(self) -> _material.TransitionMaterial:
        tran_material_id = self._table.select('tran_material_id', id=self._db_id)[0][0]
        return _material.TransitionMaterial(self._table.db.transition_materials_table, tran_material_id)

    @material.setter
    def material(self, value: _material.TransitionMaterial):
        self._table.update(self._db_id, tran_material_id=value.db_id)

    @property
    def material_id(self) -> int:
        return self._table.select('tran_material_id', id=self._db_id)[0][0]

    @material_id.setter
    def material_id(self, value: int):
        self._table.update(self._db_id, tran_material_id=value)

    @property
    def family(self) -> "_family.TransitionFamily":
        family_id = self._table.select('tran_family_id', id=self._db_id)[0][0]
        return _family.TransitionFamily(self._table.db.transition_families_table, family_id)

    @family.setter
    def family(self, value: "_family.TransitionFamily"):
        self._table.update(self._db_id, tran_family_id=value.db_id)

    @property
    def family_id(self) -> int:
        return self._table.select('tran_family_id', id=self._db_id)[0][0]

    @family_id.setter
    def family_id(self, value: int):
        self._table.update(self._db_id, tran_family_id=value)

    @property
    def protection(self) -> "_protection.TransitionProtection":
        protection_id = self._table.select('tran_protection_id', id=self._db_id)[0][0]
        return _protection.TransitionProtection(self._table.db.transition_protections_table, protection_id)

    @protection.setter
    def protection(self, value: "_protection.TransitionProtection"):
        self._table.update(self._db_id, tran_protection_id=value.db_id)
    
    @property
    def protection_id(self) -> int:
        return self._table.select('tran_protection_id', id=self._db_id)[0][0]

    @protection_id.setter
    def protection_id(self, value: int):
        self._table.update(self._db_id, tran_protection_id=value)

    @property
    def shape(self) -> "_shape.TransitionShape":
        shape_id = self._table.select('tran_shape_id', id=self._db_id)[0][0]
        return _shape.TransitionShape(self._table.db.transition_shapes_table, shape_id)

    @shape.setter
    def shape(self, value: "_shape.TransitionShape"):
        self._table.update(self._db_id, tran_shape_id=value.db_id)

    @property
    def shape_id(self) -> int:
        return self._table.select('tran_shape_id', id=self._db_id)[0][0]

    @shape_id.setter
    def shape_id(self, value: int):
        self._table.update(self._db_id, tran_shape_id=value)

    @property
    def branch_count(self) -> int:
        return self._table.select('branch_count', id=self._db_id)[0][0]

    @branch_count.setter
    def branch_count(self, value: int):
        self._table.update(self._db_id, branch_count=value)

    @property
    def layout(self) -> _layout.TransitionLayout:
        return _layout.TransitionLayout(self._table.db.transition_layouts_table, self._db_id)
