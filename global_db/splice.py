from typing import TYPE_CHECKING, Iterable as _Iterable

from .import EntryBase, TableBase
from .mixins import (PartNumberMixin, DescriptionMixin, ManufacturerMixin, FamilyMixin,
                     SeriesMixin, MaterialMixin, ColorMixin, PlatingMixin, ResourceMixin,
                     Model3DMixin, WeightMixin)

from ...wrappers.decimal import Decimal as _decimal


if TYPE_CHECKING:
    from . import splice_types as _splice_types


class SplicesTable(TableBase):
    __table_name__ = 'splices'

    def __iter__(self) -> _Iterable["Splice"]:
        for db_id in TableBase.__iter__(self):
            yield Splice(self, db_id)

    def __getitem__(self, item) -> "Splice":
        if isinstance(item, int):
            if item in self:
                return Splice(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', name=item)
        if db_id:
            return Splice(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, description: str, mfg_id: int, family_id: int,
               series_id: int, material_id: int, color_id: int, plating_id: int,
               type_id: int, min_dia: _decimal, max_dia: _decimal, resistance: _decimal,
               length: _decimal, weight: _decimal) -> "Splice":

        db_id = TableBase.insert(self, part_number=part_number, description=description,
                                 mfg_id=mfg_id, family_id=family_id, series_id=series_id,
                                 material_id=material_id, color_id=color_id, plating_id=plating_id,
                                 type_id=type_id, min_dia=float(min_dia), max_dia=float(max_dia),
                                 resistance=float(resistance), length=float(length), weight=float(weight))

        return Splice(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        series = self.get_unique('series_id', 'series')
        families = self.get_unique('family_id', 'families')
        platings = self.get_unique('plating_id', 'platings', 'symbol')
        materials = self.get_unique('material_id', 'materials')
        types = self.get_unique('type_id', 'splice_types')
        colors = self.get_unique('color_id', 'colors')
        resistances = self.get_unique('resistance')
        min_dias = self.get_unique('min_dia')
        max_dias = self.get_unique('max_dia')
        weights = self.get_unique('weight')
        lengths = self.get_unique('length')

        ret = {
            'Manufacturer': {
                'field': 'mfg_id',
                'type': 'id',
                'values': mfgs
            },
            'Family': {
                'field': 'family_id',
                'type': 'id',
                'values': families
            },
            'Series': {
                'field': 'series_id',
                'type': 'id',
                'values': series
            },
            'Plating': {
                'field': 'plating_id',
                'type': 'id',
                'values': platings
            },
            'Material': {
                'field': 'material_id',
                'type': 'id',
                'values': materials
            },
            'Type': {
                'field': 'type_id',
                'type': 'id',
                'values': types
            },
            'Color': {
                'field': 'color_id',
                'type': 'id',
                'values': colors
            },
            'Diameter Max (mm)': {
                'field': 'max_dia',
                'type': 'float',
                'values': max_dias
            },
            'Diameter Min (mm)': {
                'field': 'min_dia',
                'type': 'float',
                'values': min_dias
            },
            'Resistance ()':{
                'field': 'resistance',
                'type': 'float',
                'values': resistances
            },
            'Weight (g)': {
                'field': 'weight',
                'type': 'float',
                'values': weights
            },
            'Length (mm)': {
                'field': 'length',
                'type': 'float',
                'values': lengths
            }
        }

        return ret


class Splice(EntryBase, PartNumberMixin, DescriptionMixin, ManufacturerMixin,
             FamilyMixin, SeriesMixin, MaterialMixin, ColorMixin, PlatingMixin,
             ResourceMixin, Model3DMixin, WeightMixin):

    _table: SplicesTable = None

    @property
    def type(self) -> "_splice_types.SpliceType":
        db_id = self.type_id
        return self._table.db.splice_types_table[db_id]

    @type.setter
    def type(self, value: "_splice_types.SpliceType"):
        self.type_id = value.db_id

    @property
    def type_id(self) -> int:
        return self._table.select('type_id', id=self._db_id)[0][0]

    @type_id.setter
    def type_id(self, value: int):
        self._table.update(self._db_id, type_id=value)

    @property
    def resistance(self) -> _decimal:
        return _decimal(self._table.select('resistance', id=self._db_id)[0][0])

    @resistance.setter
    def resistance(self, value: _decimal):
        self._table.update(self._db_id, resistance=float(value))

    @property
    def min_dia(self) -> _decimal:
        return _decimal(self._table.select('min_dia', id=self._db_id)[0][0])

    @min_dia.setter
    def min_dia(self, value: _decimal):
        self._table.update(self._db_id, min_dia=float(value))

    @property
    def max_dia(self) -> _decimal:
        return _decimal(self._table.select('max_dia', id=self._db_id)[0][0])

    @max_dia.setter
    def max_dia(self, value: _decimal):
        self._table.update(self._db_id, min_dia=float(value))

    @property
    def length(self) -> _decimal:
        return _decimal(self._table.select('length', id=self._db_id)[0][0])

    @length.setter
    def length(self, value: _decimal):
        self._table.update(self._db_id, length=float(value))
