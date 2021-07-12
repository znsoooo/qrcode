# 20181104
# 更新记录和读取History
# 更新接收文件存储到recv_file文件夹下

# 20190616
# 编码格式修改
# 实用的子函数file_decode
# 支持读取和记录
# 支持输入多行数据
# 更全面的调试信息(当前/进度/下一个)
# 更加清晰的程序结构

# 20201025
# 流程优化
# 读取剪切板
# 从文本框中读取
# 接收文件名中包含时间戳
# 生成文件后在打开所在文件夹
# 兼容tk窗口和input输入
# input输入按q退出
# 调试信息并到1行


import os
import time
import base64

log = 'log_received.txt'


class storage:
    def __init__(self):
        self.total = 0
        self.lines = {}


    def add(self, s):
        ss = s.replace('\n', '').split(',')

        for s in ss:
            if s.count('.') != 1:
                if s: # 空行不用报错
                    print('InputError: %s'%s[:20])
                continue

            header, line = s.split('.')
            try:
                cnt   = int(header[4:])
                total = int(header[:4])
            except:
                continue

            if self.total != total:
                self.total = total
                self.lines = {}
            self.lines[cnt] = line

            if len(self.lines) == self.total:
                return ''.join(self.lines[i+1] for i in range(self.total))
            else:
                next_id = min(i + 1 for i in range(self.total) if i + 1 not in self.lines)
            print('Read: %d, Exist: %d/%d, Next: %d'%(cnt, len(self.lines), self.total, next_id)) # 标号范围1~N，而非0~(N-1)



def load(store, log):
    if os.path.exists(log):
        with open(log, 'r') as f:
            s = f.read()
        data = store.add(s)
        file_decode(data, log)
        print('Load history.')


def file_decode(s, log):
    if not s:
        return
    name, data = base64.urlsafe_b64decode(s.encode()).split(b'\n', 1)
    name = name.decode()
    ttime = time.strftime('%Y%m%d_%H%M%S_', time.localtime())
    file = 'recv_file/' + ttime + name
    with open(file, 'wb') as f:
        f.write(data)
    brief = data[:20] + b'.........' + data[-20:]
    print('Write File:', name)
    print('Write Data:', brief)
    os.popen('explorer /select, ' + os.path.abspath(file))
    with open(log, 'w') as f:
        f.write('')
    return data


def refresh(evt=0):
    s = ent.get('1.0', 'end')[:-1]
    data = store.add(s)
    if file_decode(data, log):
        ent.delete('1.0', 'end')


def close():
    s = ent.get('1.0', 'end')[:-1]
    if s:
        with open(log, 'a') as f:
            f.write(s + ',')
    top.destroy()


if __name__ == '__main__':
    os.makedirs('recv_file', exist_ok=True)
    store = storage()
    load(store, log)


    try:
        import tkinter
        from tkinter.scrolledtext import ScrolledText

        top = tkinter.Tk()

        try:
            s = top.clipboard_get()
        except:
            s = ''
        ent = ScrolledText(top)
        ent.pack(fill='both', expand=True)
        ent.insert(1.0, s)
        ent.bind('<KeyRelease>', refresh)
        top.protocol("WM_DELETE_WINDOW", close)
        refresh()

        top.mainloop()


    except Exception as e:
        print('import tkinter failure.')

        s = ''
        while s.lower() != 'q':
            s = input("input line(s): (press 'q' exit) ")
            data = store.add(s)
            if not file_decode(data, log):
                with open(log, 'a') as f:
                    f.write(s + ',')

