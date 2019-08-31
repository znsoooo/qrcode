# -*- coding: utf-8 -*-

# Name: QR-Code Helper
# Version: 1.07
# Platform: >= 2.7 or >= 3.4(suggestion)
# Author: github.com/znsoooo/qrcode

# Usage
# A way to easily convert text into QR-Code without network.
# An easy way to convert long text into a series of QR-Codes, so the text can be transferred without network.
# Load clipboard or input text to convert QR-Code.

# Hotkey
# Submit: Enter/Backspace/Ctrl, Mouse up
# Open: F1, Mouse double right
# PgUp: F2, Mouse single right
# PgDn: F3, Mouse single left
# Goto: F4, Mouse double left
# Exit: ESC, Mouse middle

try:
    import Tkinter as tkinter
    import tkSimpleDialog
    import tkFileDialog
    tkinter.simpledialog = tkSimpleDialog
    tkinter.filedialog = tkFileDialog
    from ScrolledText import ScrolledText
except:
    import tkinter
    import tkinter.filedialog
    import tkinter.simpledialog
    from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk
import qrcode

import os
import base64
import hashlib

__ver__ = 'v1.07'

zh_cn = 1
qrlen = 1000
print('=============')

def qrmake(qrstr):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(qrstr)
    qr.best_fit(start=20)
    qr.makeImpl(False, 3) # 3 or 6
    img = qr.make_image()
    img2 = ImageTk.PhotoImage(image=img)
    return img2

def paragraph(text, lenth):
    sentence = ''
    res = []
    for word in text:
        if len(sentence.encode('utf-8')) < lenth:
            sentence = sentence + word
        else:
            res.append(sentence)
            sentence = word
    res.append(sentence)
    return res

def getIndex(text):
    index = len(text)
    ss = text[:index].splitlines()
    if ss == []:
        ss = ['']
    pos = '%s.%s'%(len(ss),len(ss[-1]))
    return pos

def log(text, info):
    log = text.replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')
    if len(log) < 40:
        print(log)
    else:
        print(log[:10] + '...\n...\n...' + log[-10:])
    print('-------------\nLength: %s\n%s\n============='%(len(log),info))

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        try:
            self.ss = self.clipboard_get()
        except:
            self.ss = ''
        self.cnt = 0
        self.slices = paragraph(self.ss, qrlen)
        self.string = None

        if not os.path.exists('config.ini'):
            x = - 100 + 0.2 * self.winfo_screenwidth() # 100: 补偿初始Tk界面为200x200
            y = - 100 + 0.7 * self.winfo_screenheight()
            xy = '+%d+%d'%(x,y)
            with open('config.ini','w') as f:
                f.write(xy)
        with open('config.ini','r') as f:
            xy = f.read()
        self.geometry(xy)
        self.minsize(450,206)

        self.qrc = tkinter.Label(self)
        self.ent = ScrolledText(self, width=1, height=15)
        self.ent.insert(1.0, self.ss)
        self.ent.mark_set('insert','0.0') # 程序首次运行时不使用see函数,否则会有未知原因半行内容沉没在Text窗体上面一点点
        self.ent.focus()

        text = self.slices[self.cnt]
        basic = (len(self.slices),len(self.ss))
        info = 'Page: %s, Length: %s'%basic
        if zh_cn:
            info = '共%s页, %s字'%basic

        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.update_idletasks()
        self.ent.pack(padx=2, pady=2, fill='both', expand=True, side='right') # RIGHT为了在Label隐藏再显示后所在位置一致
        self.qrc.pack()
        self.setQrcode(text, info)
        self.deiconify()

        self.qrc.bind('<Button-2>',self.onExit)
        self.qrc.bind('<Button-1>',self.fliping)
        self.qrc.bind('<Button-3>',self.fliping)
        self.qrc.bind('<Double-Button-1>',self.setting)
        self.qrc.bind('<Double-ButtonRelease-3>',self.openFile) # 没有Release会在窗口打开之后的鼠标抬起时唤起右键菜单

        self.ent.bind('<Escape>',self.onExit)
        self.ent.bind('<F1>',self.openFile)
        self.ent.bind('<F2>',self.fliping)
        self.ent.bind('<F3>',self.fliping)
        self.ent.bind('<F4>',self.setting)

        self.ent.bind('<KeyRelease>',self.refresh)
        self.ent.bind('<ButtonRelease-1>',self.selected)
        self.bind('<Destroy>',lambda evt:self.onExit(evt,close=True))

        try:
            import windnd
            windnd.hook_dropfiles(self, func=self.openFile)
        except:
            pass

    def setQrcode(self, string, info):
        if self.string != string:
            self.string = string
            if string == '':
                self.qrc.forget()
            else:
                global img
                img = qrmake(string)
                self.qrc.config(image=img)
                self.qrc.pack()
        log(string, info)
        self.title('Text Helper %s (%s)'%(__ver__, info))
        if zh_cn:
            self.title('文本助手%s (%s)'%(__ver__, info))

    def refresh(self, evt):
        if evt.keysym in ['Control_L', 'Return', 'BackSpace']:
            ss2 = self.ent.get('0.0', 'end')[:-1]
            if self.ss != ss2:
                self.ss = ss2
                self.cnt = 0
                self.slices = paragraph(self.ss, qrlen)

            text = self.slices[self.cnt]
            basic = (len(self.slices),len(self.ss))
            info = 'Page: %s, Length: %s'%basic
            if zh_cn:
                info = '共%s页, %s字'%basic
            self.setQrcode(text, info)

    def fliping(self, evt):
        if evt.num == 1 or evt.keysym == 'F3':
            self.cnt = min(self.cnt+1,len(self.slices)-1)
        else:
            self.cnt = max(self.cnt-1,0)
        cur1 = getIndex(''.join(self.slices[:self.cnt]))
        cur2 = getIndex(''.join(self.slices[:self.cnt+1]))
        self.setCursor(cur1, cur2)

        text = self.slices[self.cnt]
        basic = (self.cnt+1,len(self.slices),len(text),len(self.ss))
        info = 'Page: %s/%s, Sel: %s/%s'%basic
        if zh_cn:
            info = '第%s/%s页, 共%s/%s字'%basic
        self.setQrcode(text, info)

    def selected(self, evt):
        if self.ent.tag_ranges('sel'):
            text = self.ent.selection_get()
            info = 'Sel: %s/%s'%(len(text),len(self.ss))
            if zh_cn:
                info = '选中%s/%s字'%(len(text),len(self.ss))
            self.setQrcode(text, info)

    def setCursor(self, cur1, cur2):
        self.ent.mark_set('insert', cur1)
        self.ent.tag_remove('sel','0.0','end')
        self.ent.tag_add('sel',cur1,cur2)
        self.ent.see(cur1)

    def setting(self, evt):
        max_page = len(self.slices)
        num = tkinter.simpledialog.askinteger('Goto','Go to page (1-%s):'%max_page, initialvalue=self.cnt+1)
        self.ent.focus()
        if num:
            self.cnt = max(1,min(max_page,num)) - 1

            text = self.slices[self.cnt]
            basic = (self.cnt+1,len(self.slices),len(text),len(self.ss))
            info = 'Page: %s/%s, Sel: %s/%s'%basic
            if zh_cn:
                info = '第%s/%s页, 共%s/%s字'%basic
            self.setQrcode(text, info)

    def openFile(self, evt):
        if isinstance(evt, list):
            path = evt[0].decode('gbk') # utf-8不对
        else:
            path = tkinter.filedialog.askopenfilename()
        if path != '':
            filename = os.path.basename(path)
            with open(path,'rb') as f:
                s = f.read()
            try:
                try:
                    res = s.decode()
                except:
                    try:
                        res = s.decode('gbk')
                    except:
                        raise
            except:
                s = base64.urlsafe_b64encode(filename.encode()+b'\n'+s).decode()
                total = int((len(s)-1)/(qrlen-10)+1)
                res = ''
                for i in range(total):
                    res += '%04d%04d.%s,'%(total, i+1, s[(qrlen-10)*i:(qrlen-10)*(i+1)])

            self.ss = res
            self.cnt = 0
            self.slices = paragraph(self.ss, qrlen)
            self.ent.delete(1.0, 'end')
            self.ent.insert(1.0, res)

            text = self.slices[self.cnt]
            basic = (len(self.slices),len(self.ss))
            info = 'Page: %s, Length: %s'%basic
            if zh_cn:
                info = '共%s页, %s字'%basic
            self.setQrcode(text, info)

    def onExit(self, evt, close=False):
        xy = '+%d+%d'%(self.winfo_x(),self.winfo_y())
        with open('config.ini','w') as f:
            f.write(xy)
        if not close:
            self.destroy()

if __name__ == '__main__':
    top = myPanel()
    top.mainloop()
