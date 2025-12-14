from typing import Union as _Union, Iterable as _Iterable

import wx


from . import EntryBase, TableBase
from ...wrappers.decimal import Decimal as _decimal

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, ColorMixin,
                     FamilyMixin, SeriesMixin, ResourceMixin, WeightMixin, TemperatureMixin,
                     Model3DMixin)


class BootsTable(TableBase):
    __table_name__ = 'boots'

    def __iter__(self) -> _Iterable["Boot"]:
        for db_id in TableBase.__iter__(self):
            yield Boot(self, db_id)

    def __getitem__(self, item) -> "Boot":
        if isinstance(item, int):
            if item in self:
                return Boot(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Boot(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, min_temp_id: int, max_temp_id: int, image_id: int,
               datasheet_id: int, cad_id: int, color_id: int, weight: _decimal) -> "Boot":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, min_temp_id=min_temp_id, max_temp_id=max_temp_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, color_id=color_id, weight=float(weight))

        return Boot(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        families = self.get_unique('family_id', 'families')
        series = self.get_unique('series_id', 'series')
        colors = self.get_unique('color_id', 'colors')
        materials = self.get_unique('material_id', 'materials')
        directions = self.get_unique('direction_id', 'directions')
        min_temps = self.get_unique('min_temp_id', 'temperatures')
        max_temps = self.get_unique('max_temp_id', 'temperatures')
        weights = self.get_unique('weight')

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
            'Direction': {
                'field': 'direction_id',
                'type': 'id',
                'values': directions
            },
            'Color': {
                'field': 'color_id',
                'type': 'id',
                'values': colors
            },
            'Material': {
                'field': 'material_id',
                'type': 'id',
                'values': materials
            },
            'Min Temp': {
                'field': 'min_temp_id',
                'type': 'id',
                'values': min_temps
            },
            'Max Temp': {
                'field': 'max_temp_id',
                'type': 'id',
                'values': max_temps
            },
            'Weight': {
                'field': 'weight',
                'type': 'float',
                'values': weights
            }
        }

        return ret

    @property
    def headers(self):
        return [
            'Part Number',
            'Manufacturer',
            'Description',
            'Series',
            'Family',
            'Min Temp',
            'Max Temp',
            'Weight'
        ]

    def parts_list(self):
        cmd = (
            'SELECT boot.id, boot.part_number, boot.description, manufacturer.name,',
            'family.name, series.name, mintemp.name, maxtemp.name, boot.weight FROM boots boot',
            'INNER JOIN manufacturers manufacturer ON boot.mfg_id = manufacturer.id',
            'INNER JOIN families family ON boot.family_id = family.id',
            'INNER JOIN temperatures mintemp family ON boot.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON boot.max_temp_id = maxtemp.id',
            'INNER JOIN series series ON boot.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Family': dict(),
            'Series': dict()
        }

        res = {}

        for id, part_number, description, mfg, family, series, mintemp, maxtemp, weight in data:
            res[part_number] = (mfg, description, series, family, mintemp, maxtemp, weight, id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            if family not in commons['Family']:
                commons['Family'][family] = []

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Manufacturer'][mfg].append(part_number)
            commons['Family'][family].append(part_number)
            commons['Series'][series].append(part_number)

        return res, commons


class Boot(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
           SeriesMixin, ResourceMixin, WeightMixin, ColorMixin, TemperatureMixin, Model3DMixin):
    _table: BootsTable = None
