# 20210712 build

# Ver 0.02
# 获取剪切板保护
# 剪切板助手/切换历史二维码/设置历史剪切板
# 全局Esc/中键点击/定时器最小化到托盘

# TODO
# 鼠标放置除外
# 分段和翻页

# FIXME
# 关闭和重启时位置可能漂移

# TODO FUTURE
# 可配置参数文件
# 支持文件

import os
from threading import Timer
from threading import Thread

import wx
import pynput
import qrcode
from wx.adv import TaskBarIcon

__title__ = 'QR Desktop'
__ver__ = 'Ver 0.02'

TIME_OUT = 5

CONFIG = 'config.ini'


def QrMake(qrstr):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(qrstr)
    qr.best_fit()
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    return img


class ClipboardHistroy:
    def __init__(self):
        self.data = []

    def Set(self, id):
        text = self.data.pop(id)
        self.data.insert(0, text)
        try:
            do = wx.TextDataObject()
            do.SetText(text)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(do)
                wx.TheClipboard.Close()
        except Exception as e:
            print('SetError:', e)
        return text

    def Get(self):
        try:
            do = wx.TextDataObject()
            if wx.TheClipboard.Open():
                ret = wx.TheClipboard.GetData(do)
                wx.TheClipboard.Close()
                if ret:
                    return do.GetText()
        except Exception as e:
            print('GetError:', e)

    def Latest(self):
        text = self.Get()
        if text and text not in self.data[:1]:  # maybe data is empty
            if text in self.data[1:]:
                self.data.remove(text)
            self.data.insert(0, text)
            return text


class MyTimer: # Good!
    def __init__(self, func):
        self.func = func
        self.count = 0

    def wait(self, seconds):
        self.count += 1
        Timer(seconds, self.timeout).start()

    def timeout(self):
        self.count -= 1
        if self.count == 0:
            self.func()


class Monitor:
    def __init__(self, func, func_keep, func_hide):
        self.func = func
        self.func_keep = func_keep
        self.func_hide = func_hide
        Thread(target=self.MouseListener).start()
        Thread(target=self.KeyboardListener).start()

    def refresh(self, *args):
        self.func()
        if hasattr(args[0], 'name'):
            if args[0].name == 'esc':
                self.func_hide(-1)

    def keep(self, *args):
        self.func_keep(TIME_OUT)

    def MouseListener(self):
        with pynput.mouse.Listener(on_move=self.keep, on_click=self.refresh, on_scroll=self.keep) as self.ml:
            self.ml.join()

    def KeyboardListener(self):
        with pynput.keyboard.Listener(on_press=self.keep, on_release=self.refresh) as self.kl:
            self.kl.join()

    def Close(self):
        pynput.keyboard.Listener.stop(self.kl)
        pynput.mouse.Listener.stop(self.ml)


class DemoTaskBarIcon(TaskBarIcon):
    def __init__(self, parent):
        TaskBarIcon.__init__(self, wx.adv.TBI_DOCK) # wx.adv.TBI_CUSTOM_STATUSITEM
        self.parent = parent

        icon = wx.Icon(wx.Image('wxpdemo.ico').ConvertToBitmap())
        self.SetIcon(icon, __title__)

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, parent.ShowX)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.Close)

    def Close(self, evt):
        self.parent.OnClose(-1)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self.history = ClipboardHistroy()
        self.timer   = MyTimer(self.parent.Hide)
        self.monitor = Monitor(self.SetQrCode, self.timer.wait, self.parent.ShowX)

        self.bmp = wx.StaticBitmap(self)
        self.bmp.Bind(wx.EVT_RIGHT_UP, self.OnPopup)

        self.SetQrCode(init=__title__) # clipboard maybe unavailable at first time.

    def OnPopup(self, e): # TODO clear
        menu = wx.Menu()
        for i, text in enumerate(self.history.data[1:]):
            if i:
                menu.AppendSeparator()
            menu.Append(i+1, 'Len %3d: %s'%(len(text), text.replace('\n', '\\n')))
        menu.Bind(wx.EVT_MENU, self.OnMenu)
        self.PopupMenu(menu)

    def OnMenu(self, e):
        id = e.GetId()
        text = self.history.Set(id)
        self.SetQrCode(text=text)

    def SetQrCode(self, text=None, init=None):
        self.timer.wait(TIME_OUT)
        text = text or self.history.Latest() or init
        if text:
            text = text[:1000] # TODO 增加翻页
            qr = QrMake(text)
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

            self.parent.Show(True)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '%s - %s'%(__title__, __ver__), style=wx.STAY_ON_TOP)

        self.delta = (0, 0)

        self.panel = MyPanel(self)
        self.icon = DemoTaskBarIcon(self)
        self.LoadLocation()

        self.Binding(self.panel.bmp)
        self.Show()

    def LoadLocation(self):
        if os.path.exists(CONFIG):
            with open(CONFIG) as f:
                xy = eval(f.read())
                self.SetPosition(xy)
        else:
            self.Center()

    def Binding(self, widget):
        widget.Bind(wx.EVT_MIDDLE_UP, lambda e: self.Hide())
        widget.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,     self.OnLeftUp)
        self.Bind(wx.EVT_MOTION,      self.OnMouseMove)

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

    def OnClose(self, evt):
        with open(CONFIG, 'w') as f:
            f.write(str(self.GetPosition()))
        self.panel.monitor.Close()
        self.icon.RemoveIcon()
        self.Close()

    def ShowX(self, evt):
        self.Show(not self.IsShown())


app = wx.App()
frm = MyFrame()
app.MainLoop()
