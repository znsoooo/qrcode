# -*- coding: utf-8 -*-

# Name: QR-Code Helper
# Version: 1.05
# Author: github.com/znsoooo/qrcode

# Usage
# A way to easily convert text into QR-Code without network.
# An easy way to convert long text into a series of QR-Codes, so the text can be transferred without network.
# Load clipboard or input text to convert QR-Code.

# Hotkey
# Submit:   Enter, Ctrl, Backspace
# PageUp:   F1, Right mouse
# PageDown: F2, Left mouse
# Close:    Esc, Middle mouse

try:
    import Tkinter as tkinter
except:
    import tkinter as tkinter
from PIL import ImageTk
import qrcode

qrlen = 1000
print('=============')

def qrmake(qrstr):
    img = qrcode.make(qrstr, version=20, box_size=2, border=2)
    bm = ImageTk.PhotoImage(image=img)
    return bm

def qrlog(qrstr, page, total):
    qrlog = qrstr.replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')
    if len(qrlog) < 40:
        print(qrlog)
    else:
        print(qrlog[:10] + '...\n...\n...' + qrlog[-10:])
    print('-------------\nLength: %s\nPage: %s/%s\n============='%(len(qrstr),page,total))

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

bm=[]

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

        x0 = - 100 + 0.2 * self.winfo_screenwidth() # 100: 补偿初始Tk界面为200x200
        y0 = - 100 + 0.7 * self.winfo_screenheight()
        self.geometry('+%d+%d'%(x0,y0))
        self.minsize(400,206)

        self.title('文本助手')
        self.qrc = tkinter.Label(self)
        self.ent = tkinter.Text(self, width=1, height=15)
        self.ent.insert(1.0, self.ss)
        self.ent.mark_set('insert','0.0') # 程序首次运行时不使用see函数,否则会有未知原因半行内容沉没在Text窗体上面一点点
        self.ent.focus()

        self.bind('<KeyRelease>',self.onKeyRelease)
        self.qrc.bind('<Button>',self.onKeyRelease)

        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.update_idletasks()
        self.ent.pack(padx=2, pady=2, fill=tkinter.constants.BOTH, expand=True, side=tkinter.RIGHT) # RIGHT为了在Label隐藏再显示后所在位置一致
        self.qrc.pack()
        self.setQrcode(self.slices[self.cnt])
        self.deiconify()

    def onKeyRelease(self, evt):
        if evt.num == 1:
            evt.keysym = 'F2'
        elif evt.num == 3:
            evt.keysym = 'F1'
        elif evt.num == 2:
            evt.keysym = 'Escape'
        if evt.keysym == 'Escape':
            self.destroy()
        else:
            if evt.keysym in ['F1','F2']:
                if evt.keysym == 'F1':
                    self.cnt = max(self.cnt-1,0)
                else:
                    self.cnt = min(self.cnt+1,len(self.slices)-1)
                text_pre = ''.join(self.slices[:self.cnt])
                self.ent.see(self.setCursor(text_pre))
                self.setQrcode(self.slices[self.cnt])
            elif evt.keysym in ['Control_L', 'Return', 'BackSpace']:
                ss2 = self.ent.get('0.0', 'end')[:-1]
                if self.ss != ss2:
                    self.ss = ss2
                    self.cnt = 0
                    self.slices = paragraph(self.ss, qrlen)
                self.setQrcode(self.slices[self.cnt])

    def setQrcode(self, string):
        if self.string != string:
            self.string = string
            if string == '':
                self.qrc.forget()
            else:
                bm.append(qrmake(string))
                self.qrc.config(image=bm[-1])
                self.qrc.pack()
        qrlog(string, self.cnt+1, len(self.slices))

    def setCursor(self, text):
        index = len(text)
        ss = text[:index].splitlines()
        if ss == []:
            ss = ['']
        pos = '%s.%s'%(len(ss),len(ss[-1]))
        self.ent.mark_set('insert', pos)
        return pos


if __name__ == '__main__':
    top = myPanel()
    top.mainloop()
