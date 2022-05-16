"""
Hotkey: Ctrl-Alt-Q
"""

import wx
import qrcode

__help__  = 'https://github.com/znsoooo/qrcode'


class QrFrame(wx.Dialog):
    def __init__(self, qr):
        wx.Dialog.__init__(self, None, -1, 'QR')

        img_pil = qr.get_image().convert('RGB')
        img_wx = wx.Image(img_pil.size, img_pil.tobytes())
        bmp = wx.StaticBitmap(self, -1, wx.Bitmap(img_wx))

        self.Fit()
        self.Center()
        self.ShowModal()
        self.Destroy()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Text')
        self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_NOHIDESEL)
        self.text.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.text.Bind(wx.EVT_TEXT, self.OnText)
        self.text.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, self.OnText)
        self.Center()
        self.Show()

    def OnFocus(self, evt):
        do = wx.TextDataObject()
        if wx.TheClipboard.Open():
            if wx.TheClipboard.GetData(do):
                self.text.SetValue(do.GetText())
            wx.TheClipboard.Close()
        evt.Skip()

    def OnKeyDown(self, evt):
        if evt.ControlDown() and evt.AltDown() and evt.GetKeyCode() == ord('Q'):
            try:
                s = self.text.GetStringSelection() or self.text.GetValue() or __help__
                qr = qrcode.make(s, box_size=2, border=2)
                QrFrame(qr)
            except qrcode.exceptions.DataOverflowError:
                wx.MessageBox('DataOverflowError')
        evt.Skip()

    def OnText(self, evt):
        len1 = len(self.text.GetValue().encode())
        len2 = len(self.text.GetStringSelection().encode())
        if len2:
            title = 'Text - %d/%d' % (len2, len1)
        elif len1:
            title = 'Text - %d' % len1
        else:
            title = 'Text'
        self.SetTitle(title)
        evt.Skip()


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame()
    app.MainLoop()
