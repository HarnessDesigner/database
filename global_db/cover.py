from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from ...wrappers.decimal import Decimal as _decimal
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, DirectionMixin,
                     FamilyMixin, SeriesMixin, ResourceMixin, WeightMixin,
                     TemperatureMixin, ColorMixin, DimensionMixin, Model3DMixin)


class CoversTable(TableBase):
    __table_name__ = 'covers'

    def __iter__(self) -> _Iterable["Cover"]:
        for db_id in TableBase.__iter__(self):
            yield Cover(self, db_id)

    def __getitem__(self, item) -> "Cover":
        if isinstance(item, int):
            if item in self:
                return Cover(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Cover(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int,
               direction_id: int, min_temp_id: int, max_temp_id: int, color_id: int,
               length: _decimal, width: _decimal, height: _decimal, pins: str, weight: _decimal) -> "Cover":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, direction_id=direction_id,
                                 min_temp_id=min_temp_id, max_temp_id=max_temp_id, color_id=color_id,
                                 length=float(length), width=float(width), height=float(height),
                                 pins=pins, weight=float(weight))

        return Cover(self, db_id)

    @property
    def search_items(self) -> dict:
        mfgs = self.get_unique('mfg_id', 'manufacturers')
        series = self.get_unique('series_id', 'series')
        families = self.get_unique('family_id', 'families')
        colors = self.get_unique('color_id', 'colors')
        directions = self.get_unique('direction_id', 'directions')
        min_temps = self.get_unique('min_temp_id', 'temperatures')
        max_temps = self.get_unique('max_temp_id', 'temperatures')
        lengths = self.get_unique('length')
        widths = self.get_unique('width')
        heights = self.get_unique('height')
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
            'Length': {
                'field': 'length',
                'type': 'float',
                'values': lengths
            },
            'Color': {
                'field': 'color_id',
                'type': 'id',
                'values': colors
            },
            'Direction': {
                'field': 'direction_id',
                'type': 'id',
                'values': directions
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
            },
            'Width': {
                'field': 'width',
                'type': 'float',
                'values': widths
            },
            'Height': {
                'field': 'height',
                'type': 'float',
                'values': heights
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
            'Weight',
            'Min Temp',
            'Max Temp'
        ]

    def parts_list(self):
        cmd = (
            'SELECT cover.id, cover.part_number, cover.description, manufacturer.name,',
            'series.name, cover.weight, mintemp.name, maxtemp.name, family.name FROM covers cover',
            'INNER JOIN manufacturers manufacturer ON cover.mfg_id = manufacturer.id',
            'INNER JOIN materials material ON cover.material_id = material.id',
            'INNER JOIN temperatures mintemp ON cover.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON cover.max_temp_id = maxtemp.id',
            'INNER JOIN families family ON cover.family_id = family.id',
            'INNER JOIN series series ON cover.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Family': dict(),
            'Series': dict(),
            'Min Temp': dict(),
            'Max Temp': dict()
        }

        res = {}

        for (id, part_number, description, mfg, series, weight, mintemp, maxtemp, family) in data:

            res[part_number] = (mfg, description, series, family, weight, mintemp, maxtemp, id)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            if family not in commons['Family']:
                commons['Family'][family] = []

            commons['Family'][family].append(part_number)

            if series not in commons['Series']:
                commons['Series'][series] = []

            commons['Series'][series].append(part_number)

            if mintemp not in commons['Min Temp']:
                commons['Min Temp'][mintemp] = []

            commons['Min Temp'][mintemp].append(part_number)

            if maxtemp not in commons['Max Temp']:
                commons['Max Temp'][maxtemp] = []

            commons['Max Temp'][maxtemp].append(part_number)

        return res, commons


class Cover(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, DirectionMixin,
            FamilyMixin, SeriesMixin, ResourceMixin, TemperatureMixin,
            ColorMixin, DimensionMixin, WeightMixin, Model3DMixin):

    _table: CoversTable = None

    @property
    def pins(self) -> str:
        return self._table.select('pins', id=self._db_id)[0][0]

    @pins.setter
    def pins(self, value: str):
        self._table.update(self._db_id, pins=value)
