# -*- coding: utf-8 -*-

# usage: znsoooo.com/qrcode

# 20180510
# 支持双击打开通过py34运行
# 支持启动置入剪切板内容
# 当剪切板为空或非文本时的default

# 20190507
# 修改为类
# 基于Python3的编程
# 键盘快捷键(Esc/Left/Right)
# 文本变化后即时改变二维码
# 文本框界面宽度适配
# 其他优化

import sys
if sys.version_info < (3, 0):
    import Tkinter as tkinter
else:
    import tkinter as tkinter
from PIL import ImageTk
import qrcode

import win32con
import win32clipboard as w

qrlen = 1000
print('=============')

def qrmake(qrstr):
    qrlog = qrstr.replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')
    if len(qrlog) < 40:
        print(qrlog)
    else:
        print(qrlog[:10] + '...\n...\n...' + qrlog[-10:])
    qr = qrcode.QRCode(version=20, box_size=2, border=2)
    qr.add_data(qrstr)
    img = qr.make_image()
    bm = ImageTk.PhotoImage(image=img)
    return bm

def graph_split(graph, lenth):
    total = 0
    sentence = ''
    res = []
    for word in graph:
        if len(sentence.encode('utf-8')) < lenth:
            sentence = sentence + word
        else:
            res.append(sentence)
            sentence = word
    res.append(sentence)
    return res

def getClipboard():
    w.OpenClipboard()
    try:
        d = w.GetClipboardData(win32con.CF_TEXT).decode('gbk')
    except:
        d = ''
    w.CloseClipboard()
    return d

def setCenter(self):
    x0, y0 = self.winfo_x(), self.winfo_y()
    w0, h0 = self.winfo_reqwidth(), self.winfo_reqheight()
    self.update_idletasks()
    w1, h1 = self.winfo_reqwidth(), self.winfo_reqheight()
    self.geometry('+%d+%d'%(x0+(w0-w1)/2,y0+(h0-h1)/2))

bm=[]

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.ss = getClipboard()
        self.cnt = 0
        self.slices = graph_split(self.ss, qrlen)
        self.string = None

        x0 = - 100 + 0.2 * self.winfo_screenwidth() # 100: 补偿初始Tk界面为200x200
        y0 = - 100 + 0.7 * self.winfo_screenheight()
        self.geometry('+%d+%d'%(x0,y0))

        self.title('文本助手')
        self.qrc = tkinter.Label(self)
        self.ent = tkinter.Text(self, width=28, height=6)
        self.ent.insert(1.0, self.ss)
        self.ent.focus()

        self.bind('<KeyRelease>',self.onKeyRelease)

        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.update_idletasks()
        self.qrc.pack()
        self.ent.pack(padx=2, pady=2, fill=tkinter.constants.BOTH, expand=True, side=tkinter.BOTTOM) # BOTTOM为了在Label隐藏再显示后所在位置一致
        self.setQrcode(self.slices[self.cnt])
        setCenter(self)
        self.deiconify()

    def onKeyRelease(self, evt):
        if evt.keysym == 'Escape':
            self.destroy()
        else:
            if evt.keysym == 'F1':
                self.cnt = max(self.cnt-1,0)
            elif evt.keysym == 'F2':
                self.cnt = min(self.cnt+1,len(self.slices)-1)
            elif evt.keysym in ['Control_L', 'Return', 'BackSpace']:
                ss2 = self.ent.get('0.0', 'end')[:-1]
                if self.ss != ss2:
                    self.ss = ss2
                    self.cnt = 0
                    self.slices = graph_split(self.ss, qrlen)
            self.setQrcode(self.slices[self.cnt])
            setCenter(self)

    def setQrcode(self, string):
        if self.string != string:
            self.string = string
            if string == '':
                bm.append(qrmake(string))
                self.qrc.config(image=bm[-1])
                self.qrc.pack()
                self.qrc.forget()
            else:
                bm.append(qrmake(string))
                self.qrc.config(image=bm[-1])
                self.qrc.pack()
            print('-------------\nPage: %s/%s\n============='%(self.cnt+1,len(self.slices)))

if __name__ == '__main__':
    top = myPanel()
    top.mainloop()
