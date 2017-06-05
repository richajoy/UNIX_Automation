#! /usr/bin/env python
class DoubleRep(object):
    def __str__(self):
        return "Hi, This is a string"
    def __repr__(self):
        return "Hi, This is a repr"

dr = DoubleRep()
print dr
dr
