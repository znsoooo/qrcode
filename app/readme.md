# QR-Code Helper
- Version: 1.07
- Platform: >= 2.7 or >= 3.4(suggestion)
- Author: github.com/znsoooo/qrcode

## Usage
- A way to easily convert text into QR-Code without network.
- An easy way to convert long text into a series of QR-Codes, so the text can be transferred without network.
- Load clipboard or input text to convert QR-Code.

## Hotkey
- Submit: Enter/Backspace/Ctrl, Mouse up
- Open: F1, Mouse double right
- PgUp: F2, Mouse single right
- PgDn: F3, Mouse single left
- Goto: F4, Mouse double left
- Exit: ESC, Mouse middle


# History

## qr1.07

#### 20180510
- 支持双击打开通过py34运行
- 支持启动置入剪切板内容
- 当剪切板为空或非文本时的default

#### 20190507
- 修改为类
- 基于Python3的编程
- 键盘快捷键(Esc/Left/Right)
- 文本变化后即时改变二维码
- 文本框界面宽度适配
- 其他优化
 
#### 20190509
- 取消默认值
- 当二维码内容为空时隐藏二维码
- 启动时窗口所在位置设定
- 窗口大小变化前后窗口中心保持不变(但可以拖动)
- 键盘响应热键: Esc/F1/F2/Ctrl/Enter/Back

#### 20190510
- 响应鼠标操作
- 翻页时所在光标移动到指定位置
- 修改横向布局
- 窗口总大小保持不变(Text弹性)

#### 20190511
- 当只有触发热键F1/Ctrl等才进入setQrcode
- 当Page1和Page2内容一样时依然打印调试信息

#### 20190614

- __新增功能__
- 读取文件(读取文本/二进制转为base64码)
- 跳转页码
- 标题栏显示系统信息(当前页/总页数/选中字数/总字数)
- 选中文本实时转化为二维码
- 选中转化为二维码对应的文本
- Text增加滚动条
- config.ini记录窗口最后关闭位置
#### 
- __优化__
- 适配py27
- 后台更新图像解决热键响应慢和无法响应双击的问题
- log函数改为"text+info"的组合
- 可配置中英文提示信息
- 热键配置调整
- 事件绑定整理(确定绑定按键/鼠标按下还是抬起)
- onKeyRelease函数拆分为fliping/refresh/onExit三个部分

#### 20190621
- 超级提速生成二维码的速度(不做best_mask_pattern所以理论提速9倍)
- 由于生成二维码速度变快所以不再使用后台线程生成二维码图片

#### 20190827
- 支持拖拽加载文件(windnd: 仅支持py3)
- 提出版本参数到全局变量


## qr0.01

#### 20190511
- 从qr1.05中分支出的仅读取剪切板内容的功能


# TODO
- py2的拖拽
- py2和py3打开文件时的默认解码格式不一样
- 打开文件时选区设定不对
