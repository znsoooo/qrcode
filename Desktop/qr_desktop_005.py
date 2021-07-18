# 20210712 build

# Name:    QR Desktop
# Version: 0.0.5.0
# Date:    2021-07-18
# Author:  Lishixian
# Email:   11313213@qq.com
# Github:  github.com/znsoooo/qrcode/tree/master/Desktop

# Ver 0.01
# 实时获取剪切板文本转换为二维码显示

# Ver 0.02
# 左键拖拽移动位置/关闭记忆位置
# 剪切板助手/右键设置历史剪切板
# 全局Esc/中键点击/Alt+F4/定时无操作最小化到托盘
# 左键单击托盘切换显示状态/右键单击退出
# 长文本分段/全局热键左右翻页

# Ver 0.03
# 可配置参数文件
# 分段平均分布二维码大小
# 点击托盘切换常开/常关/自动显示3种状态/Tips提示
# 打包程序添加图标/版权信息/资源文件

# Ver 0.05
# 右键选择清空记录
# 鼠标放置不消失
# 拖拽添加文件
# 自动解码
# 自动连续播放

import os
import sys
import time
import zlib
import base64
import configparser
import subprocess as sub
from threading import Timer
from threading import Thread

import wx
import pynput
import qrcode
from wx.adv import TaskBarIcon

__title__ = 'QR Desktop'
__ver__ = 'Ver 0.05'


def ReadConfig(path):
    ini = configparser.ConfigParser()
    ini.read(path)
    s = __title__
    if not ini.has_section(s):
        ini.add_section(s)
        ini.set(s, 'length', '300')
        ini.set(s, 'timeout', '6')
        ini.set(s, 'position', 'None')
        ini.write(open(path, 'w'))
    return int(ini.get(s, 'length')), int(ini.get(s, 'timeout')), eval(ini.get(s, 'position'))


def ReadAutorun(path):
    ini = configparser.ConfigParser()
    ini.read(path)
    s, o = __title__, 'autorun'
    if ini.has_section(s) and ini.has_option(s, o):
        return ini.get(s, o)


def SaveConfig(path, option, value):
    ini = configparser.ConfigParser()
    ini.read(path)
    ini.set(__title__, option, str(value))
    ini.write(open(path, 'w'))


def QrMake(qrstr):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(qrstr)
    qr.best_fit()
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    return img


def OpenFile(file):
    with open(file, 'rb') as f:
        s = f.read()
    try:
        return False, s.decode()
    except:
        try:
            return False, s.decode('gbk')
        except:
            filename = os.path.basename(file)
            text = base64.b64encode(zlib.compress(s)).decode().replace('/', '_') # use '_' and '-' make wrap line cleaner.
            return True, filename + '|' + text # '|' will not in filename


def DecodeFile(data):
    # test: # 1/2:1,1/2:1,2/2:1, # (hello world!) 2/3:yVcozy_KSVE,1/3:hello.txt|eJzLSM3J,3/3:EAB6JBH4=,2/3:yVcozy_KSVE,
    # format check
    try:
        data = data.replace(' ', '').replace('\r', '').replace('\n', '')
        if not data.endswith(','):
            return
        data2 = []
        total = 0
        for line in data.split(',')[:-1]:
            header, text = line.split(':', 1)
            page, total = list(map(int, header.split('/')))
            data2.append((page, total, text))
    except:
        return

    # total value check
    for line in data2:
        if line[1] != total:
            return 'TotalValueError: %d != %d' % (line[1], total)
    data3 = {line[0]: line[2] for line in data2}

    # page value check
    data4 = []
    for i in range(total):
        if (i + 1) in data3:
            data4.append(data3[i + 1])
        else:
            return 'MissingPageError: %d' % (i + 1)

    # decode file
    try:
        text = ''.join(data4)
        file, content = text.split('|', 1)
        content2 = zlib.decompress(base64.b64decode(content.replace('_', '/')))
        root, ext = os.path.splitext(file)
        cnt = 1
        while os.path.exists(file):
            file = '%s_%d%s' % (root, cnt, ext)
            cnt += 1
        with open(file, 'wb') as f:
            f.write(content2)
        cmd = 'explorer /select, "%s"' % os.path.abspath(file)
        sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, stdin=sub.PIPE) # `os.popen` cant use in `pyinstaller -F -w` mode.
    except Exception as e:
        return 'DecodeError: %s' % e


def SplitAverage(text, length): # split average
    total = len(text.encode())
    page = - (- total // length)
    current = 0
    s = bytearray()
    p = 1
    for c in text:
        s.extend(c.encode())
        if current + len(s) >= (p * total) // page:
            current += len(s)
            yield s.decode()
            s.clear()
            p += 1
            if p > page:
                return


class ClipboardHistroy:
    def __init__(self):
        self.last = None
        self.data = []

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

    def set(self, text):
        try:
            do = wx.TextDataObject()
            do.SetText(text)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(do)
                wx.TheClipboard.Close()
        except Exception as e:
            print('SetError:', e)

    def find(self, id):
        text = self.data.pop(id)
        self.data.insert(0, text)
        self.set(text)
        self.last = self.get() # restore status prevent text change after set/get (when data read from file, '\r\n' change to '\n').
        return text

    def add(self, text):
        if text in self.data[1:]:
            self.data.remove(text)
        self.data.insert(0, text)

    def latest(self):
        text = self.get()
        if text and text != self.last:
            self.last = text
            self.add(text)
            return text


class MyLastTimer: # Good!
    def __init__(self, func):
        self.func = func
        self.th = Timer(0, int)

    def wait(self, seconds): # only last timer work.
        self.th.cancel()
        self.th = Timer(seconds, self.timeout)
        self.th.start()

    def timeout(self):
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

    def stop(self):
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


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, func):
        wx.FileDropTarget.__init__(self)
        self.func = func

    def OnDropFiles(self, x, y, filenames):
        self.func(filenames)
        return True


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, parent):
        TaskBarIcon.__init__(self, wx.adv.TBI_DOCK) # wx.adv.TBI_CUSTOM_STATUSITEM

        self.parent = parent
        self.icon = wx.Icon(wx.Image(IMG_ICON).ConvertToBitmap())
        self.SetMyIcon()
        parent.SetIcon(self.icon)

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, parent.Swap)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, parent.OnClose)

    def SetMyIcon(self):
        spec = '\nRight Click to Close' or '\nLeft Click to Switch, Right Click to Close.'
        self.SetIcon(self.icon, '%s (%s)'%(__title__, ['Off', 'On', 'Auto'][self.parent.always]) + spec)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '%s - %s'%(__title__, __ver__), style=wx.STAY_ON_TOP) # | wx.BORDER_NONE

        self.always = -1
        self.encode = False
        self.enter  = False

        self.icon = MyTaskBarIcon(self)
        self.bmp  = wx.StaticBitmap(self)

        self.history = ClipboardHistroy()
        self.timer   = MyLastTimer(self.Hide)
        self.monitor = Monitor(self.MonitorHook)
        Mover(self, self.bmp)
        self.bmp.SetDropTarget(MyFileDropTarget(self.OnOpenFile))

        self.LoadLocation() # before `SetQrCode`
        self.SetQrCode(init=__title__) # clipboard maybe unavailable first time.
        self.timer.wait(TIME_OUT) # timer for run at first time.

        self.Binding(self.bmp)

        self.Show()

    def Binding(self, widget):
        widget.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        widget.Bind(wx.EVT_LEAVE_WINDOW, self.OnEnter)
        widget.Bind(wx.EVT_MIDDLE_UP, self.Hide)
        widget.Bind(wx.EVT_RIGHT_UP,  self.OnPopup)
        self.Bind(wx.EVT_CLOSE,       self.Hide) # maybe call by `Alt+F4`

    def MonitorHook(self, typ, *args):
        self.timer.wait(TIME_OUT)
        if typ in ['release', 'click']:
            self.SetQrCode()
            if hasattr(args[0], 'name'): # global hotkey
                self.HotKey(args[0].name)

    def HotKey(self, key):
        if key == 'esc':
            self.Swap()
        elif key == 'left':
            self.Flip(-1)
        elif key == 'right':
            self.Flip(1)

    def SetQrCode(self, text=None, init=None, encode=False):
        text = text or self.history.latest() or init
        if text:
            self.encode = encode
            ret = DecodeFile(text) # format error or decode success will return `None`.
            text = ret or text
            self.texts = list(SplitAverage(text, PART_LEN))
            self.page = 0
            self.SetText()
            self.Show()

    def SetText(self):
        text = self.texts[self.page]
        if self.encode:
            text = '%d/%d:%s,\n' % (self.page+1, len(self.texts), text)
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
        while 0 <= page < len(self.texts): # avoid maximum recursion depth exceeded.
            self.page = page
            self.SetText()

            autorun = ReadAutorun(CONFIG) # read config here so it can be stopped.
            if autorun: # not `None` or empty string.
                self.always = 1
                time.sleep(float(autorun))
                page = self.page + n
            else:
                break

    def OnOpenFile(self, filenames):
        if os.path.isfile(filenames[0]):
            encode, text = OpenFile(filenames[0]) # TODO: how about folder and multi files?
            self.SetQrCode(text=text, encode=encode)
            self.history.add(text)

    def OnPopup(self, evt):
        menu = wx.Menu()
        menu.Append(0, 'Clear History')
        for i, text in enumerate(self.history.data[1:]):
            menu.AppendSeparator()
            menu.Append(i+1, 'Len %3d: %s'%(len(text), text.__repr__()))
        menu.Bind(wx.EVT_MENU, self.OnMenu)
        self.PopupMenu(menu)

    def OnMenu(self, evt):
        id = evt.GetId()
        if not id:
            self.history.data = self.history.data[:1] # clear data except current.
            return
        text = self.history.find(id)
        self.SetQrCode(text=text)

    def Show(self, show=True):
        if self.always == self.IsShown():
            return
        bmp = self.bmp
        tip = bmp.GetToolTipText()
        bmp.SetToolTip('') # prevent remain shadow after hide frame.
        super().Show(show)
        bmp.SetToolTip(tip) # restore tip text.

    def Hide(self, evt=None):
        if evt or not self.enter: # call by `Alt+F4`
            self.Show(False)

    def Swap(self, evt=None):
        if evt: # click icon
            if self.always == -1:
                self.always = self.IsShown()
            else:
                self.always = -1
                self.Show(not self.IsShown())
            self.icon.SetMyIcon()
        else: # press key
            self.Show(not self.IsShown())

    def LoadLocation(self):
        self.SetSize((10, 10)) # make sure save/load at the same place.
        if XY:
            self.SetPosition(XY)
        else:
            self.Center()

    def SetSizeCenter(self, size):
        x, y = self.GetPosition()
        w1, h1 = self.GetSize()
        w2, h2 = size
        self.SetPosition((x - 1 + (w1 - w2) // 2, y - 1 + (h1 - h2) // 2))
        self.SetSize((w2 + 2, h2 + 2))
        # self.SetSize(size) # while no border

    def OnEnter(self, evt):
        self.enter = evt.Entering()

    def OnClose(self, evt):
        self.SetSizeCenter((10, 10)) # make sure save/load at the same place.
        xy = str(self.GetPosition()) # prevent generate 0 byte file.
        SaveConfig(CONFIG, 'position', xy)
        self.timer.th.cancel()
        self.monitor.stop()
        self.icon.Destroy() # only `RemoveIcon` will still run in mainloop.
        self.Destroy()


if __name__ == '__main__':
    CONFIG = 'config.ini'
    PART_LEN, TIME_OUT, XY = ReadConfig(CONFIG)
    IMG_ICON = 'icon.ico'
    if hasattr(sys, '_MEIPASS'):
        IMG_ICON = os.path.join(sys._MEIPASS, IMG_ICON)

    app = wx.App()
    locale = wx.Locale(wx.LANGUAGE_ENGLISH) # sometimes PNG read error.
    frm = MyFrame()
    app.MainLoop()
