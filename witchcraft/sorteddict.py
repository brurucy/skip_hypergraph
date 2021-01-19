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
        if isinstance(other, int):
            return self.max < other
        else:
            return self.max < other.max


class RoaringTeleportList(dict):

    def __init__(self):
        super().__init__()
        self.maximum_height = -1
        self.subindexes = []

    def insert(self, key, value=None):

        height = int(-(log2(random())))

        if self.maximum_height < height:
            for i in range(height - self.maximum_height):
                self.subindexes.append(RoaringMinMaxBitmap())
            self.maximum_height = height

        highest = self.subindexes[height]

        if key not in highest.indexes:
            highest.insert(key)
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


class ListOfBuckets:
    def __init__(self):
        self.list_of_buckets = []
        self.min = float("inf")
        self.max = float("-inf")


def handle_overflow(list_of_buckets, i, load):
    B = RoaringMinMaxBitmap()
    candidate_sublist = list_of_buckets.list_of_buckets[i]
    new_bucket_indexes = candidate_sublist.indexes[:load//2]
    candidate_sublist.indexes = candidate_sublist.indexes.difference(new_bucket_indexes)
    B.indexes = new_bucket_indexes
    B.max = B.indexes.max()
    insort_left(list_of_buckets.list_of_buckets, B)


class RoaringSplitList(dict):
    def __init__(self, load=2000):
        super().__init__()
        self.maximum_height = -1
        self.heights = []
        self.load = load

    def delete(self, nr):
        for he in self.heights:
            lb = he.list_of_buckets
            if len(lb) != 0:
                if not (nr > lb[-1].max or nr < lb[0].min):
                    i = bisect_left(lb, nr)
                    if i != len(lb) and not (lb[i].min > nr):
                        j = bisect_left(lb[i].indexes, nr)
                        if j != len(lb[i].indexes) and lb[i].indexes[j] == nr:
                            if len(lb[i].indexes) == 1:
                                del lb[i]
                            else:
                                del lb[i].indexes[j]
                                lb[i].max = lb[i].indexes[-1]
                                lb[i].min = lb[i].indexes[0]
                            return True

        return False

    def lookup(self, key):
        for he in self.heights:
            if key <= he.list_of_buckets[-1].max:
                i = bisect_left(he.list_of_buckets, key)
                if i != len(he.list_of_buckets) and he.list_of_buckets[i].indexes[0] <= key:
                    if key in he.list_of_buckets[i].indexes:
                        return dict.__getitem__(self, key)

        return False

    def insert(self, key, value):
        height = int(-(log2(random())))
        if self.maximum_height < height:
            for i in range(height - self.maximum_height):
                B = ListOfBuckets()
                C = RoaringMinMaxBitmap()
                B.list_of_buckets.append(C)
                self.heights.append(B)
            self.maximum_height = height

        height = self.heights[height]

        L = len(height.list_of_buckets)
        i = bisect_left(height.list_of_buckets, key)

        if i == 0 or L == 1:
            updated_maxlist = height.list_of_buckets[0].indexes
            updated_maxlist.add(key)
            dict.__setitem__(self, key, value)
            height.list_of_buckets[0].max = updated_maxlist.max()
            if len(updated_maxlist) == self.load:
                handle_overflow(height, 0, self.load)
        elif i == L:
            updated_maxlist = height.list_of_buckets[-1].indexes
            updated_maxlist.add(key)
            dict.__setitem__(self, key, value)
            height.list_of_buckets[-1].max = key
            if len(updated_maxlist) == self.load:
                handle_overflow(height, i - 1, self.load)

        else:
            updated_maxlist = height.list_of_buckets[i].indexes
            if updated_maxlist[0] <= key:
                updated_maxlist.add(key)
                dict.__setitem__(self, key, value)
                height.list_of_buckets[i].max = updated_maxlist.max()
                if len(updated_maxlist) == self.load:
                    handle_overflow(height, i, self.load)
            else:
                updated_maxlist = height.list_of_buckets[i - 1].indexes
                updated_maxlist.add(key)
                dict.__setitem__(self, key, value)
                height.list_of_buckets[i - 1].max = key
                if len(updated_maxlist) == self.load:
                    handle_overflow(height, i - 1, self.load)

    def show_hedges(self):
        for i in self.heights:
            maxes = [j.max for j in i.list_of_buckets]
            print(maxes)

    def show_edges(self):
        for i in self.heights:
            print("--------" + str(len(i.list_of_buckets)) + "-----------")
            for j in i.list_of_buckets:
                print(j.indexes)

    def show_minmax(self):
        for i in self.heights:
            print(f'({i.min}, {i.max})')
