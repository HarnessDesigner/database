from typing import Iterable as _Iterable

from . import EntryBase, TableBase
from .mixins import NameMixin


class ColorsTable(TableBase):
    __table_name__ = 'colors'

    def __iter__(self) -> _Iterable["Color"]:
        for db_id in TableBase.__iter__(self):
            yield Color(self, db_id)

    def insert(self, name: str, rgb: int) -> "Color":
        db_id = TableBase.insert(self, name=name, rgb=rgb)
        return Color(self, db_id)


class Color(EntryBase, NameMixin):
    _table: ColorsTable = None

    @property
    def rgb(self) -> tuple[int, int, int, int]:
        rgb = self._table.select('rgb', id=self._db_id)[0][0]

        r = rgb >> 16
        g = (rgb >> 8) & 0xff
        b = rgb & 0xFF
        return r, g, b, 255

    @rgb.setter
    def rgb(self, value: tuple[int, int, int]):
        r, g, b = value[:3]

        rgb = r << 16 | b << 8 | b

        self._table.update(self._db_id, rgb=rgb)
