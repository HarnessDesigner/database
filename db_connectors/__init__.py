from typing import Optional as _Optional, Generator as _Generator

from ...config import Config as _Config


CONNECTOR_SQLITE = 1
CONNECTOR_MYSQL = 2


class Config(_Config):
    db_connector = CONNECTOR_SQLITE


class ConnectorBase:

    def __init__(self, mainframe, db_name):
        self.mainframe = mainframe
        self.db_name = db_name
        self.create_tables = False

    def connect(self) -> bool:
        raise NotImplementedError

    def execute(self, operation: str,
                params: _Optional[tuple] = None,
                multi: bool = False) -> _Optional[_Generator]:
        raise NotImplementedError

    def executemany(self, operation: str,
                    seq_params: list | tuple) -> _Optional[_Generator]:
        raise NotImplementedError

    @property
    def lastrowid(self) -> _Optional[int]:
        raise NotImplementedError

    def fetchone(self) -> _Optional[list[tuple]]:
        raise NotImplementedError

    def fetchmany(self, size: _Optional[int] = None) -> list[tuple]:
        raise NotImplementedError

    def fetchall(self) -> list[tuple]:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


if Config.db_connector == CONNECTOR_SQLITE:
    from .sqlite_connector import SQLConnector

elif Config.db_connector == CONNECTOR_MYSQL:
    from .mysql_connector import SQLConnector
else:
    raise RuntimeError('Unknown connector type')


