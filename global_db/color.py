from typing import Iterable as _Iterable
import weakref

from . import EntryBase, TableBase
from .mixins import NameMixin

from ...wrappers import color as _color


class ColorsTable(TableBase):
    __table_name__ = 'colors'

    def __iter__(self) -> _Iterable["Color"]:
        for db_id in TableBase.__iter__(self):
            yield Color(self, db_id)

    def __getitem__(self, item) -> "Color":
        if isinstance(item, int):
            if item in self:
                return Color(self, item)
            raise IndexError(str(item))

        db_id = self.select('id', name=item)
        if db_id:
            return Color(self, db_id[0][0])

        raise KeyError(item)

    def insert(self, name: str, rgb: int) -> "Color":
        db_id = TableBase.insert(self, name=name, rgb=rgb)
        return Color(self, db_id)


class Color(EntryBase, NameMixin):
    _color_instances = {}

    _table: ColorsTable = None

    @classmethod
    def _remove_ref(cls, ref):
        for key, value in list(cls._color_instances.items()):
            if value != ref:
                continue

            del cls._color_instances[key]
            break

    def _update_color(self, c: _color.Color) -> None:
        self.rgba = (c.GetRed(), c.GetGreen(), c.GetBlue)

    @property
    def ui(self) -> _color.Color:
        if self.db_id in self._color_instances:
            ref = self._color_instances[self.db_id]
            color = ref()
            if color is not None:
                return color

        color = _color.Color(*self.rgb)
        color.Bind(self._update_color)
        self._color_instances[self.db_id] = weakref.ref(color, Color._remove_ref)
        return color

    @property
    def rgb(self) -> tuple[int, int, int, int]:
        rgb = self._table.select('rgb', id=self._db_id)[0][0]

        r = rgb >> 16
        g = (rgb >> 8) & 0xff
        b = rgb & 0xFF
        return r, g, b, 255

    @rgb.setter
    def rgb(self, value: tuple[int, int, int, int]):
        r, g, b = value[:3]

        rgb = r << 16 | b << 8 | b

        self._table.update(self._db_id, rgb=rgb)
