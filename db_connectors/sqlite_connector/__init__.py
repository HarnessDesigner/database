from typing import (
    Dict as _Dict,
    Optional as _Optional,
    Sequence as _Sequence,
    Union as _Union,
    Generator as _Generator,
    List as _List,
    Tuple as _Tuple,
    Set as _Set
)


from datetime import (
    date as _date,
    datetime as _datetime,
    time as _time,
    timedelta as _timedelta
)

from decimal import Decimal as _Decimal
from time import struct_time as _struct_time

import os
import sqlite3

from ....config import Config as _Config
from .... import utils
from .. import ConnectorBase


class Config(metaclass=_Config):
    database_path = os.path.join(utils.get_appdata(), 'harness_maker.db')


_StrOrBytes = _Union[str, bytes]

_ToMysqlInputTypes = _Optional[_Union[int, float, _Decimal, _StrOrBytes, bool,
                                      _datetime, _date, _time, _struct_time, _timedelta]]

_ToPythonOutputTypes = _Optional[_Union[float, int, _Decimal, _StrOrBytes, _date,
                                        _timedelta, _datetime, _Set[str]]]
_ParamsSequenceType = _Sequence[_ToMysqlInputTypes]
_ParamsDictType = _Dict[str, _ToMysqlInputTypes]
_ParamsSequenceOrDictType = _Union[_ParamsDictType, _ParamsSequenceType]

_RowType = _Tuple[_ToPythonOutputTypes, ...]


class SQLConnector(ConnectorBase):

    def __init__(self, mainframe):
        super().__init__(mainframe, Config.database_path)

        if not os.path.exists(Config.database_path):
            self.create_tables = True

        self._connection: sqlite3.Connection = None
        self._cursor: sqlite3.Cursor = None

    def connect(self):
        self._connection = sqlite3.connect(self.db_name)
        self._cursor = self._connection.cursor()

    def execute(self, operation: str,
                params: _Optional[_ParamsSequenceOrDictType] = None,
                _=None) -> _Optional[_Generator[sqlite3.Cursor, None, None]]:

        if params is None:
            return self._cursor.execute(operation)
        else:
            return self._cursor.execute(operation, params)

    def executemany(
        self, operation: str, seq_params: _Sequence[_ParamsSequenceOrDictType]
    ) -> _Optional[_Generator[sqlite3.Cursor, None, None]]:

        return self._cursor.executemany(operation, seq_params)

    @property
    def lastrowid(self) -> _Optional[int]:
        return self._cursor.lastrowid

    def fetchone(self) -> _Optional[_RowType]:
        return self._cursor.fetchone()

    def fetchmany(self, size: _Optional[int] = None) -> _List[_RowType]:
        return self._cursor.fetchmany(size)

    def fetchall(self) -> _List[_RowType]:
        return self._cursor.fetchall()

    def commit(self):
        self._connection.commit()

    def close(self):
        self.commit()

        self._cursor.close()
        self._connection.close()

        self._cursor = None
        self._connection = None
