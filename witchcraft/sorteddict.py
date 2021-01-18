from pyroaring import BitMap
from math import log2
from bisect import bisect_left, insort_left
from random import random


class RoaringMinMaxBitmap():
    def __init__(self):
        self.indexes = BitMap()
        self.max = float('-inf')
        self.min = float('inf')

    def insert(self, key):
        self.indexes.add(key)
        self.max = self.indexes.max()
        self.min = self.indexes.min()

    def discard(self, key):
        self.indexes.discard(key)
        if not self.indexes:
            self.max = float('-inf')
            self.min = float('inf')
        else:
            self.max = self.indexes.max()
            self.min = self.indexes.min()

    def __lt__(self, other):
        return self.indexes.min() < other


class RoaringTeleportList(dict):

    def __init__(self):
        super().__init__()
        self.height = -1
        self.subindexes = []

    def insert(self, key, value=None):

        height = int(-(log2(random())))

        if self.height < height:
            for i in range(height - self.height):
                self.subindexes.append(RoaringMinMaxBitmap())
            self.height = height

        highest = self.subindexes[height]

        if key not in highest.indexes:
            highest.insert(key, value)
            dict.__setitem__(self, key, value)

    def lookup(self, key):

        for i in self.subindexes:
            if i.min <= key <= i.max:
                if key in i.indexes:
                    return dict.__getitem__(self, key)
        return False

    def delete(self, key):
        for i in self.subindexes:
            if i.min <= key <= i.max:
                if key in i.indexes:
                    dict.__setitem__(self, key, '<deleted>')

    def discard(self, key):
        for i in self.subindexes:
            if i.min <= key <= i.max:
                if key in i.indexes:
                    i.discard(key)
                    dict.__delitem__(self, key)

    def show_hedges(self):
        for i in self.subindexes:
            print(i.indexes)

    def show_minmax(self):
        for i in self.subindexes:
            print(f'({i.min}, {i.max})')


class RoaringMaxDict:
    def __init__(self):
        self.indexes = BitMap()
        self.max = float("-inf")

    def insert(self, key):
        self.indexes.add(key)
        self.max = self.indexes.max()

    def discard(self, key):
        self.indexes.discard(key)
        if not self.indexes:
            self.max = float('-inf')
        else:
            self.max = self.indexes.max()

    def __lt__(self, other):
        if isinstance(other, int):
            return self.max < other
        else:
            return self.max < other.max


class SortableSubList:
    def __init__(self):
        self.sublists = []


def splitter_two(arr, load):
    half = load // 2
    zs = arr[0:half]
    arr = arr.difference(zs)
    return zs


def Overload(blist, i, load):
    B = RoaringMaxDict()
    candidate_sublist = blist.sublists[i]
    B.indexes = splitter_two(candidate_sublist.indexes, load)
    B.max = B.indexes.max()
    insort_left(blist.sublists, B)


class RoaringSplitList(dict):
    def __init__(self, load):
        super().__init__()
        self.height = -1
        self.blists = []
        self.load = load

    def lookup(self, key):
        for he in self.blists:
            if key <= he.sublists[-1].max:
                i = bisect_left(he.sublists, key)
                if i != len(he.sublists) and he.sublists[i].indexes[0] <= key:
                    if key in he.sublists[i].indexes:
                        return dict.__getitem__(self, key)

        return False

    def insert(self, key, value):
        height = int(-(log2(random())))
        if self.height < height:
            for i in range(height - self.height):
                B = SortableSubList()
                C = RoaringMaxDict()
                B.sublists.append(C)
                self.blists.append(B)
            self.height = height

        blist = self.blists[height]

        L = len(blist.sublists)
        i = bisect_left(blist.sublists, key)

        if i == 0 or L == 1:
            updated_maxlist = blist.sublists[0].indexes
            updated_maxlist.add(key)
            dict.__setitem__(self, key, value)
            blist.sublists[0].max = updated_maxlist.max()
            if len(updated_maxlist) == self.load:
                Overload(blist, 0, self.load)
        elif i == L:
            updated_maxlist = blist.sublists[-1].indexes
            updated_maxlist.add(key)
            dict.__setitem__(self, key, value)
            blist.sublists[-1].max = key
            if len(updated_maxlist) == self.load:
                Overload(blist, i - 1, self.load)

        else:
            updated_maxlist = blist.sublists[i].indexes
            if updated_maxlist[0] <= key:
                updated_maxlist.add(key)
                dict.__setitem__(self, key, value)
                blist.sublists[i].max = updated_maxlist.max()
                if len(updated_maxlist) == self.load:
                    Overload(blist, i, self.load)
            else:
                updated_maxlist = blist.sublists[i - 1].indexes
                updated_maxlist.add(key)
                dict.__setitem__(self, key, value)
                blist.sublists[i - 1].max = key
                if len(updated_maxlist) == self.load:
                    Overload(blist, i - 1, self.load)

    def show_hedges(self):
        for i in self.blists:
            maxes = [j.max for j in i.sublists]
            print(maxes)

    def show_edges(self):
        for i in self.blists:
            print("--------" + str(len(i.sublists)) + "-----------")
            for j in i.sublists:
                print(j.indexes)

    def show_minmax(self):
        for i in self.blists:
            print(f'({i.min}, {i.max})')
