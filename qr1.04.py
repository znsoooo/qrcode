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

# 20190509
# 取消默认值
# 当二维码内容为空时隐藏二维码
# 启动时窗口所在位置设定
# 窗口大小变化前后窗口中心保持不变(但可以拖动)
# 键盘响应热键: Esc/F1/F2/Ctrl/Enter/Back

# 20190510
# 响应鼠标操作
# 翻页时所在光标移动到指定位置
# 修改横向布局
# 窗口总大小保持不变(Text弹性)

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
    if len(qrlog) < 40: print(qrlog)
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
            print('-------------\nPage: %s/%s\n============='%(self.cnt+1,len(self.slices)))

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