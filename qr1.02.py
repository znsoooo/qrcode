# -*- coding: utf-8 -*-

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
    qr=qrcode.QRCode(version=20, box_size=2, border=2)
    qr.add_data(qrstr)
    img=qr.make_image()
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

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth() - top.winfo_reqwidth())*0.2
    y = (top.winfo_screenheight() - top.winfo_reqheight())*0.8
    top.geometry('+%d+%d'%(x,y))

def getClipboard():
    w.OpenClipboard()
    try:
        d = w.GetClipboardData(win32con.CF_TEXT).decode('gbk')
    except:
        d = 'usage: znsoooo.com/qrcode'
    w.CloseClipboard()
    return d

bm=[]

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.ss = getClipboard()
        self.cnt = 0
        self.slices = graph_split(self.ss, qrlen)
        self.string = None

        self.title('二维码助手')
        self.qrc = tkinter.Label(self)
        self.ent = tkinter.Text(self, width=20, height=6)
        self.ent.insert(1.0, self.ss)
        self.ent.focus()

        self.bind('<KeyRelease>',self.onKeyRelease)

        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.qrc.pack()
        self.ent.pack(padx=2, pady=2, fill=tkinter.constants.BOTH, expand=True)
        self.setQrcode(self.slices[self.cnt])
        setCenter(self)
        self.deiconify()

    def onKeyRelease(self, evt):
        if evt.keysym == 'Escape':
            self.destroy()
        else:
            if evt.keysym == 'Left':
                self.cnt = max(self.cnt-1,0)
            elif evt.keysym == 'Right':
                self.cnt = min(self.cnt+1,len(self.slices)-1)
            else:
                ss2 = self.ent.get('0.0', 'end')[:-1]
                if self.ss != ss2:
                    self.ss = ss2
                    self.cnt = 0
                    self.slices = graph_split(self.ss, qrlen)
            self.setQrcode(self.slices[self.cnt])

    def setQrcode(self, string):
        if self.string != string:
            self.string = string
            bm.append(qrmake(string))
            self.qrc.configure(image=bm[-1])
            print('-------------\nPage: %s/%s\n============='%(self.cnt+1,len(self.slices)))

if __name__ == '__main__':
    top = myPanel()
    top.mainloop()