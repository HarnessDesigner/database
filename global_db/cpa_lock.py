
from typing import Iterable as _Iterable
from . import EntryBase, TableBase
from ...wrappers.decimal import Decimal as _decimal

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
                     SeriesMixin, ResourceMixin, TemperatureMixin, WeightMixin,
                     ColorMixin, DimensionMixin, Model3DMixin)


class CPALocksTable(TableBase):
    __table_name__ = 'cpa_locks'

    def __iter__(self) -> _Iterable["CPALock"]:

        for db_id in TableBase.__iter__(self):
            yield CPALock(self, db_id)

    def __getitem__(self, item) -> "CPALock":
        if isinstance(item, int):
            if item in self:
                return CPALock(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return CPALock(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int, min_temp_id: int,
               max_temp_id: int, pins: str, color_id: int, length: _decimal, width: _decimal,
               height: _decimal, terminal_size: _decimal, weight: _decimal) -> "CPALock":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, min_temp_id=min_temp_id,
                                 max_temp_id=max_temp_id, pins=pins, color_id=color_id, length=float(length),
                                 width=float(width), height=float(height), terminal_size=float(terminal_size), weight=float(weight))

        return CPALock(self, db_id)

    @property
    def search_items(self) -> dict:
        ret = {
            0: {
                'label': 'Part Number',
                'type': [str],
                'out_params': 'part_number'
            },
            1: {
                'label': 'Description',
                'type': [str],
                'out_params': 'description'
            },
            2: {
                'label': 'Manufacturer',
                'type': [int, str],
                'search_params': ['mfg_id', 'manufacturers', 'name']
            },
            3: {
                'label': 'Family',
                'type': [int, str],
                'search_params': ['family_id', 'families', 'name']
            },
            4: {
                'label': 'Series',
                'type': [int, str],
                'search_params': ['series_id', 'series', 'name']
            },
            5: {
                'label': 'Color',
                'type': [int, str],
                'search_params': ['color_id', 'colors', 'name']
            },
            6: {
                'label': 'Direction',
                'type': [int, str],
                'search_params': ['direction_id', 'directions', 'name']
            },
            7: {
                'label': 'Temperature (Min)',
                'type': [int, str],
                'search_params': ['min_temp_id', 'temperatures', 'name']
            },
            8: {
                'label': 'Temperature (Max)',
                'type': [int, str],
                'search_params': ['max_temp_id', 'temperatures', 'name']
            },
            9: {
                'label': 'Length (mm)',
                'type': [float],
                'search_params': ['length']
            },
            10: {
                'label': 'Width (mm)',
                'type': [float],
                'search_params': ['width']
            },
            11: {
                'label': 'Height (mm)',
                'type': [float],
                'search_params': ['height']
            },
            12: {
                'label': 'Weight (g)',
                'type': [float],
                'search_params': ['weight']
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
            'SELECT cpa_lock.id, cpa_lock.part_number, cpa_lock.description,',
            'manufacturer.name, series.name, cpa_lock.weight, mintemp.name,',
            'maxtemp.name, family.name FROM cpa_locks cpa_lock',
            'INNER JOIN manufacturers manufacturer ON cpa_lock.mfg_id = manufacturer.id',
            'INNER JOIN temperatures mintemp ON cpa_lock.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON cpa_lock.max_temp_id = maxtemp.id',
            'INNER JOIN families family ON cpa_lock.family_id = family.id',
            'INNER JOIN series series ON cpa_lock.series_id = series.id;'
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


class CPALock(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
              SeriesMixin, ResourceMixin, TemperatureMixin, WeightMixin,
              ColorMixin, DimensionMixin, Model3DMixin):

    _table: CPALocksTable = None

    @property
    def pins(self) -> str:
        return self._table.select('pins', id=self._db_id)[0][0]

    @pins.setter
    def pins(self, value: str):
        self._table.update(self._db_id, pins=value)

    @property
    def terminal_size(self) -> _decimal:
        return _decimal(self._table.select('terminal_size', id=self._db_id)[0][0])

    @terminal_size.setter
    def terminal_size(self, value: _decimal):
        self._table.update(self._db_id, terminal_size=float(value))
