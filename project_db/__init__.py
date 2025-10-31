
from typing import Iterable as _Iterable, TYPE_CHECKING

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
        self._pjt_terminals_table = None
        self._points_2d = []
        self._points_3d = []

        self._current_count = 0

    def load(self, project_id):
        self.mainframe.unload()

        self._current_count = 0

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
        self._pjt_terminals_table = PJTTerminalsTable(self, project_id)

        # the points are how we initially identify thing. It links together
        # the various objects. As an example say I have a wire and in the
        # middle of that wire there is a "layout" to add a bend in the wire.
        # the actual back end code has that translated into 2 wires and a
        # layout where the ends of the wire that share the layout also share
        # the same point as the layout on those ends. So When a user grabs that
        # layout and moves it when the coordinates change for the point the
        # layout position and each end of the wire  positions all get changed
        # in a single go. The editor representation for only those specific
        # objects get redrawn. I don't need to hold any references to any of
        # the objects other than the shared points. This is due to how matplotlib
        # is written and me having the ability to extend/monkeypath portions
        # of the matplotlib code where I am able to attach our objects to the
        # matplotlib objects (artists) that represent the graphical elements
        # in the editor. This works out well because I was able to entend matplotlib
        # so it properly translates screen cords into world coords so mouse interaction
        # takes place. I am able to adjust the coordinates of our object from events
        # that occur in the matplot lib objects.

        self._points_2d = [point.point for point in self._pjt_coordinates_2d_table]
        self._points_3d = [point.point for point in self._pjt_coordinates_3d_table]

        # the loading occurs using multiple threads to speed things up.
        # The plan is to have a thread running that creates multiple SQL
        # connections. One thread and one connection for each of the database
        # tables. The main thread will be responsible only for rendering the
        # GUI. There will be a few more threads that do the actual number
        # crunching. In order to use actual parallel processing I will be using
        # Python with the GIL turned off. I have to see if that is even possible
        # yet if I compile the program using Cython.
        self.mainframe.load()

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
    def pjt_terminals_table(self) -> PJTTerminalsTable:
        return self._pjt_terminals_table
