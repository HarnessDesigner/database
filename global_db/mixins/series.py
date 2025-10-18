from .base import BaseMixin


class SeriesMixin(BaseMixin):

    @property
    def series(self) -> "_series.Series":
        series_id = self._table.select('series_id', id=self._db_id)
        return _series.Series(self._table.db.series_table, series_id[0][0])

    @series.setter
    def series(self, value: "_series.Series"):
        self._table.update(self._db_id, series_id=value.db_id)

    @property
    def series_id(self) -> int:
        return self._table.select('series_id', id=self._db_id)[0][0]

    @series_id.setter
    def series_id(self, value: int):
        self._table.update(self._db_id, series_id=value)


from .. import series as _series  # NOQA
