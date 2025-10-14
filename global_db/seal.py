from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
                     ColorMixin, TemperatureMixin, ImageMixin, DatasheetMixin, CADMixin)


class SealsTable(TableBase):
    __table_name__ = 'seals'

    def __iter__(self) -> _Iterable["Seal"]:
        for db_id in TableBase.__iter__(self):
            yield Seal(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, series_id: int, type: str, hardness: int,  # NOQA
               color_id: int, lubricant: str, min_temp_id: int, max_temp_id: int, length: float, o_dia: float,
               i_dia: float, wire_dia_min: float, wire_dia_max: float, image_id: int, datasheet_id: int,
               cad_id: int) -> "Seal":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 series_id=series_id, type=type, hardness=hardness, color_id=color_id,
                                 lubricant=lubricant, min_temp_id=min_temp_id, max_temp_id=max_temp_id,
                                 length=length, o_dia=o_dia, i_dia=i_dia, wire_dia_min=wire_dia_min,
                                 wire_dia_max=wire_dia_max, image_id=image_id, datasheet_id=datasheet_id,
                                 cad_id=cad_id)
        return Seal(self, db_id)


class Seal(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, SeriesMixin,
           ColorMixin, TemperatureMixin, ImageMixin, DatasheetMixin, CADMixin):

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
