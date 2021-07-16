# 20210712 build

# TODO
# 剪切板助手/切换二维码和设置历史剪切板
# 退出最小化到状态栏/全局Esc和鼠标移动到左上角
# 图标/二维码切换

# FIXME
# 关闭和重启时位置可能漂移

# TODO FUTURE
# 分段和翻页
# 定时切换回到图标/鼠标放置除外
# 可配置参数文件
# 支持文件

import os
from threading import Thread

import wx
import pynput
import qrcode

__ver__ = 'Ver 0.01'

CONFIG = 'config.ini'


def qrmake(qrstr):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(qrstr)
    qr.best_fit()
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    return img


class ClipboardHistroy:
    def __init__(self, parent):
        self.data = []

    def Latest(self):
        do = wx.TextDataObject()
        if wx.TheClipboard.Open():
            ret = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if ret:
                text = do.GetText()
                if text not in self.data[:1]: # maybe data is empty
                    if text in self.data[1:]:
                        self.data.remove(text)
                    self.data.insert(0, text)
                    return text


class Monitor:
    def __init__(self, func):
        self.func = func
        t1 = Thread(target=self.MouseListener)
        t2 = Thread(target=self.KeyboardListener)
        t1.start()
        t2.start()

    def refresh(self, *args):
        self.func()

    def ignore(self, *args):
        return

    def MouseListener(self):
        with pynput.mouse.Listener(on_move=self.ignore, on_click=self.refresh, on_scroll=self.ignore) as self.ml:
            self.ml.join()

    def KeyboardListener(self):
        with pynput.keyboard.Listener(on_press=self.ignore, on_release=self.refresh) as self.kl:
            self.kl.join()

    def Close(self):
        pynput.keyboard.Listener.stop(self.kl)
        pynput.mouse.Listener.stop(self.ml)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.bmp = wx.StaticBitmap(self)
        self.history = ClipboardHistroy(self)
        self.monitor = Monitor(self.SetQrCode)
        self.SetQrCode()

    def SetQrCode(self):
        text = self.history.Latest()
        if text:
            text = text[:1000] # TODO 增加翻页
            qr = qrmake(text)
            img_pil = qr.convert('RGB')
            img_wx = wx.Image(img_pil.size, img_pil.tobytes())

            w0, h0 = self.bmp.GetSize()
            self.bmp.SetBitmap(wx.Bitmap(img_wx))

            w, h = self.bmp.GetSize()
            x, y = self.parent.GetPosition()
            self.parent.SetSize((w+2, h+2)) # TODO 自动合适大小
            self.parent.SetPosition((int(x+(w0-w)/2), int(y+(h0-h)/2))) # TODO 自动合适大小

            tt = wx.ToolTip('Length: %d\n%s'%(len(text), text))
            self.bmp.SetToolTip(tt)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'QR Assistant - %s'%__ver__,style = wx.STAY_ON_TOP)

        self.delta = (0,0)

        self.panel = MyPanel(self)
        self.LoadLocation()
        self.Binding(self.panel.bmp)
        self.Show()

    def OnExit(self, evt):
        with open(CONFIG, 'w') as f:
            f.write(str(self.GetPosition()))
        self.panel.monitor.Close()
        self.Close()

    def LoadLocation(self):
        if os.path.exists(CONFIG):
            with open(CONFIG) as f:
                xy = eval(f.read())
                self.SetPosition(xy)
        else:
            self.Center()

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        x, y = self.ClientToScreen(evt.GetPosition())
        originx, originy = self.GetPosition()
        dx = x - originx
        dy = y - originy
        self.delta = ((dx, dy))

    def OnLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            x, y = self.ClientToScreen(evt.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)

    def Binding(self, widget):
        widget.Bind(wx.EVT_RIGHT_UP,  self.OnExit)
        widget.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,     self.OnLeftUp)
        self.Bind(wx.EVT_MOTION,      self.OnMouseMove)


app = wx.App()
frm = MyFrame()
app.MainLoop()
