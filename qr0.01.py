# -*- coding: utf-8 -*-

# Name: QR-Code Lite Helper
# Version: 0.01
# Author: github.com/znsoooo/qrcode

# Usage
# A way to easily convert text into QR-Code without network.
# An easy way to convert long text into a series of QR-Codes, so the text can be transferred without network.
# Load text from clipboard and convert to QR-Code.
# Restart to reload text in clipboard.

# Hotkey
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

def paragraph(text, lenth):
    total = 0
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

        x0 = - 100 + 0.2 * self.winfo_screenwidth() # 100: 补偿初始Tk界面为200x200
        y0 = - 100 + 0.7 * self.winfo_screenheight()
        self.geometry('+%d+%d'%(x0,y0))

        self.title('文本助手')
        self.qrc = tkinter.Label(self)

        self.bind('<KeyRelease>',self.onKeyRelease)
        self.bind('<Button>',self.onKeyRelease)

        self.withdraw() # withdraw/deiconify 阻止页面闪烁
        self.qrc.pack()
        self.setQrcode(self.slices[self.cnt])
        self.deiconify()

    def onKeyRelease(self, evt):
        if evt.keysym == 'Escape' or evt.num == 2:
            self.destroy()
        elif evt.keysym == 'F1' or evt.num == 3:
            self.cnt = max(self.cnt-1,0)
            self.setQrcode(self.slices[self.cnt])
        elif evt.keysym == 'F2' or evt.num == 1:
            self.cnt = min(self.cnt+1,len(self.slices)-1)
            self.setQrcode(self.slices[self.cnt])

    def setQrcode(self, string):
        bm.append(qrmake(string))
        self.qrc.config(image=bm[-1])
        self.qrc.pack()
        print('-------------\nLength: %s\nPage: %s/%s\n============='%(len(string),self.cnt+1,len(self.slices)))


if __name__ == '__main__':
    top = myPanel()
    top.mainloop()
