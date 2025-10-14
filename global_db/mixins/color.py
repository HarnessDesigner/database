from . import BaseMixin


class ColorMixin(BaseMixin):

    @property
    def color(self) -> "_color.Color":
        color_id = self._table.select('color_id', id=self._db_id)
        return _color.Color(self._table.db.colors_table, color_id[0][0])

    @color.setter
    def color(self, value: "_color.Color"):
        self._table.update(self._db_id, color_id=value.db_id)

    @property
    def color_id(self) -> int:
        return self._table.select('color_id', id=self._db_id)[0][0]

    @color_id.setter
    def color_id(self, value: int):
        self._table.update(self._db_id, color_id=value)


from .. import color as _color  # NOQA
