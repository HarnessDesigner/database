
from typing import Iterable as _Iterable, TYPE_CHECKING
import wx


from ....config import Config as _Config


class Config(_Config):
    recent_projects = []


if TYPE_CHECKING:
    from ... import ui as _ui


class PJTEntryBase:

    def __init__(self, table: "PJTTableBase", db_id: int, project_id: int):
        self._table = table
        self._db_id = db_id
        self.project_id = project_id

    @property
    def db_id(self):
        return self._db_id

    def delete(self) -> None:
        self._table.delete(self.db_id)


class PJTTableBase:
    __table_name__: str = None

    def __init__(self, db: "PJTTables", project_id: int | None = None):
        self.db = db
        self._con = db.connector

        self.project_id = project_id

    def __getitem__(self, item):
        self._con.execute(f'SELECT * FROM {self.__table_name__} WHERE id = {item};')

        for line in self._con.fetchall():
            return line

    def __iter__(self) -> _Iterable[int]:
        if self.project_id is None:
            self._con.execute(f'SELECT id FROM {self.__table_name__};')
        else:
            self._con.execute(f'SELECT id FROM {self.__table_name__} WHERE project_id = {self.project_id};')

        for line in self._con.fetchall():
            yield line[0]

    @property
    def table_name(self) -> str:
        return self.__table_name__

    def __contains__(self, db_id: int) -> bool:
        self._con.execute(f'SELECT id FROM {self.__table_name__} WHERE id = {db_id};')

        if self._con.fetchall():
            return True

        return False

    def insert(self, **kwargs) -> int:
        fields = []
        values = []
        args = []

        if self.project_id is not None:
            fields.append('project_id')
            values.append('?')
            args.append(self.project_id)

        for key, value in kwargs.items():
            fields.append(key)
            args.append(value)
            values.append('?')

        fields = ', '.join(fields)
        values = ', '.join(values)
        self._con.execute(f'INSERT INTO {self.__table_name__} ({fields}) VALUES ({values});', args)
        self._con.commit()
        return self._con.lastrowid

    def select(self, *args, **kwargs):
        args = ', '.join(args)

        values = []

        if self.project_id is not None:
            values.append(f'project_id = {self.project_id}')

        for key, value in kwargs.items():
            if isinstance(value, (str, float)):
                value = f'"{value}"'
            elif value is None:
                value = 'NULL'

            values.append(f'{key} = {value}')

        values = ' AND '.join(values)

        where = f' WHERE {values}'

        self._con.execute(f'SELECT {args} FROM {self.__table_name__}{where};')
        res = self._con.fetchall()
        return res

    def delete(self, db_id: int) -> None:
        self._con.execute(f'DELETE FROM {self.__table_name__} WHERE id = {db_id};')
        self._con.commit()

    def update(self, db_id: int, **kwargs):
        fields = []
        values = []

        for key, value in kwargs.items():
            fields.append(f'{key} = ?')
            values.append(value)

        fields = ', '.join(fields)
        self._con.execute(f'UPDATE {self.__table_name__} SET {fields} WHERE id = {db_id};', values)
        self._con.commit()

    def execute(self, cmd, params=None):
        if params is None:
            self._con.execute(cmd)
        else:
            self._con.execute(cmd, params)

    def fetchall(self):
        return self._con.fetchall()


from .pjt_bundle import PJTBundlesTable  # NOQA
from .pjt_bundle_layout import PJTBundleLayoutsTable  # NOQA
from .pjt_circuit import PJTCircuitsTable  # NOQA
from .pjt_coordinate_2d import PJTCoordinates2DTable  # NOQA
from .pjt_coordinate_3d import PJTCoordinates3DTable  # NOQA
from .pjt_housing import PJTHousingsTable  # NOQA
from .pjt_splice import PJTSplicesTable  # NOQA
from .pjt_transition import PJTTransitionsTable  # NOQA
from .pjt_wire import PJTWiresTable  # NOQA
from .pjt_wire2d_layout import PJTWire2DLayoutsTable  # NOQA
from .pjt_wire3d_layout import PJTWire3DLayoutsTable  # NOQA
from .pjt_cavity_map import PJTCavityMapsTable  # NOQA
from .pjt_cavity import PJTCavitiesTable  # NOQA
from .pjt_terminal import PJTTerminalsTable  # NOQA

from .project import ProjectsTable  # NOQA


class PJTTables:

    def __init__(self, mainframe: "_ui.MainFrame"):
        self.mainframe = mainframe
        self.global_db = mainframe.global_db
        self.connector = mainframe.db_connector

        self._projects_table = ProjectsTable(self)

        self._pjt_bundles_table = None
        self._pjt_bundle_layouts_table = None
        self._pjt_circuits_table = None
        self._pjt_coordinates_2d_table = None
        self._pjt_coordinates_3d_table = None
        self._pjt_housings_table = None
        self._pjt_splices_table = None
        self._pjt_transitions_table = None
        self._pjt_wires_table = None
        self._pjt_wire_2d_layouts_table = None
        self._pjt_wire_3d_layouts_table = None
        self._pjt_cavities_table = None
        self._pjt_cavity_maps_table = None
        self._pjt_terminals_table = None

    def load(self, project_id):
        self._pjt_bundles_table = PJTBundlesTable(self, project_id)
        self._pjt_bundle_layouts_table = PJTBundleLayoutsTable(self, project_id)
        self._pjt_circuits_table = PJTCircuitsTable(self, project_id)
        self._pjt_coordinates_2d_table = PJTCoordinates2DTable(self, project_id)
        self._pjt_coordinates_3d_table = PJTCoordinates3DTable(self, project_id)
        self._pjt_housings_table = PJTHousingsTable(self, project_id)
        self._pjt_splices_table = PJTSplicesTable(self, project_id)
        self._pjt_transitions_table = PJTTransitionsTable(self, project_id)
        self._pjt_wires_table = PJTWiresTable(self, project_id)
        self._pjt_wire_2d_layouts_table = PJTWire2DLayoutsTable(self, project_id)
        self._pjt_wire_3d_layouts_table = PJTWire3DLayoutsTable(self, project_id)
        self._pjt_cavities_table = PJTCavitiesTable(self, project_id)
        self._pjt_cavity_maps_table = PJTCavityMapsTable(self, project_id)
        self._pjt_terminals_table = PJTTerminalsTable(self, project_id)

    @property
    def pjt_bundles_table(self) -> PJTBundlesTable:
        return self._pjt_bundles_table

    @property
    def pjt_bundle_layouts_table(self) -> PJTBundleLayoutsTable:
        return self._pjt_bundle_layouts_table

    @property
    def pjt_circuits_table(self) -> PJTCircuitsTable:
        return self._pjt_circuits_table

    @property
    def pjt_coordinates_2d_table(self) -> PJTCoordinates2DTable:
        return self._pjt_coordinates_2d_table

    @property
    def pjt_coordinates_3d_table(self) -> PJTCoordinates3DTable:
        return self._pjt_coordinates_3d_table

    @property
    def pjt_housings_table(self) -> PJTHousingsTable:
        return self._pjt_housings_table

    @property
    def pjt_splices_table(self) -> PJTSplicesTable:
        return self._pjt_splices_table

    @property
    def pjt_transitions_table(self) -> PJTTransitionsTable:
        return self._pjt_transitions_table

    @property
    def pjt_wires_table(self) -> PJTWiresTable:
        return self._pjt_wires_table

    @property
    def pjt_wire_2d_layouts_table(self) -> PJTWire2DLayoutsTable:
        return self._pjt_wire_2d_layouts_table

    @property
    def pjt_wire_3d_layouts_table(self) -> PJTWire3DLayoutsTable:
        return self._pjt_wire_3d_layouts_table

    @property
    def projects_table(self) -> ProjectsTable:
        return self._projects_table

    @property
    def pjt_cavities_table(self) -> PJTCavitiesTable:
        return self._pjt_cavities_table

    @property
    def pjt_cavity_maps_table(self) -> PJTCavityMapsTable:
        return self._pjt_cavity_maps_table

    @property
    def pjt_terminals_table(self) -> PJTTerminalsTable:
        return self._pjt_terminals_table


class Project:

    def __init__(self, mainframe: "_ui.MainFrame"):
        self.mainframe = mainframe
        self.connector = self.mainframe.db_connector
        self.project_id = None
        self.project_name = ''
        self.tables = PJTTables(self.mainframe)

    def select_project(self):
        from ...dialogs.project_dialog import OpenProjectDialog

        project_names = []

        self.connector.execute(f'SELECT name FROM projects;')
        for name in self.connector.fetchall():
            project_names.append(name[0])

        dlg = OpenProjectDialog(self.mainframe, Config.recent_projects, project_names)

        if dlg.ShowModal() != wx.ID_CANCEL:
            project_name = dlg.GetValue()
        else:
            project_name = None

        dlg.Destroy()

        self.connector.execute(f'SELECT id FROM projects WHERE name = "{project_name};')
        res = self.connector.fetchall()

        if res:
            self.project_id = res[0][0]
        else:
            self.connector.execute(f'INSERT INTO projects (name) VALUES (?);', (project_name,))
            self.connector.commit()
            self.project_id = self.connector.lastrowid

        self.tables.load(self.project_id)

    @property
    def recent_projects(self):
        return Config.recent_projects[:]
