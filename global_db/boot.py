from typing import Union as _Union, Iterable as _Iterable

from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, ColorMixin,
                     FamilyMixin, SeriesMixin, ImageMixin, DatasheetMixin, CADMixin)


class BootsTable(TableBase):
    __table_name__ = 'boots'

    def __iter__(self) -> _Iterable["Boot"]:
        for db_id in TableBase.__iter__(self):
            yield Boot(self, db_id)

    def __getitem__(self, db_id) -> "Boot":
        if db_id in self:
            return Boot(self, db_id)

        raise IndexError(str(db_id))

    def get(self, part_number) -> _Union["Boot", None]:
        self._cur.execute(f'SELECT id from {self.__table_name__} WHERE part_number = "{part_number}";')
        for line in self._cur.fetchall():
            db_id = line[0]
            return Boot(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int, color_id: int) -> "Boot":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, color_id=color_id)

        return Boot(self, db_id)


class Boot(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
           SeriesMixin, ImageMixin, DatasheetMixin, CADMixin, ColorMixin):
    _table: BootsTable = None
