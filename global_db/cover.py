from typing import Iterable as _Iterable

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, DirectionMixin,
                     FamilyMixin, SeriesMixin, ResourceMixin, WeightMixin,
                     TemperatureMixin, ColorMixin, DimensionMixin)


class CoversTable(TableBase):
    __table_name__ = 'covers'

    def __iter__(self) -> _Iterable["Cover"]:
        for db_id in TableBase.__iter__(self):
            yield Cover(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int,
               direction_id: int, min_temp_id: int, max_temp_id: int, color_id: int,
               length: float, width: float, height: float, pins: str, weight: float) -> "Cover":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, direction_id=direction_id,
                                 min_temp_id=min_temp_id, max_temp_id=max_temp_id, color_id=color_id,
                                 length=length, width=width, height=height, pins=pins, weight=weight)

        return Cover(self, db_id)


class Cover(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, DirectionMixin,
            FamilyMixin, SeriesMixin, ResourceMixin, TemperatureMixin,
            ColorMixin, DimensionMixin, WeightMixin):

    _table: CoversTable = None

    @property
    def pins(self) -> str:
        return self._table.select('pins', id=self._db_id)[0][0]

    @pins.setter
    def pins(self, value: str):
        self._table.update(self._db_id, pins=value)
