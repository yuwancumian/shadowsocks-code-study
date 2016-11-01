#!/usr/bin/env python
# coding:utf-8
import os
import time
import signal


"""
信号相关:

SIGKILL 结束进程,kill -9就是向进程发这个信号,这个信号的特点是不能被捕获,忽略或者阻塞
SIGTERM 结束进程,kill 不加任何参数的时候就是向进程发送这个信号,这个信号可以被捕获,忽略等处理,所以很多程序可以利用这一点在退出的时候清空缓存等.
SIGINT  中断进程(表现为结束进程),和SIGTERM相似,可以被捕获处理,一般用于用户终端Ctrl+C发送信号给进程
SIGQUIT 中断进程,跟前三者的区别为这个信号会生成该进程的core dump文件并会清空该进程占用的资源,可以被捕获处理,用户终端通过Ctrl+\发送给进程
SIGSTP  挂起进程, 但不结束进程, 可以发送SIGCONT信号让进程继续, 可以被捕获处理,可以通过ctrl+Z发送
SIGHUP  现在常用于平滑重启服务,比如nginx,ssh等


其他相关:
core dump  核心文件通常在系统收到特定的信号时由操作系统生成。信号可以由程序执行过程中的异常触发，也可以由外部程序发送。动作的结果一般是生成一个某
个进程的内存转储的文件，文件包含了此进程当前的运行堆栈信息。一般用于调试.
Ctrl+D 这不是一个信号,仅仅代表输入的结束,end of file.Ctrl+D, when typed at the start of a line on a terminal, signifies the end of the input. This is not a signal in the unix sense: when an application is reading from the terminal and the user presses Ctrl+D, the application is notified that the end of the file has been reached (just like if it was reading from a file and had passed the last byte).
"""


print os.getpid()

def handler(signum, frame):
    print "Received {0}".format(signum)

signal.signal(signal.SIGUSR1, handler)
signal.signal(signal.SIGINT, handler)

while 1:
    print "waiting..."
    time.sleep(5)



"""
kill -SIGUSR1 pid

"""
