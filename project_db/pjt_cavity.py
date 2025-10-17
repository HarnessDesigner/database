
from typing import Iterable as _Iterable

from . import PJTEntryBase, PJTTableBase


class PJTCavitiesTable(PJTTableBase):
    __table_name__ = 'pjt_cavities'

    def __iter__(self) -> _Iterable["PJTCavity"]:

        for db_id in PJTTableBase.__iter__(self):
            yield PJTCavity(self, db_id, self.project_id)

    def insert(self, part_id: int, cavity_map_id: int, terminal_id: int, name: str) -> "PJTCavity":
        db_id = PJTTableBase.insert(self, part_id=part_id, cavity_map_id=cavity_map_id,
                                    terminal_id=terminal_id, name=name)

        return PJTCavity(self, db_id, self.project_id)


class PJTCavity(PJTEntryBase):
    _table: PJTCavitiesTable = None

    @property
    def name(self) -> str:
        return self._table.select('name', id=self._db_id)[0][0]

    @name.setter
    def name(self, value: str):
        self._table.update(self._db_id, name=value)

    @property
    def cavity_map(self) -> "_pjt_cavity_map.PJTCavityMap":
        cavity_map_id = self.cavity_map_id
        return self._table.db.pjt_cavity_maps_table[cavity_map_id]

    @property
    def cavity_map_id(self) -> int:
        return self._table.select('cavity_map_id', id=self._db_id)[0][0]

    @cavity_map_id.setter
    def cavity_map_id(self, value: int):
        self._table.update(self._db_id, cavity_map_id=value)

    @property
    def cavities(self) -> "_pjt_terminal.PJTTerminal":

        terminal_ids = self._table.db.pjt_terminals_table.select('id', cavity_id=self._db_id)
        if terminal_ids:
            terminal_id = terminal_ids[0][0]
            terminal = _pjt_terminal.PJTTerminal(
                self._table.db.pjt_terminals_table, terminal_id, self.project_id)

            return terminal

    @property
    def part(self) -> "_cavity.Cavity":
        part_id = self.part_id
        if part_id is None:
            return None

        return self._table.db.global_db.cavities_table[part_id]

    @property
    def part_id(self) -> int:
        return self._table.select('part_id', id=self._db_id)[0][0]

    @part_id.setter
    def part_id(self, value: int):
        self._table.update(self._db_id, part_id=value)


from . import pjt_cavity_map as _pjt_cavity_map  # NOQA
from . import pjt_terminal as _pjt_terminal  # NOQA

from ..global_db import cavity as _cavity  # NOQA
