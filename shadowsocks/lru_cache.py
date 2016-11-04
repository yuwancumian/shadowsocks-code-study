#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2015 clowwindy
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

from __future__ import absolute_import, division, print_function, \
    with_statement

import collections
import logging
import time


# this LRUCache is optimized for concurrency, not QPS
# n: concurrency, keys stored in the cache
# m: visits not timed out, proportional to QPS * timeout
# get & set is O(1), not O(n). thus we can support very large n
# TODO: if timeout or QPS is too large, then this cache is not very efficient,
#       as sweep() causes long pause


class LRUCache(collections.MutableMapping):
    """This class is not thread safe"""

    def __init__(self, timeout=60, close_callback=None, *args, **kwargs):
        self.timeout = timeout  # 缓存多长时间的DNS解析结果
        self.close_callback = close_callback
        self._store = {}  # 存储域名-->IP的解析结果
        self._time_to_keys = collections.defaultdict(list)  # {timestamp: [google.com, facebook.com, ...], ...}
        self._keys_to_last_time = {}  # 每一个域名被解析/被访问的时间戳映射,{google.com: timestamp, facebook.com: timestamp,...}
        self._last_visits = collections.deque()  # 时间戳队列,先入先出
        self._closed_values = set()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        # O(1)
        t = time.time()
        self._keys_to_last_time[key] = t
        self._time_to_keys[t].append(key)
        self._last_visits.append(t)
        return self._store[key]

    def __setitem__(self, key, value):
        # O(1)
        t = time.time()
        self._keys_to_last_time[key] = t
        self._store[key] = value
        self._time_to_keys[t].append(key)
        self._last_visits.append(t)

    def __delitem__(self, key):
        # O(1)
        del self._store[key]
        del self._keys_to_last_time[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def sweep(self):
        # O(m)
        now = time.time()
        c = 0
        while len(self._last_visits) > 0: # 最近请求时间的一个双端队列列表,里面的元素是浮点类型时间戳
            least = self._last_visits[0] # 获取距离现在时间最长的那个时间戳
            if now - least <= self.timeout: # 如果队列中距离现在时刻最长的那个时间戳都没有超时的话就退出当前while循环,否则继续
                break
            if self.close_callback is not None:  # 如果关闭的回调函数不为空
                for key in self._time_to_keys[least]:  # 遍历距离现在时间最长的那个时刻的解析/访问域名列表
                    if key in self._store:  # 如果已经缓存了解析结果
                        if now - self._keys_to_last_time[key] > self.timeout:  # 如果这个域名最近一次访问/解析的时间超过设定的超时时间
                            value = self._store[key]  # 获取这个IP地址
                            if value not in self._closed_values:  # 如果这个IP地址不在将被清空的列表里
                                self.close_callback(value)  # 将这个IP地址传递给关闭时回掉函数
                                self._closed_values.add(value)  # 并把这个IP地址添加到待清空的列表里
            self._last_visits.popleft()  # 删除时间戳队列中距离现在时刻最长的那一个时间戳
            for key in self._time_to_keys[least]:  # 遍历距离现在时刻最长的那个时间戳所对应的访问/解析的域名列表
                if key in self._store:  # 如果这个域名在待删除的结合中
                    if now - self._keys_to_last_time[key] > self.timeout:  # 如果这个域名访问的时间戳超过定义的超时时间(超时)
                        del self._store[key]  # 从待删除集合中删除该域名
                        del self._keys_to_last_time[key]  # 从域名-->timestamp字典中删除该元素
                        c += 1  # 开始定义为0,每次遇到一个符合删除条件的就加1
            del self._time_to_keys[least]  # 从{timestamp: [google.com,facebook.com...],...}中删除距离现在时刻最长的那个时间戳
        if c:  # 如果待删除的域名个数不为0的话
            self._closed_values.clear()  # 清空待删除集合
            logging.debug('%d keys swept' % c)


def test():
    c = LRUCache(timeout=0.3)

    c['a'] = 1
    assert c['a'] == 1

    time.sleep(0.5)
    c.sweep()
    assert 'a' not in c

    c['a'] = 2
    c['b'] = 3
    time.sleep(0.2)
    c.sweep()
    assert c['a'] == 2
    assert c['b'] == 3

    time.sleep(0.2)
    c.sweep()
    c['b']
    time.sleep(0.2)
    c.sweep()
    assert 'a' not in c
    assert c['b'] == 3

    time.sleep(0.5)
    c.sweep()
    assert 'a' not in c
    assert 'b' not in c

    global close_cb_called
    close_cb_called = False

    def close_cb(t):
        global close_cb_called
        assert not close_cb_called
        close_cb_called = True

    c = LRUCache(timeout=0.1, close_callback=close_cb)
    c['s'] = 1
    c['s']
    time.sleep(0.1)
    c['s']
    time.sleep(0.3)
    c.sweep()

if __name__ == '__main__':
    test()
