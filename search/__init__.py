from typing import TYPE_CHECKING, Union

import wx

from wx.lib import scrolledpanel


if TYPE_CHECKING:
    from .. import global_db as _global_db
    from .. import project_db as _project_db


class ItemsPanel(scrolledpanel.ScrolledPanel):
    def __init__(self, parent, choices):
        scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        v_sizer = wx.BoxSizer(wx.VERTICAL)

        ctrls = []

        def _HSizer(label, ctrl):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            st = wx.StaticText(self, wx.ID_ANY, label=label)

            sizer.Add(st, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
            sizer.Add(ctrl, 0, wx.ALL, 5)

        for choice in choices:
            checkbox = wx.CheckBox(self, wx.ID_ANY)
            v_sizer.Add(_HSizer(choice, checkbox), 0)
            ctrls.append([choice, checkbox])

        self._ctrls = ctrls

        self.SetupScrolling(self, scroll_x=False)
        self.SetSizer(v_sizer)

    def Reset(self):
        for _, ctrl in self._ctrls:
            ctrl.SetValue(False)


    def GetValues(self):
        res = []

        for name, ctrl in self._ctrls:
            if ctrl.GetValue():
                res.append(name)

        return res


class SearchPanelField(wx.Panel):

    def __init__(self, parent, label, field_name, choices):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        self.field_name = field_name
        v_sizer = wx.BoxSizer(wx.VERTICAL)

        st = wx.StaticText(self, wx.ID_ANY, label=label)
        v_sizer.Add(st, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.items_panel = ItemsPanel(self, choices)
        v_sizer.Add(self.items_panel, 1, wx.ALL | wx.EXPAND, 5)

        self.reset_button = wx.Button(wx.ID_RESET, size=(40, -1))

        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)

        v_sizer.Add(self.reset_button, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        self.SetSizer(v_sizer)

    def on_reset(self, evt):
        evt.Skip()
        self.items_panel.Reset()

    def GetSQLCommand(self):
        res = []
        values = self.items_panel.GetValues()

        for value in values:
            if value.isdigit():
                value = int(value)

            res.append(f'{self.field_name} = {repr(value}}')

        res = ' OR '.join(res)
        return f'({res})'

class SearchPanel(scrolledpanel.ScrolledPanel):

    def __init__(self, parent, db_table: Union["_global_db.TableBase", "_project_db.PJTTableBase"]):
        scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        self._db_table = db_table

        self.SetupScrolling(self, scroll_y=False)

        db_table.field_mapping


