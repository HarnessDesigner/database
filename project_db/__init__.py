
from typing import Iterable as _Iterable, TYPE_CHECKING

import weakref

if TYPE_CHECKING:
    from ... import ui as _ui


class PJTEntryMeta(type):

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        cls._instances = {}

    def __call__(cls, table, db_id, project_id):
        if db_id not in cls._instances:
            cls._instances[db_id] = super().__call__(table, db_id, project_id)

        instance = cls._instances[db_id]

        return instance

    def unload(cls):
        cls._instances.clear()


class PJTEntryBase:

    def __init__(self, table: "PJTTableBase", db_id: int, project_id: int):
        self._table = table
        self._db_id = db_id
        self.project_id = project_id
        self.__callbacks = []
        self.__stop_callbacks = 0

    def __enter__(self):
        self.__stop_callbacks += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__stop_callbacks -= 1
        self._process_callbacks()

    def __remove_ref(self, ref):
        try:
            self.__callbacks.remove(ref)
        except ValueError:
            pass

    _selected: bool = False

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, flag: bool):
        self._selected = flag
        self._process_callbacks()

    def Bind(self, callback):
        for ref in self.__callbacks[:]:
            cb = ref()
            if cb is None:
                try:
                    self.__callbacks.remove(ref)
                except ValueError:
                    pass

            elif cb == callback:
                return
        else:
            self.__callbacks.append(weakref.ref(callback, self.__remove_ref))

    def Unbind(self, callback):
        for ref in self.__callbacks[:]:
            cb = ref()
            if cb is None:
                try:
                    self.__callbacks.remove(ref)
                except ValueError:
                    pass
            elif cb == callback:
                self.__callbacks.remove(ref)
                return

    def _process_callbacks(self):
        if self.__stop_callbacks > 0:
            return

        for ref in self.__callbacks[:]:
            cb = ref()
            if cb is None:
                try:
                    self.__callbacks.remove(ref)
                except ValueError:
                    pass

                continue

            cb(self)

    @property
    def db_id(self) -> int:
        return self._db_id

    @property
    def table(self):
        return self._table

    def delete(self) -> None:
        self._table.delete(self.db_id)

        del self.__class__._instances[self.db_id]  # NOQA

        self._process_callbacks()


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

    def select(self, *args, OR: bool = False, **kwargs):
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

        if OR:

            values = ' OR '.join(values)
        else:
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
from .pjt_bundle_layer import PJTBundleLayersTable  # NOQA
from .pjt_circuit import PJTCircuitsTable  # NOQA
from .pjt_point_2d import PJTPoints2DTable  # NOQA
from .pjt_point_3d import PJTPoints3DTable  # NOQA
from .pjt_housing import PJTHousingsTable  # NOQA
from .pjt_splice import PJTSplicesTable  # NOQA
from .pjt_transition import PJTTransitionsTable  # NOQA
from .pjt_wire import PJTWiresTable  # NOQA
from .pjt_wire2d_layout import PJTWire2DLayoutsTable  # NOQA
from .pjt_wire3d_layout import PJTWire3DLayoutsTable  # NOQA
from .pjt_cavity import PJTCavitiesTable  # NOQA
from .pjt_terminal import PJTTerminalsTable  # NOQA
from .pjt_wire_marker import PJTWireMarkersTable  # NOQA
from .pjt_seal import PJTSealsTable  # NOQA
from .pjt_cover import PJTCoversTable  # NOQA
from .pjt_boot import PJTBootsTable  # NOQA
from .pjt_cpa_lock import PJTCPALocksTable  # NOQA
from .pjt_tpa_lock import PJTTPALocksTable  # NOQA
from .pjt_wire_service_loop import PJTWireServiceLoopsTable  # NOQA

from .project import ProjectsTable  # NOQA


class PJTTables:

    def __init__(self, mainframe: "_ui.MainFrame"):
        self.mainframe = mainframe
        self.global_db = mainframe.global_db
        self.connector = mainframe.db_connector

        self._projects_table = ProjectsTable(self)

        self._pjt_bundles_table = None
        self._pjt_bundle_layouts_table = None
        self._pjt_bundle_layers_table = None
        self._pjt_circuits_table = None
        self._pjt_points_2d_table = None
        self._pjt_points_3d_table = None
        self._pjt_housings_table = None
        self._pjt_splices_table = None
        self._pjt_transitions_table = None
        self._pjt_wires_table = None
        self._pjt_wire_2d_layouts_table = None
        self._pjt_wire_3d_layouts_table = None
        self._pjt_cavities_table = None
        self._pjt_terminals_table = None
        self._pjt_seals_table = None
        self._pjt_covers_table = None
        self._pjt_boots_table = None
        self._pjt_cpa_locks_table = None
        self._pjt_tpa_locks_table = None
        self._pjt_wire_markers_table = None
        self._pjt_wire_service_loops_table = None

        self._points_2d = []
        self._points_3d = []

        self._current_count = 0

    def load(self, project_id):
        self.mainframe.unload()

        self._current_count = 0

        self._pjt_bundles_table = PJTBundlesTable(self, project_id)
        self._pjt_bundle_layouts_table = PJTBundleLayoutsTable(self, project_id)
        self._pjt_bundle_layers_table = PJTBundleLayersTable(self, project_id)
        self._pjt_circuits_table = PJTCircuitsTable(self, project_id)
        self._pjt_points_2d_table = PJTPoints2DTable(self, project_id)
        self._pjt_points_3d_table = PJTPoints3DTable(self, project_id)
        self._pjt_housings_table = PJTHousingsTable(self, project_id)
        self._pjt_splices_table = PJTSplicesTable(self, project_id)
        self._pjt_transitions_table = PJTTransitionsTable(self, project_id)
        self._pjt_wires_table = PJTWiresTable(self, project_id)
        self._pjt_wire_2d_layouts_table = PJTWire2DLayoutsTable(self, project_id)
        self._pjt_wire_3d_layouts_table = PJTWire3DLayoutsTable(self, project_id)
        self._pjt_cavities_table = PJTCavitiesTable(self, project_id)
        self._pjt_terminals_table = PJTTerminalsTable(self, project_id)
        self._pjt_seals_table = PJTSealsTable(self, project_id)
        self._pjt_covers_table = PJTCoversTable(self, project_id)
        self._pjt_boots_table = PJTBootsTable(self, project_id)
        self._pjt_cpa_locks_table = PJTCPALocksTable(self, project_id)
        self._pjt_tpa_locks_table = PJTTPALocksTable(self, project_id)
        self._pjt_wire_markers_table = PJTWireMarkersTable(self, project_id)
        self._pjt_wire_service_loops_table = PJTWireServiceLoopsTable(self, project_id)

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

        self._points_2d = [point.point for point in self._pjt_points_2d_table]
        self._points_3d = [point.point for point in self._pjt_points_3d_table]

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
    def pjt_bundle_layers_table(self) -> PJTBundleLayersTable:
        return self._pjt_bundle_layers_table

    @property
    def pjt_circuits_table(self) -> PJTCircuitsTable:
        return self._pjt_circuits_table

    @property
    def pjt_points_2d_table(self) -> PJTPoints2DTable:
        return self._pjt_points_2d_table

    @property
    def pjt_points_3d_table(self) -> PJTPoints3DTable:
        return self._pjt_points_3d_table

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

    @property
    def pjt_seals_table(self) -> PJTSealsTable:
        return self._pjt_seals_table

    @property
    def pjt_covers_table(self) -> PJTCoversTable:
        return self._pjt_covers_table

    @property
    def pjt_boots_table(self) -> PJTBootsTable:
        return self._pjt_boots_table

    @property
    def pjt_cpa_locks_table(self) -> PJTCPALocksTable:
        return self._pjt_cpa_locks_table

    @property
    def pjt_tpa_locks_table(self) -> PJTTPALocksTable:
        return self._pjt_tpa_locks_table

    @property
    def pjt_wire_markers_table(self) -> PJTWireMarkersTable:
        return self._pjt_wire_markers_table

    @property
    def pjt_wire_service_loops_table(self) -> PJTWireServiceLoopsTable:
        return self._pjt_wire_service_loops_table
