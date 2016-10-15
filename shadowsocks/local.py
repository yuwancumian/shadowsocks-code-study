#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 clowwindy
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

#使用__future__模块来让python 2.X使用3.X的新功能
"""
1. 建议使用绝对引用
2. python3.X中,所有的除法都是精确除法
3. python3.X中,print是一个func,带入该模块后,默认的print不能使用了
4. 使用with语句
引用__future__是为了更多地兼容python2.X和python3.X
"""
from __future__ import absolute_import, division, print_function, \
    with_statement

import sys
import os
import logging
import signal
#把当前目录加入到sys.path的最前面,保证重名的时候出现混乱引入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from shadowsocks import shell, daemon, eventloop, tcprelay, udprelay, asyncdns


@shell.exception_handle(self_=False, exit_code=1)
def main():
    #检查python的版本
    shell.check_python()

    # fix py2exe
    #和 cx_freeze 这个库有关。这是一个用于在 windows 下将程序打包成 exe 的库，会将一个变量 frozen 注入到 sys 中。
    if hasattr(sys, "frozen") and sys.frozen in \
            ("windows_exe", "console_exe"):
        p = os.path.dirname(os.path.abspath(sys.executable))
        os.chdir(p) # 修改目录,相当于cd

    config = shell.get_config(True) # config的数据类型为dict,就是用户配置的config.json
    daemon.daemon_exec(config)

    logging.info("starting local at %s:%d" %
                 (config['local_address'], config['local_port']))

    dns_resolver = asyncdns.DNSResolver()
    tcp_server = tcprelay.TCPRelay(config, dns_resolver, True)
    udp_server = udprelay.UDPRelay(config, dns_resolver, True)
    loop = eventloop.EventLoop()
    dns_resolver.add_to_loop(loop)
    tcp_server.add_to_loop(loop)
    udp_server.add_to_loop(loop)

    def handler(signum, _):
        logging.warn('received SIGQUIT, doing graceful shutting down..')
        tcp_server.close(next_tick=True)
        udp_server.close(next_tick=True)
    # 捕获并处理SIGQUIT信号,如果没有这个信号就注册SIGTERM信号,windows不支持SIGQUIT信号
    signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

    def int_handler(signum, _):
        sys.exit(1)
    signal.signal(signal.SIGINT, int_handler)

    daemon.set_user(config.get('user', None))
    loop.run()

if __name__ == '__main__':
    main()
