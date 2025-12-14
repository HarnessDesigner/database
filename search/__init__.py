from typing import TYPE_CHECKING, Union

import wx

from wx.lib import scrolledpanel, newevent


if TYPE_CHECKING:
    from .. import global_db as _global_db
    from .. import project_db as _project_db


SearchChangedEvent, EVT_SEARCH_CHANGED_EVENT = newevent.NewEvent()
SearchChangedCommandEvent, EVT_SEARCH_CHANGED_COMMAND_EVENT = newevent.NewCommandEvent()


class Item(wx.BoxSizer):

    def __init__(self, st, ctrl):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        self.st = st
        self.ctrl = ctrl
        self.Add(st, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.Add(ctrl, 0, wx.ALL, 5)

    def GetValue(self):
        return self.ctrl.GetValue()

    def GetName(self):
        return self.st.GetLabel()


class ItemsPanel(scrolledpanel.ScrolledPanel):
    def __init__(self, parent, choices):
        scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        v_sizer = wx.BoxSizer(wx.VERTICAL)

        self.items = []

        def _HSizer(label, ctrl):
            st = wx.StaticText(self, wx.ID_ANY, label=label)
            sizer = Item(st, ctrl)
            self.items.append(sizer)
            return sizer

        for choice in choices:
            checkbox = wx.CheckBox(self, wx.ID_ANY)
            v_sizer.Add(_HSizer(choice, checkbox), 0)

        self.SetupScrolling(self, scroll_x=False)
        self.SetSizer(v_sizer)

    def Reset(self):
        for item in self.items:
            item.ctrl.SetValue(False)

    def GetValues(self):
        res = []

        for item in self.items:
            if item.GetValue():
                res.append(item)

        return res


class SearchPanelField(wx.Panel):

    def __init__(self, parent, label, field_name, field_type, choices):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN)

        self.field_name = field_name
        self.field_type = field_type
        self.choices = choices[:]
        v_sizer = wx.BoxSizer(wx.VERTICAL)

        st = wx.StaticText(self, wx.ID_ANY, label=label)
        v_sizer.Add(st, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        if field_type == 'id':
            choices = [choice[1] for choice in choices]

        self.items_panel = ItemsPanel(self, sorted(choices))
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
        items = self.items_panel.GetValues()

        for item in items:
            if self.field_type == 'id':
                for value, choice in self.choices:
                    if choice == item.GetLabel():
                        break
                else:
                    raise RuntimeError('sanity check')
            elif self.field_type in ('str', 'float'):
                value = f'"{item.GetLabel()}"'
            else:
                value = item.GetLabel()

            res.append(f'{self.field_name} = {value}')

        res = ' OR '.join(res)
        return f'({res})'


class SearchPanel(scrolledpanel.ScrolledPanel):

    def __init__(self, parent, db_table: Union["_global_db.TableBase", "_project_db.PJTTableBase"]):
        scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        self._db_table = db_table

        self.SetupScrolling(self, scroll_y=False)

        self.search_items = db_table.search_items

        self.fields = []
        for label, data in self.search_items.items():
            field = SearchPanelField(self, label, data['field'], data['type'], data['values'])
            self.fields.append(field)

            field.Bind(wx.EVT_CHECKBOX, self.on_update)
            field.Bind(wx.EVT_BUTTON, self.on_update)

    def on_update(self, evt):
        evt.Skip()

        cmd = []
        for field in self.fields:
            params = field.GetSQLCommand()
            if params:
                cmd.append(params)

        if cmd:
            cmd = ' AND '.join(cmd)
            cmd = f'SELECT id from {self._db_table.__table_name__} WHERE {cmd};'
        else:
            cmd = f'SELECT id from {self._db_table.__table_name__};'

        # Create the event
        evt = SearchChangedEvent(command=cmd)
        # Post the event
        wx.PostEvent(self, evt)
