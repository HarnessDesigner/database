from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
                     SeriesMixin, ResourceMixin, TemperatureMixin,
                     ColorMixin, DimensionMixin)


class TPALocksTable(TableBase):
    __table_name__ = 'tpa_locks'

    def __iter__(self) -> _Iterable["TPALock"]:

        for db_id in TableBase.__iter__(self):
            yield TPALock(self, db_id)

    def __getitem__(self, item) -> "TPALock":
        if isinstance(item, int):
            if item in self:
                return TPALock(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', part_number=item)
        if db_id:
            return TPALock(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int, min_temp_id: int,
               max_temp_id: int, pins: str, color_id: int, length: float, width: float,
               height: float, terminal_size: float) -> "TPALock":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, min_temp_id=min_temp_id,
                                 max_temp_id=max_temp_id, pins=pins, color_id=color_id, length=length,
                                 width=width, height=height, terminal_size=terminal_size)

        return TPALock(self, db_id)


class TPALock(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
              SeriesMixin, ResourceMixin, TemperatureMixin,
              ColorMixin, DimensionMixin):

    _table: TPALocksTable = None

    @property
    def pins(self) -> str:
        return self._table.select('pins', id=self._db_id)[0][0]

    @pins.setter
    def pins(self, value: str):
        self._table.update(self._db_id, pins=value)

    @property
    def terminal_size(self) -> float:
        return self._table.select('terminal_size', id=self._db_id)[0][0]

    @terminal_size.setter
    def terminal_size(self, value: float):
        self._table.update(self._db_id, terminal_size=value)
