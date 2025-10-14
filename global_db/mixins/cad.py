from . import BaseMixin


class CADMixin(BaseMixin):

    @property
    def cad(self) -> "_cad.CAD":
        cad_id = self._table.select('cad_id', id=self._db_id)
        return _cad.CAD(self._table.db.cads_table, cad_id[0][0])

    @cad.setter
    def cad(self, value: "_cad.CAD"):
        self._table.update(self._db_id, cad_id=value.db_id)

    @property
    def cad_id(self) -> int:
        return self._table.select('cad_id', id=self._db_id)[0][0]

    @cad_id.setter
    def cad_id(self, value: int):
        self._table.update(self._db_id, cad_id=value)


from .. import cad as _cad  # NOQA
