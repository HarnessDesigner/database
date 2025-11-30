from typing import TYPE_CHECKING, Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase

if TYPE_CHECKING:
    from . import pjt_housing as _pjt_housing

    from ..global_db import boot as _boot


class PJTBootsTable(PJTTableBase):
    __table_name__ = 'pjt_boots'

    def __iter__(self) -> _Iterable["PJTBoot"]:
        for db_id in PJTTableBase.__iter__(self):
            yield PJTBoot(self, db_id, self.project_id)

    def __getitem__(self, item) -> "PJTBoot":
        if isinstance(item, int):
            if item in self:
                return PJTBoot(self, item, self.project_id)
            raise IndexError(str(item))

        raise KeyError(item)

    def insert(self, part_id: int, housing_id: int | None) -> "PJTBoot":
        db_id = PJTTableBase.insert(self, part_id=part_id, housing_id=housing_id)

        return PJTBoot(self, db_id, self.project_id)


class PJTBoot(PJTEntryBase):
    _table: PJTBootsTable = None

    @property
    def table(self) -> PJTBootsTable:
        return self._table

    @property
    def part(self) -> "_boot.Boot":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.boots_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)
        self._process_callbacks()

    @property
    def housing(self) -> "_pjt_housing.PJTHousing":
        db_id = self.housing_id
        if db_id is None:
            return None

        return self._table.db.pjt_housings_table[db_id]

    @property
    def housing_id(self) -> int:
        return self._table.select('housing_id', id=self._db_id)[0][0]

    @housing_id.setter
    def housing_id(self, value: int):
        self._table.update(self._db_id, housing_id=value)
        self._process_callbacks()
