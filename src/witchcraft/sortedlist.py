from bisect import bisect_left, insort_left
from math import log2
from random import random
from array import array
from witchcraft.bisect_killer.cy_monobound import binary_search as monobound_binary_search

def handle_overflow(list_of_buckets, i, load, support_cython=False):
    B = Bucket(support_cython)
    candidate_bucket = list_of_buckets.list_of_buckets[i]
    half_load = load // 2
    new_bucket_indexes = [0] * half_load if not support_cython else array('l', [0]) * half_load
    for i in range(half_load - 1, -1, -1):
        new_bucket_indexes[i] = candidate_bucket.indexes.pop()
    B.indexes = new_bucket_indexes
    B.min = B.indexes[0]
    B.max = candidate_bucket.max
    candidate_bucket.max = candidate_bucket.indexes[-1]
    insort_left(list_of_buckets.list_of_buckets, B)

class Bucket:
    def __init__(self, support_cython=False):
        self.indexes = [] if not support_cython else array('l')
        self.max = float("-inf")
        self.min = float("inf")

    def __lt__(self, other):
        if isinstance(other, int):
            return self.max < other
        else:
            return self.max < other.max


class ListOfBuckets:
    def __init__(self):
        self.list_of_buckets = []
        self.min = float("inf")
        self.max = float("-inf")

    def __lt__(self, other):
        return self.max > other


class SplitList:
    def __init__(self, load=2000):
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

    def lookup(self, nr):
        for he in self.heights:
            lb = he.list_of_buckets
            if len(lb) != 0:
                if not (nr > lb[-1].max or nr < lb[0].min):
                    i = bisect_left(lb, nr)
                    if i != len(lb) and not (lb[i].min > nr):
                        j = bisect_left(lb[i].indexes, nr)
                        if j != len(lb[i].indexes) and lb[i].indexes[j] == nr:
                            return True

        return False

    def insert(self, nr):
        height = int(-(log2(random())))
        if self.maximum_height < height:
            for i in range(height - self.maximum_height):
                B = ListOfBuckets()
                C = Bucket()
                B.list_of_buckets.append(C)
                self.heights.append(B)
            self.maximum_height = height

        height = self.heights[height]

        L = len(height.list_of_buckets)
        i = bisect_left(height.list_of_buckets, nr)

        if i == 0:
            candidate_bucket = height.list_of_buckets[0]
            insort_left(candidate_bucket.indexes, nr)
            candidate_bucket.max = candidate_bucket.indexes[-1]
            candidate_bucket.min = candidate_bucket.indexes[0]

            if len(candidate_bucket.indexes) == self.load:
                handle_overflow(height, 0, self.load)
        elif i == L:
            candidate_bucket = height.list_of_buckets[-1]
            candidate_bucket.indexes.append(nr)
            candidate_bucket.max = nr
            candidate_bucket.min = candidate_bucket.indexes[0]
            if len(candidate_bucket.indexes) == self.load:
                handle_overflow(height, i - 1, self.load)
        else:
            candidate_bucket = height.list_of_buckets[i]
            if candidate_bucket.min <= nr:
                insort_left(candidate_bucket.indexes, nr)
                candidate_bucket.min = candidate_bucket.indexes[0]
                if len(height.list_of_buckets[i].indexes) == self.load:
                    handle_overflow(height, i, self.load)
            else:
                candidate_bucket = height.list_of_buckets[i - 1]
                candidate_bucket.indexes.append(nr)
                candidate_bucket.max = nr

                if len(candidate_bucket.indexes) == self.load:
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


### MONOBOUND ###

class MonoboundSplitList:
    def __init__(self, load=2000):
        self.maximum_height = -1
        self.heights = []
        self.load = load
    
    def delete(self, nr): #not tested in this notebook
        for he in self.heights:
            lb = he.list_of_buckets
            if len(lb) != 0: 
                if not(nr > lb[-1].max or nr < lb[0].min): 
                    i = bisect_left(lb, nr)
                    if i != len(lb) and not(lb[i].min > nr):
                        j = monobound_binary_search(hee[i].indexes, len(lb[i].indexes), nr)
                        if j >= 0:
                            if len(lb[i].indexes) == 1:
                                del lb[i]
                            else:
                                del lb[i].indexes[j]
                                lb[i].max = lb[i].indexes[-1]
                                lb[i].min = lb[i].indexes[0]
                            return True

        return False
    
    def lookup(self, nr):
        for he in self.heights:
            lb = he.list_of_buckets
            if len(lb) != 0: 
                if not( nr > lb[-1].max or nr < lb[0].min): #skipping
                    i = bisect_left(lb, nr)
                    if i != len(lb) and not(lb[i].min > nr):
                        j = monobound_binary_search(lb[i].indexes, len(lb[i].indexes), nr)
                        if j >= 0:
                            return True

        return False

    def insert(self, nr):
        height = int(-(log2(random())))
        if self.maximum_height < height:
            for i in range(height - self.maximum_height):
                B = ListOfBuckets()
                C = Bucket(support_cython=True)
                B.list_of_buckets.append(C)
                self.heights.append(B)
            self.maximum_height = height

        height = self.heights[height]

        L = len(height.list_of_buckets)
        i = bisect_left(height.list_of_buckets, nr)

        if i == 0:
            candidate_bucket = height.list_of_buckets[0]
            insort_left(candidate_bucket.indexes, nr)
            candidate_bucket.max = candidate_bucket.indexes[-1]
            candidate_bucket.min = candidate_bucket.indexes[0]
            
            if len(candidate_bucket.indexes) == self.load:
                handle_overflow(height, 0, self.load, support_cython=True)
        elif i == L:
            candidate_bucket = height.list_of_buckets[-1]
            candidate_bucket.indexes.append(nr)
            candidate_bucket.max = nr
            candidate_bucket.min = candidate_bucket.indexes[0]
            if len(candidate_bucket.indexes) == self.load:
                handle_overflow(height, i - 1, self.load, support_cython=True)
        else:
            candidate_bucket = height.list_of_buckets[i]
            if candidate_bucket.min <= nr:
                insort_left(candidate_bucket.indexes, nr)
                candidate_bucket.min = candidate_bucket.indexes[0]
                if len(height.list_of_buckets[i].indexes) == self.load:
                    handle_overflow(height, i, self.load, support_cython=True)
            else:
                candidate_bucket = height.list_of_buckets[i - 1]
                candidate_bucket.indexes.append(nr)
                candidate_bucket.max = nr

                if len(candidate_bucket.indexes) == self.load:
                    handle_overflow(height, i - 1, self.load, support_cython=True)

    def show_hedges(self):
        for i in self.heights:
            maxes = [j.max for j in i.list_of_buckets]
            print(maxes)

    def show_edges(self):
        for i in self.heights:
            print("--------" + str(len(i.list_of_buckets)) +"-----------")
            for j in i.list_of_buckets:
                print(j.indexes)

    def show_minmax(self):
        for i in self.heights:
            print(f'({i.min}, {i.max})')
