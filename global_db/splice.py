

from typing import Iterable as _Iterable

from .import EntryBase, TableBase
from .mixins import (PartNumberMixin, ManufacturerMixin, ResourceMixin,
                     DescriptionMixin, Model3DMixin, WeightMixin, ColorMixin)

from ...wrappers.decimal import Decimal as _decimal


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

    def insert(self, name: str) -> "Splice":
        db_id = TableBase.insert(self, name=name)
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
            'Weight': {
                'field': 'weight',
                'type': 'float',
                'values': weights
            },
            'Length': {
                'field': 'length',
                'type': 'float',
                'values': lengths
            }
        }

        return ret


class Splice(EntryBase, PartNumberMixin, ManufacturerMixin, ResourceMixin,
             DescriptionMixin, Model3DMixin, WeightMixin, ColorMixin):
    _table: SplicesTable = None

    @property
    def diameter(self) -> _decimal:
        return _decimal(self._table.select('diameter', id=self._db_id)[0][0])

    @diameter.setter
    def diameter(self, value: _decimal):
        self._table.update(self._db_id, diameter=float(value))

    @property
    def length(self) -> _decimal:
        return _decimal(self._table.select('length', id=self._db_id)[0][0])

    @length.setter
    def length(self, value: _decimal):
        self._table.update(self._db_id, length=float(value))