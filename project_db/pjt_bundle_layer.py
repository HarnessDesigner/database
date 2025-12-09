
from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase
from ...wrappers.decimal import Decimal as _decimal

if TYPE_CHECKING:
    from . import pjt_bundle as _pjt_bundle
    from . import pjt_wire as _pjt_wire


class PJTBundleLayersTable(PJTTableBase):
    __table_name__ = 'pjt_bundle_layer'

    def __iter__(self) -> _Iterable["PJTBundleLayer"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBundleLayer(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTBundleLayer":
        if isinstance(item, int):
            if item in self:
                return PJTBundleLayer(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, bundle_id: int, layer_id: int, diameter: _decimal) -> "PJTBundleLayer":
        db_id = PJTTableBase.insert(self, bundle_id=bundle_id, layer_id=layer_id, diameter=float(diameter))

        return PJTBundleLayer(self, db_id, self.project_id)


class PJTBundleLayer(PJTEntryBase):
    _table: PJTBundleLayersTable = None

    @property
    def table(self) -> PJTBundleLayersTable:
        return self._table

    @property
    def wires(self) -> list["_pjt_wire.PJTWire"]:
        res = []
        db_ids = self._table.db.pjt_wires_table.select('id', layer_id=self.db_id)
        for db_id in db_ids:
            res.append(self._table.db.pjt_wires_table[db_id[0]])

        return res

    @property
    def bundle(self) -> "_pjt_bundle.PJTBundle":
        bundle_id = self.bundle_id
        return self._table.db.pjt_bundles_table[bundle_id]

    @property
    def bundle_id(self) -> int:
        return self._table.select('bundle_id', id=self._db_id)[0][0]

    @bundle_id.setter
    def bundle_id(self, value: int):
        self._table.update(self._db_id, bundle_id=value)
        self._process_callbacks()

    @property
    def layer_id(self) -> int:
        return self._table.select('layer_id', id=self._db_id)[0][0]

    @layer_id.setter
    def layer_id(self, value: int):
        self._table.update(self._db_id, layer_id=value)
        self._process_callbacks()

    @property
    def diameter(self) -> _decimal:
        return _decimal(self._table.select('diameter', id=self._db_id)[0][0])

    @diameter.setter
    def diameter(self, value: _decimal):
        self._table.update(self._db_id, diameter=float(value))
        self._process_callbacks()
