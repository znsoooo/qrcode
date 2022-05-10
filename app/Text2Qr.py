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
        self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Center()
        self.Show()
        self.text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.text.Bind(wx.EVT_TEXT, self.OnText)

    def OnKeyDown(self, evt):
        if evt.ControlDown() and evt.AltDown() and evt.GetKeyCode() == ord('Q'):
            try:
                qr = qrcode.make(self.text.GetValue() or __help__, box_size=2, border=2)
                QrFrame(qr)
            except qrcode.exceptions.DataOverflowError:
                wx.MessageBox('DataOverflowError')
        evt.Skip()

    def OnText(self, evt):
        length = len(self.text.GetValue().encode())
        title = 'Text - %d' % length if length else 'Text'
        self.SetTitle(title)


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame()
    app.MainLoop()
