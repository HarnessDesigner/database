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

import wx

from datetime import (
    date as _date,
    datetime as _datetime,
    time as _time,
    timedelta as _timedelta
)

from decimal import Decimal as _Decimal
from time import struct_time as _struct_time

import os

try:
    from ....config import Config as _Config
except ImportError:
    class _Config:
        pass

from .... import utils
import sqlite3


class Config(_Config):
    autosave_interval = 5  # minutes
    global_database_path = os.path.join(utils.get_appdata(), 'harness_maker_global_database.db')
    recent_projects = []


_StrOrBytes = _Union[str, bytes]

_ToMysqlInputTypes = _Optional[_Union[int, float, _Decimal, _StrOrBytes, bool,
                                      _datetime, _date, _time, _struct_time, _timedelta]]

_ToPythonOutputTypes = _Optional[_Union[float, int, _Decimal, _StrOrBytes, _date,
                                        _timedelta, _datetime, _Set[str]]]
_ParamsSequenceType = _Sequence[_ToMysqlInputTypes]
_ParamsDictType = _Dict[str, _ToMysqlInputTypes]
_ParamsSequenceOrDictType = _Union[_ParamsDictType, _ParamsSequenceType]

_RowType = _Tuple[_ToPythonOutputTypes, ...]


class _DBase:

    def __init__(self, sql_connector, db_name):
        self.sql_connector = sql_connector
        self.db_name = db_name
        self._connection: sqlite3.Connection = None
        self._cursor: sqlite3.Cursor = None

    def connect(self):
        self._connection = sqlite3.connect(self.db_name)
        self._cursor = self._connection.cursor()

    def execute(self, operation: _StrOrBytes,
                params: _Optional[_ParamsSequenceOrDictType] = None,
                ) -> _Optional[_Generator[sqlite3.Cursor, None, None]]:
        self._cursor.execute(operation, params)

    def executemany(
        self, operation: str, seq_params: _Sequence[_ParamsSequenceOrDictType]
    ) -> _Optional[_Generator[sqlite3.Cursor, None, None]]:

        self._cursor.executemany(operation, seq_params)

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


class GlobalDBase(_DBase):
    pass


def _get_default_project_path():
    pp = os.path.join(os.path.expanduser('~'), 'Harness Maker')
    if not os.path.exists(pp):
        os.mkdir(pp)

    return pp


class ProjectDBase(_DBase):

    def __init__(self, sql_connector, db_name):
        super().__init__(sql_connector, db_name)
        self._project_id = None

        self._project = None
        self.timer = wx.Timer(sql_connector.parent)

        if Config.recent_projects:
            last_path = Config.recent_projects[0]

            if os.path.exists(last_path + '._auto_save'):
                dlg = wx.MessageDialog(sql_connector.parent,
                                       'Well this is embarassing...\nA crash may have occured. Would you like to resume the last session?',
                                       'Crash Recovery', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)

                dlg.CenterOnParent()
                if dlg.ShowModal() == wx.ID_YES:
                    self.load_project(last_path + '._auto_save')

    def select_project(self):
        from .project_dialog import OpenProjectDialog
        if Config.recent_projects:
            last_path = os.path.split(Config.recent_projects[0])[0]
        else:
            last_path = _get_default_project_path()

        if not os.path.exists(last_path):
            last_path = _get_default_project_path()

        dlg = OpenProjectDialog(self.sql_connector.parent, last_path)

        if dlg.ShowModal() != wx.ID_CANCEL:
            project_file = dlg.GetPath()
        else:
            project_file = None

        dlg.Destroy()

        return project_file

    def connect(self):
        return

    def load_project(self, project):
        if not project.endswith('.hrn._auto_save') and not project.endswith('hrn'):
            project += '.hrn'
        self._project_id = 1

        try:
            self._connection = sqlite3.connect(':memory:')
            backup_db = sqlite3.connect(project)
            self._connection.backup(backup_db)
            backup_db.close()

            self._cursor = self._connection.cursor()

        except:  # NOQA
            print('Database failed to open')
            # show error dialog

        else:
            if project.endswith('.hrn'):
                if project in Config.recent_projects:
                    Config.recent_projects.remove(project)

                Config.recent_projects.insert(0, project)

                while len(Config.recent_projects) > 5:
                    Config.recent_projects = Config.recent_projects[:-1]

            self._project = project

            self.sql_connector.parent.Bind(wx.EVT_TIMER, self._on_backup, id=self.timer.GetId())
            self.timer.Start(Config.autosave_interval * 60 * 1000)

    def _on_backup(self, evt):
        self.sql_connector.parent.SetStatus('auto saving.....')

        if self._project.endswith('._auto_save'):
            project = self._project
        else:
            project = self._project + '._auto_save'

        if os.path.exists(project):
            os.remove(project)

        backup_db = sqlite3.connect(project)
        self._connection.commit()
        backup_db.backup(self._connection)
        backup_db.close()

        self.sql_connector.parent.SetStatus('')

        evt.Skip()

    @property
    def recent_projects(self):
        return Config.recent_projects[:]


class SQLConnector:

    def __init__(self, parent):
        self.parent = parent
        self.global_db = GlobalDBase(self, Config.global_database_path)
        self.project_db = ProjectDBase(self, Config.project_database_name)
