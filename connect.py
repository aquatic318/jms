#!/usr/bin/env python
# coding: utf-8

"""
    connect.py
    ~~~~~~~~~~~
    This script is the jms endpoint for ssh connect.
    User login the server may first running.

    1. Use SSH Authentication. So not achieve socket and self authentication method.
    2. Use paramiko module as a proxy for your ssh connection
    3. Use ...


    :copyright: (c) 2016 by Jumpserver Team.
    :licence: BSD, see LICENSE for more details.

"""

import os
import sys
import paramiko
import select
import socket
import time

try:
    import termios
    import tty
except ImportError:
    print('\033[1;31m仅支持类Unix系统 Only unix like supported.\033[0m')
    time.sleep(3)
    sys.exit()


username = 'root'
password = 'redhat'
host = '192.168.244.129'
port = 22


def color_print(msg, color='red', exit=False):
    """
    Print colorful string.
    颜色打印字符或者退出
    """
    color_msg = {'blue': '\033[1;36m{0}\033[0m',
                 'green': '\033[1;32m{0}\033[0m',
                 'yellow': '\033[1;33m{0}\033[0m',
                 'red': '\033[1;31m{0}\033[0m',
                 'title': '\033[30;42m{0}\033[0m',
                 'info': '\033[32m{0}\033[0m'}
    msg = color_msg.get(color, 'red').format(msg)
    print(msg)
    if exit:
        time.sleep(2)
        sys.exit()
    return msg


class TTY:
    def __init__(self, host='127.0.0.1', port=22, username='root', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.chan = None
        self.__get_chan()

    def __get_chan(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.host,
                        port=self.port,
                        username=self.username,
                        password=self.password)
        except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException):
            color_print('连接服务器失败', exit=True)
        self.ssh = ssh
        self.chan = ssh.invoke_shell(term='xterm')

    def posix_shell(self):
        old_tty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.chan.settimeout(0.0)

            while True:
                try:
                    r, w, e = select.select([self.chan, sys.stdin], [], [])
                except:
                    pass

                if self.chan in r:
                    try:
                        recv_data = self.chan.recv(1024).decode('utf8')
                        if len(recv_data) == 0:
                            break
                        sys.stdout.write(recv_data)
                        sys.stdout.flush()
                    except socket.timeout:
                        print('Timeout')
                if sys.stdin in r:
                    x = os.read(sys.stdin.fileno(), 1024)
                    if len(x) == 0:
                        break
                    self.chan.send(x)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)


if __name__ == '__main__':
    tty_ = TTY(host=host, port=port, username=username, password=password)
    tty_.posix_shell()