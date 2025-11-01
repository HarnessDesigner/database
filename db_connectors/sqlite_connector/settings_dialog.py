import wx


try:
    from . import Config as SQLConfig
    from ....config import Config as _Config
except ImportError:
    from __init__ import Config as SQLConfig

    class _Config:
        pass


class SQLOptionsDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, size=Config.size,
                           title='MySQL Options', pos=Config.pos,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOVE, self.on_move)
