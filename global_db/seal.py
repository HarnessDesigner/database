from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
                     ColorMixin, TemperatureMixin, ResourceMixin, WeightMixin, Model3DMixin)


class SealsTable(TableBase):
    __table_name__ = 'seals'

    def __iter__(self) -> _Iterable["Seal"]:
        for db_id in TableBase.__iter__(self):
            yield Seal(self, db_id)

    def __getitem__(self, item) -> "Seal":
        if isinstance(item, int):
            if item in self:
                return Seal(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return Seal(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, series_id: int, type: str, hardness: int,  # NOQA
               color_id: int, lubricant: str, min_temp_id: int, max_temp_id: int, length: float, o_dia: float,
               i_dia: float, wire_dia_min: float, wire_dia_max: float, image_id: int, datasheet_id: int,
               cad_id: int, weight: float) -> "Seal":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 series_id=series_id, type=type, hardness=hardness, color_id=color_id,
                                 lubricant=lubricant, min_temp_id=min_temp_id, max_temp_id=max_temp_id,
                                 length=length, o_dia=o_dia, i_dia=i_dia, wire_dia_min=wire_dia_min,
                                 wire_dia_max=wire_dia_max, image_id=image_id, datasheet_id=datasheet_id,
                                 cad_id=cad_id, weight=weight)
        return Seal(self, db_id)

    def parts_list(self):
        cmd = (
            'SELECT seal.id, seal.part_number, seal.description, manufacturer.name,',
            'series.name, seal.weight, mintemp.name, maxtemp.name, seal.o_dia,',
            'seal.i_dia, seal.type, seal.wire_dia_min, seal.wire_dia_max FROM seals seal',
            'INNER JOIN manufacturers manufacturer ON seal.mfg_id = manufacturer.id',
            'INNER JOIN temperatures mintemp ON seal.min_temp_id = mintemp.id',
            'INNER JOIN temperatures maxtemp ON seal.max_temp_id = maxtemp.id',
            'INNER JOIN series series ON seal.series_id = series.id;'
        )
        cmd = ' '.join(cmd)
        data = self.execute(cmd)

        commons = {
            'Manufacturer': dict(),
            'Outside Diameter': dict(),
            'Inside Diameter': dict(),
            'Type': dict(),
            'Min Wire Diameter': dict(),
            'Max Wire Diameter': dict(),
            'Series': dict(),
            'Min Temp': dict(),
            'Max Temp': dict()
        }

        res = {}

        for (id, part_number, description, mfg, series, weight, mintemp, maxtemp,
             o_dia, i_dia, type, wire_dia_min, wire_dia_max) in data:

            res[part_number] = (id, description, mfg, series, weight, mintemp,
                                maxtemp, o_dia, i_dia, type, wire_dia_min, wire_dia_max)

            if mfg not in commons['Manufacturer']:
                commons['Manufacturer'][mfg] = []

            commons['Manufacturer'][mfg].append(part_number)

            if o_dia not in commons['Outside Diameter']:
                commons['Outside Diameter'][o_dia] = []

            commons['Outside Diameter'][o_dia].append(part_number)

            if i_dia not in commons['Inside Diameter']:
                commons['Inside Diameter'][i_dia] = []

            commons['Inside Diameter'][i_dia].append(part_number)

            if type not in commons['Type']:
                commons['Type'][type] = []

            commons['Type'][type].append(part_number)

            if wire_dia_min not in commons['Min Wire Diameter']:
                commons['Min Wire Diameter'][wire_dia_min] = []

            commons['Min Wire Diameter'][wire_dia_min].append(part_number)

            if wire_dia_max not in commons['Max Wire Diameter']:
                commons['Max Wire Diameter'][wire_dia_max] = []

            commons['Max Wire Diameter'][wire_dia_max].append(part_number)

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


class Seal(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
           ColorMixin, TemperatureMixin, ResourceMixin, WeightMixin, Model3DMixin):

    _table: SealsTable = None

    @property
    def o_dia(self) -> float:
        return self._table.select('o_dia', id=self._db_id)[0][0]

    @o_dia.setter
    def o_dia(self, value: float):
        self._table.update(self._db_id, o_dia=value)

    @property
    def i_dia(self) -> float:
        return self._table.select('i_dia', id=self._db_id)[0][0]

    @i_dia.setter
    def i_dia(self, value: float):
        self._table.update(self._db_id, i_dia=value)

    @property
    def type(self) -> str:
        return self._table.select('type', id=self._db_id)[0][0]

    @type.setter
    def type(self, value: str):
        self._table.update(self._db_id, type=value)

    @property
    def hardness(self) -> int:
        return self._table.select('hardness', id=self._db_id)[0][0]

    @hardness.setter
    def hardness(self, value: int):
        self._table.update(self.hardness, i_dia=value)

    @property
    def lubricant(self) -> str:
        return self._table.select('lubricant', id=self._db_id)[0][0]

    @lubricant.setter
    def lubricant(self, value: str):
        self._table.update(self._db_id, lubricant=value)

    @property
    def length(self) -> float:
        return self._table.select('length', id=self._db_id)[0][0]

    @length.setter
    def length(self, value: float):
        self._table.update(self._db_id, length=value)

    @property
    def wire_dia_min(self) -> float:
        return self._table.select('wire_dia_min', id=self._db_id)[0][0]

    @wire_dia_min.setter
    def wire_dia_min(self, value: float):
        self._table.update(self._db_id, wire_dia_min=value)

    @property
    def wire_dia_max(self) -> float:
        return self._table.select('wire_dia_max', id=self._db_id)[0][0]

    @wire_dia_max.setter
    def wire_dia_max(self, value: float):
        self._table.update(self._db_id, wire_dia_max=value)
