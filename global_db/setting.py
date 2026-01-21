from typing import Iterable as _Iterable

from . import EntryBase, TableBase


class SettingsTable(TableBase):
    __table_name__ = 'settings'

    def __getitem__(self, item) -> "Setting":
        if isinstance(item, int):
            value = self.select('value', id=item)
            if not value:
                raise IndexError(str(item))

            return eval(value[0][0])

        value = self.select('value', name=item)

        if not value:
            raise AttributeError(item)

        return eval(value[0][0])
