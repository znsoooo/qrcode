# 20210712 build

# Ver 0.01
# 实时获取剪切板文本转换为二维码显示

# Ver 0.02
# 左键拖拽移动位置/关闭记忆位置
# 剪切板助手/右键设置历史剪切板
# 全局Esc/中键点击/定时无操作最小化到托盘
# 左键单击托盘切换显示状态/右键单击退出
# 长文本分段/全局热键左右翻页

# TODO FUTURE
# 参数配置文件
# 支持文件
# 鼠标放置不消失

import os
from threading import Timer
from threading import Thread

import wx
import pynput
import qrcode
from wx.adv import TaskBarIcon

__title__ = 'QR Desktop'
__ver__ = 'Ver 0.02'

TIME_OUT = 6
PART_LEN = 300
IMG_ICON = 'icon.png'

CONFIG = 'config.ini'


def QrMake(qrstr):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(qrstr)
    qr.best_fit()
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    return img


def Split(text, length):
    s = bytearray()
    for c in text:
        s.extend(c.encode())
        if len(s) >= length:
            yield s.decode()
            s.clear()
    if s:
        yield s.decode()


class ClipboardHistroy:
    def __init__(self):
        self.data = []

    def set(self, id):
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

    def get(self):
        try:
            do = wx.TextDataObject()
            if wx.TheClipboard.Open():
                ret = wx.TheClipboard.GetData(do)
                wx.TheClipboard.Close()
                if ret:
                    return do.GetText()
        except Exception as e:
            print('GetError:', e)

    def latest(self):
        text = self.get()
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
    def __init__(self, func):
        self.func = func
        Thread(target=self.mouser).start()
        Thread(target=self.keyboarder).start()

    def hook(self, *typ_names):
        for name in typ_names:
            yield (lambda typ: (lambda *args: self.func(typ, *args)))(name)

    def mouser(self):
        with pynput.mouse.Listener(*self.hook('move', 'click', 'scroll')) as self.ml:
            self.ml.join()

    def keyboarder(self):
        with pynput.keyboard.Listener(*self.hook('press', 'release')) as self.kl:
            self.kl.join()

    def close(self):
        pynput.keyboard.Listener.stop(self.kl)
        pynput.mouse.Listener.stop(self.ml)


class Mover:
    def __init__(self, parent, widget):
        self.p = parent
        self.dxy = (0, 0)
        widget.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        parent.Bind(wx.EVT_LEFT_UP,   self.OnLeftUp)
        parent.Bind(wx.EVT_MOTION,    self.OnMouseMove)

    def OnLeftDown(self, evt):
        self.p.CaptureMouse()
        x, y = self.p.ClientToScreen(evt.GetPosition())
        x0, y0 = self.p.GetPosition()
        dx = x - x0
        dy = y - y0
        self.dxy = (dx, dy)

    def OnLeftUp(self, evt):
        if self.p.HasCapture():
            self.p.ReleaseMouse()

    def OnMouseMove(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            x, y = self.p.ClientToScreen(evt.GetPosition())
            fp = (x - self.dxy[0], y - self.dxy[1])
            self.p.Move(fp)


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, parent):
        TaskBarIcon.__init__(self, wx.adv.TBI_DOCK) # wx.adv.TBI_CUSTOM_STATUSITEM

        icon = wx.Icon(wx.Image(IMG_ICON).ConvertToBitmap())
        self.SetIcon(icon, __title__)
        parent.SetIcon(icon)

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, parent.Swap)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, parent.OnClose)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '%s - %s'%(__title__, __ver__), style=wx.STAY_ON_TOP) # | wx.BORDER_NONE

        self.icon = MyTaskBarIcon(self)
        self.bmp  = wx.StaticBitmap(self)

        self.history = ClipboardHistroy()
        self.timer   = MyTimer(self.Hide)
        self.monitor = Monitor(self.MonitorHook)
        Mover(self, self.bmp)

        self.LoadLocation() # before SetQrCode
        self.SetQrCode(init=__title__) # clipboard maybe unavailable first time.
        self.timer.wait(TIME_OUT) # timer for run at first time.

        self.Binding(self.bmp)

        self.Show()

    def Binding(self, widget):
        widget.Bind(wx.EVT_MIDDLE_UP, self.Hide)
        widget.Bind(wx.EVT_RIGHT_UP,  self.OnPopup)
        self.Bind(wx.EVT_CLOSE,       self.OnClose) # maybe close by Alt+F4

    def MonitorHook(self, typ, *args):
        self.timer.wait(TIME_OUT)
        if typ in ['release', 'click']:
            self.SetQrCode()
            if hasattr(args[0], 'name'): # global hotkey
                self.HotKey(args[0].name)

    def HotKey(self, key):
        if key == 'esc':
            self.Swap(-1)
        elif key == 'left':
            self.Flip(-1)
        elif key == 'right':
            self.Flip(1)

    def SetQrCode(self, text=None, init=None):
        text = text or self.history.latest() or init
        if text:
            self.texts = list(Split(text, PART_LEN))
            self.page = 0
            self.SetText()
            self.Show()

    def SetText(self):
        text = self.texts[self.page]
        qr = QrMake(text)
        img_pil = qr.convert('RGB')
        img_wx = wx.Image(img_pil.size, img_pil.tobytes())

        if len(self.texts) == 1:
            header = 'Length: %d\n' % len(text)
        else:
            header = 'Length: %d (%d/%d)\n' % (len(text), self.page+1, len(self.texts))

        self.bmp.SetBitmap(wx.Bitmap(img_wx))
        self.bmp.SetToolTip(header + text)
        self.SetSizeCenter(self.bmp.GetSize())

    def Flip(self, n):
        page = self.page + n
        if 0 <= page < len(self.texts):
            self.page = page
            self.SetText()

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
        text = self.history.set(id)
        self.SetQrCode(text=text)

    def Show(self, show=True):
        bmp = self.bmp
        tip = bmp.GetToolTipText()
        bmp.SetToolTip('') # prevent remain shadow after hide frame.
        super().Show(show)
        bmp.SetToolTip(tip) # restore tip text.

    def Hide(self, evt=0):
        self.Show(False)

    def Swap(self, evt):
        self.Show(not self.IsShown())

    def LoadLocation(self):
        self.SetSize((10, 10)) # make sure save/load at the same place.
        if os.path.exists(CONFIG):
            with open(CONFIG) as f:
                xy = eval(f.read())
                self.SetPosition(xy)
        else:
            self.Center()

    def SetSizeCenter(self, size):
        x, y = self.GetPosition()
        w1, h1 = self.GetSize()
        w2, h2 = size
        self.SetPosition((x - 1 + (w1 - w2) // 2, y - 1 + (h1 - h2) // 2))
        self.SetSize((w2 + 2, h2 + 2))
        # self.SetSize(size) # while no border

    def OnClose(self, evt):
        self.SetSizeCenter((10, 10)) # make sure save/load at the same place.
        xy = str(self.GetPosition()) # prevent generate 0 byte file.
        with open(CONFIG, 'w') as f:
            f.write(xy)
        self.monitor.close()
        self.icon.Destroy() # only `RemoveIcon` will still run in mainloop.
        self.Destroy()


app = wx.App()
locale = wx.Locale(wx.LANGUAGE_ENGLISH)
frm = MyFrame()
app.MainLoop()
