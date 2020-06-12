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

import os
import base64
import serial
import serial.tools.list_ports

log = 'log_received.txt'

def file_decode(s):
    name, data = base64.urlsafe_b64decode(s.encode()).split(b'\n', 1)
    name = name.decode()
    os.makedirs('recv_file', exist_ok=True)
    with open('recv_file/'+name, 'wb') as f:
        f.write(data)
    brief = data[:20] + b'.........' + data[-20:]
    print('Write File:', name)
    print('Write Data:', brief)

def get_port():
    port_scaner = None
    port_list = serial.tools.list_ports.comports()
    for port in port_list:
        if port[1][0:5] == 'HH400':
            port_scaner = port[0]
            print('scaner:', port_scaner)
    return port_scaner

class storage:
    def __init__(self):
        self.total = 0
        self.lines = {}

    def add(self, s):
        if s.count('.') != 1:
            print('Input Error: %s'%s[:20])
            return None
        header, line = s.split('.')
        cnt = int(header[4:])
        total = int(header[:4])
        if self.total != total:
            self.total = total
            self.lines = {}
        self.lines[cnt] = line
        print('Read: %s/%s'%(cnt,self.total)) # 由于数字标号在二维码生成环节有实际意义，所以从1开始编号而非从0开始

        if len(self.lines) == self.total:
            data = ''
            for i in range(1, self.total+1):
                data += self.lines[i]
            return data
        else:
            print('Recv: %s/%s'%(len(self.lines),self.total))
            for i in range(1, self.total+1):
                if i not in self.lines:
                    print('Next: %s'%i)
                    return None

if __name__ == '__main__':
    store = storage()

    if os.path.exists(log):
        with open(log, 'r') as f:
            ss = f.read().split(',')
        for s in ss:
            data = store.add(s)
            if data:
                file_decode(data)
        print('Load history')

    scaner = get_port()
    if scaner:
        ser = serial.Serial(scaner,115200)

    while True:
        if scaner:
            ss = ser.readline().decode()[0:-1].split(',')
        else:
            ss = input('input line(s): ').split(',')
        for s in ss:
            data = store.add(s)
            if data:
                file_decode(data)
                with open(log, 'w') as f:
                    f.write('')
            else:
                with open(log, 'a') as f:
                    f.write(s + ',')

