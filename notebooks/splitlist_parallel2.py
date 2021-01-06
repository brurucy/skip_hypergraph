from operator import attrgetter
from sortedcontainers import SortedList
import bisect
import math
import random as random
from pyroaring import BitMap
from multiprocessing import Process, Queue, cpu_count, set_start_method
from multiprocessing.dummy import Pool
from functools import partial
import timeit
import numpy as np
import time

set_start_method('fork') # NOTE: this is only availabe on UNIX (NOT on Windows)


def binarysearch(a, x):
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        #print(a[i], x)
        return True
    else:
        return False


# splits the overloaded list into two consecutive parts
def splitterSimple(arr, load):
    half = load // 2
    zs = [0] * half
    for i in range(half-1, -1, -1):
        zs[i] = arr.pop()
    return zs

# if overload is detected, splits and adds a new split into levellist


def OverloadSimple(blist, i, load):
    B = IntervalList(5)
    candidate_sublist = blist.sublists[i]
    B.indexes = splitterSimple(candidate_sublist.indexes, load)
    #B.i = - blist.sublists[i].i - 1
    B.max = candidate_sublist.max
    candidate_sublist.max = candidate_sublist.indexes[-1]
    blist.sublists.insert(i+1, B)


class IntervalList:
    def __init__(self, nr):
        self.indexes = [nr]
        self.max = float("-inf")

    def __lt__(self, other):
        if isinstance(other, int):
            return self.max < other
        else:
            return self.max < other.max


class LevelList:
    def __init__(self):
        self.sublists = []
        self.min = float("inf")
        self.max = float("-inf")

    def __lt__(self, other):
        return self.max > other


class LookupWorkers():
    def __init__(self):
        self.n_workers = cpu_count() - 1
        self.pool = Pool(self.n_workers)
        self.result = False

    def callback(self, result):
        if result == True:
            self.result = True
            self.pool.terminate()

    def run(self, job, nr):

        batch_size, batch_left = divmod(len(global_heights), self.n_workers)

        for i in range(self.n_workers):
            take_heights = batch_size
            if batch_left > 0:
                take_heights += 1
                batch_left -= 1
            indices = (i*take_heights, i*take_heights+take_heights)
            try:
                self.pool.apply_async(job, args=(nr, indices), callback=self.callback)
            except ValueError:
                break

        self.pool.close()
        self.pool.join()

        return self.result


def lookup_subprocess(nr, indices):
    start, end = indices
    for he in global_heights[start:end]:
        if nr <= he.sublists[-1].max:
            i = bisect.bisect_left(he.sublists, nr)

            if i != len(he.sublists) and he.sublists[i].indexes[0] <= nr:
                if binarysearch(he.sublists[i].indexes, nr):
                    return True

    return False


class SplitList:  # Rucy, rename it!
    def __init__(self):
        self.height = -1
        self.blists = []
        self.load = 2000

    def lookup(self, nr):
        global global_heights
        global_heights = self.blists

        workers = LookupWorkers()
        result = workers.run(lookup_subprocess, nr)

        return result

    def insert(self, nr):
        # Getting the estimated geometric distribution
        height = int(-(math.log2(random.random())))
        # Checking whether we need to add new edges
        if self.height < height:
            for i in range(height - self.height):
                B = LevelList()
                C = IntervalList(nr)
                C.max = -1  # arbitrary contemporary max
                B.sublists.append(C)
                self.blists.append(B)
            self.height = height

        # Getting the to-be-added list
        blist = self.blists[height]

        # Doing the search to see which Intervallist it should be in
        L = len(blist.sublists)
        i = bisect.bisect_left(blist.sublists, nr)

        # If it's smaller than all other elements then just insort it
        if i == 0 or L == 1:
            candid = blist.sublists[0]
            bisect.insort_left(candid.indexes, nr)
            candid.max = candid.indexes[-1]
            if len(candid.indexes) == self.load:
                OverloadSimple(blist, 0, self.load)
        # If it's bigger than all the other elements than just append it
        elif i == L:
            candid = blist.sublists[-1]
            candid.indexes.append(nr)
            candid.max = nr
            if len(candid.indexes) == self.load:
                OverloadSimple(blist, i-1, self.load)

            # Else add it
        else:
            candidate_sublist = blist.sublists[i]
            # if the element is also bigger than the minimum of the current list than we insort it
            if candidate_sublist.indexes[0] <= nr:
                bisect.insort_left(candidate_sublist.indexes, nr)

                if len(blist.sublists[i].indexes) == self.load:
                    OverloadSimple(blist, i, self.load)
            # then the element must be smaller then the min of the current list but therefore
            # bigger than the max of the previous list-- so we just append it
            else:
                candidate_sublist = blist.sublists[i-1]
                candidate_sublist.indexes.append(nr)
                candidate_sublist.max = nr

                if len(candidate_sublist.indexes) == self.load:
                    OverloadSimple(blist, i-1, self.load)

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
