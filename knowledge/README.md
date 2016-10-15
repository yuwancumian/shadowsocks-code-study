知识总结
===

从代码阅读过程中学习到的知识点,知识点没有固定顺序,是在阅读代码的过程中想到的.

1. `getattr`

```
获取对象的属性,这里说的属性是类的key/value属性,不包括函数.
getattr(object, name[, default])
name必须是字符串,如果对象没有name这个属性的话,就会返回默认值,和dict中get类似,如果没有设置默认值,那么就会报错AtrributeError.
hasattr(object, name)
判断对象是否有某个属性,如果有的话返回True,没有的话返回False,这个是基于getattr实现的,看getattr是否抛出错误.
setattr(object, name, value)
为对象的属性赋值,该属性可以存在或者不存在
delattr(object, name)
删除一个已经存在的属性

class Person(object):
    def __init__(self, name):
        self.name = name


p = Person("Rocky")

print hasattr(p, "name")
print p.__dict__
print getattr(p, "name")
print setattr(p, "sex", "man")
print p.__dict__
delattr(p, "sex")
print getattr(p, "sex", "woman")

输出:
True
{'name': 'Rocky'}
Rocky
None
{'name': 'Rocky', 'sex': 'man'}
woman

```

2. python3中byte和str的转换

`由于python3中byte和str类型显性不同,默认是不会自动转换的`

![转换](https://raw.githubusercontent.com/hellorocky/blog/master/picture/byte2str.jpg)
