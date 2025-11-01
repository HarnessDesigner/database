from typing import Union as _Union, Iterable as _Iterable

import wx


from . import EntryBase, TableBase

from .mixins import (PartNumberMixin, ManufacturerMixin, DescriptionMixin, ColorMixin,
                     FamilyMixin, SeriesMixin, ResourceMixin, WeightMixin)


class BootsTable(TableBase):
    __table_name__ = 'boots'

    def __iter__(self) -> _Iterable["Boot"]:
        for db_id in TableBase.__iter__(self):
            yield Boot(self, db_id)

    def __getitem__(self, db_id) -> "Boot":
        if db_id in self:
            return Boot(self, db_id)

        raise IndexError(str(db_id))

    def get(self, part_number) -> _Union["Boot", None]:
        self._cur.execute(f'SELECT id from {self.__table_name__} WHERE part_number = "{part_number}";')
        for line in self._cur.fetchall():
            db_id = line[0]
            return Boot(self, db_id)

    def insert(self, part_number: str, mfg_id: int, description: str, family_id: int,
               series_id: int, image_id: int, datasheet_id: int, cad_id: int, color_id: int, weight: float) -> "Boot":

        db_id = TableBase.insert(self, part_number=part_number, mfg_id=mfg_id, description=description,
                                 family_id=family_id, series_id=series_id, image_id=image_id,
                                 datasheet_id=datasheet_id, cad_id=cad_id, color_id=color_id, weight=weight)

        return Boot(self, db_id)

    def get_control(self, parent):
        pass


from ...widgets import auto_complete as _auto_complete  # NOQA
from ...dialogs import remove_db_record as _remove_db_record  # NOQA


class BootChoiceControl(wx.StaticBox):

    def __init__(self, parent, part_table: BootsTable):

        self.part_table = part_table
        mfg_id_mapping = self.mfg_id_mapping = {}
        mfg_name_mapping = self.mfg_name_mapping = {}
        pn_name_mapping = self.pn_name_mapping = {}

        mfg_mapping = self.mfg_mapping = {}

        items = part_table.select('id', 'part_number', 'mfg_id')
        for pn_id, pn, mfg_id in items():
            if mfg_id in mfg_id_mapping:
                mfg_name = mfg_name_mapping[mfg_id]
            else:
                mfg_name = part_table.db.manufacturers_table.select('name', id=mfg_id)
                if mfg_name:
                    mfg_name = mfg_name[0][0]
                else:
                    continue

                mfg_id_mapping[mfg_id] = mfg_name
                mfg_name_mapping[mfg_name] = mfg_id

            if mfg_name not in mfg_mapping:
                mfg_mapping[mfg_name] = []

            mfg_mapping[mfg_name].append(pn)

            pn_name_mapping[pn] = pn_id

        mfg_choices = sorted(list(mfg_mapping.keys()))

        wx.StaticBox.__init__(self, parent, wx.ID_ANY, "Boot")

        v_sizer = wx.BoxSizer(wx.VERTICAL)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mfg_label = wx.StaticText(self, wx.ID_ANY, label='Manufacturer:')
        self.mfg_ctrl = _auto_complete.AutoComplete(self, wx.ID_ANY, autocomplete_choices=mfg_choices)
        self.mfg_add_btn = wx.Button(self, wx.ID_ANY, label='Add', size=(30, -1))
        self.mfg_remove_btn = wx.Button(self, wx.ID_ANY, label='Remove', size=(30, -1))

        h_sizer.Add(mfg_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        h_sizer.Add(self.mfg_ctrl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        h_sizer.Add(self.mfg_add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 25)
        h_sizer.Add(self.mfg_remove_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)

        v_sizer.Add(h_sizer, 0, wx.EXPAND | wx.ALL, 10)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pn_label = wx.StaticText(self, wx.ID_ANY, label='Part Number:')
        self.pn_ctrl = _auto_complete.AutoComplete(self, wx.ID_ANY, autocomplete_choices=[])
        self.pn_add_btn = wx.Button(self, wx.ID_ANY, label='Add', size=(30, -1))
        self.pn_remove_btn = wx.Button(self, wx.ID_ANY, label='Remove', size=(30, -1))

        h_sizer.Add(pn_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        h_sizer.Add(self.pn_ctrl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        h_sizer.Add(self.pn_add_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 25)
        h_sizer.Add(self.pn_remove_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)

        v_sizer.Add(h_sizer, 0, wx.EXPAND | wx.ALL, 5)

        v_sizer.Add(h_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.SetSizer(v_sizer)

    def on_mfg(self, evt):
        def _do():
            mfg_name = self.mfg_ctrl.GetValue()
            if mfg_name in self.mfg_name_mapping:
                mfg_id = self.mfg_name_mapping[mfg_name]

                self.mfg_remove_btn.Enable(mfg_id != 0)
                self.mfg_add_btn.Enable(False)
                self.pn_ctrl.SetAutoCompleteChoices(sorted(self.mfg_mapping[mfg_name]))
                self.pn_ctrl.SetValue('')
                self.pn_remove_btn.Enable(False)
                self.pn_add_btn.Enable(False)
                self.pn_ctrl.Enable(True)
            else:
                self.mfg_remove_btn.Enable(False)
                self.mfg_add_btn.Enable(mfg_name != '')
                self.pn_ctrl.Enable(False)

        wx.CallAfter(_do)
        evt.Skip()

    def on_mfg_add(self, evt):
        # TODO: add new manufacturer to database (opens a dialog to add a new manufacturer)

        evt.Skip()

    def on_mfg_remove(self, evt):
        dlg = _remove_db_record.RemoveDBRecordDialog(self.GetMainFrame(), 'Manufacturer', self.mfg_ctrl.GetValue())
        res = dlg.ShowModal()
        if res == wx.ID_YES:
            # TODO: remove manufacturer from database and set all records that use that manufacturer to use mfg_id 0
            pass

        dlg.Destroy()

        evt.Skip()

    def on_pn(self, evt):
        def _do():
            mfg_name = self.mfg_ctrl.GetValue()
            pn = self.pn_ctrl.GetValue()
            if pn in self.mfg_mapping[mfg_name]:
                self.pn_remove_btn.Enable(True)
                self.pn_add_btn.SetLabel('Update')
                self.pn_add_btn.Enable(True)
            elif pn in self.pn_name_mapping:
                self.pn_remove_btn.Enable(False)
                self.pn_add_btn.SetLabel('Update')
                self.pn_add_btn.Enable(True)
            else:
                self.pn_add_btn.SetLabel('Add')
                self.pn_add_btn.Enable(pn != '')
                self.pn_remove_btn.Enable(False)

        wx.CallAfter(_do)
        evt.Skip()

    def on_pn_add(self, evt):
        mfg = self.mfg_ctrl.GetValue()
        pn = self.pn_ctrl.GetValue()

        if self.pn_add_btn.GetLabel() == 'Add':
            # TODO: add new part to database (opens a dialog to add a new boot)
            pass

        elif self.pn_add_btn.GetLabel() == 'Update':
            if pn in self.mfg_mapping[mfg]:
                # TODO: Update project database
                pass
            else:
                # TODO: Change manufacturer of part to new manufacturer
                pass

        evt.Skip()

    def on_pn_remove(self, evt):
        evt.Skip()


class AddBootDialog(wx.Dialog):

    def __init__(self, parent, db_obj):

        self.db_obj = db_obj


class Boot(EntryBase, PartNumberMixin, ManufacturerMixin, DescriptionMixin, FamilyMixin,
           SeriesMixin, ResourceMixin, WeightMixin, ColorMixin):
    _table: BootsTable = None
