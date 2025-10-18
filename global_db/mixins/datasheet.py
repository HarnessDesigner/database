from .base import BaseMixin


class DatasheetMixin(BaseMixin):

    @property
    def datasheet(self) -> "_datasheet.Datasheet":
        datasheet_id = self._table.select('datasheet_id', id=self._db_id)
        return _datasheet.Datasheet(self._table.db.datasheets_table, datasheet_id[0][0])

    @datasheet.setter
    def datasheet(self, value: "_datasheet.Datasheet"):
        self._table.update(self._db_id, datasheet_id=value.db_id)

    @property
    def datasheet_id(self) -> int:
        return self._table.select('datasheet_id', id=self._db_id)[0][0]

    @datasheet_id.setter
    def datasheet_id(self, value: int):
        self._table.update(self._db_id, datasheet_id=value)


from .. import datasheet as _datasheet  # NOQA
