from operator import attrgetter
from sortedcontainers import SortedList
import bisect
import math
import random as random
from pyroaring import BitMap
from multiprocessing import Process, Queue, cpu_count
from multiprocessing.dummy import Pool
from functools import partial
import timeit
import numpy as np

def cleanup_processes(processes):
    for process in processes:
        process.terminate()

def binarysearch(a, x):
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        #print(a[i], x)
        return True
    else:
        return False
    
    
#splits the overloaded list into two consecutive parts
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
    
# # manual, process-based parallelization
#
# class LookupProcess(Process):
#     def __init__(self, queue, he, nr):
#         Process.__init__(self)
#         self.queue = queue
#         self.he = he
#         self.nr = nr
    
#     def lookup(self, he, nr):
#         if nr <= he.sublists[-1].max:
#             i = bisect.bisect_left(he.sublists, nr)

#             if i != len(he.sublists) and he.sublists[i].indexes[0] <= nr:
#                 if binarysearch(he.sublists[i].indexes, nr):
#                     return True

#         return False

#     def run(self):
#         result = self.lookup(self.he, self.nr)
#         self.queue.put(result)
        
class LookupWorkers():
    def __init__(self):
        self.pool = Pool()
        self.result = False

    def callback(self, result):
        for found_in_height in result:
            if found_in_height:
                self.result = True
                self.pool.terminate()
                break

    def run(self, job, heights, nr):
        results = self.pool.map_async(partial(job, nr=nr), heights, callback=self.callback)
        
        self.pool.close()
        self.pool.join()
        
        return self.result
    
class SplitList:# Rucy, rename it!
    def __init__(self):
        self.height = -1
        self.blists = []
        self.load = 2000
        
    def lookup_subprocess(he, nr, callback):
        if nr <= he.sublists[-1].max:
            i = bisect.bisect_left(he.sublists, nr)

            if i != len(he.sublists) and he.sublists[i].indexes[0] <= nr:
                if binarysearch(he.sublists[i].indexes, nr):
                    callback(True)

        callback(False)   

    def lookup(self, nr):
        workers = LookupWorkers()
        result = workers.run(self.lookup_subprocess, self.blists, nr)
        
        return result

    def insert(self, nr):
        ## Getting the estimated geometric distribution
        height = int(-(math.log2(random.random())))
        ## Checking whether we need to add new edges
        if self.height < height:
            for i in range(height - self.height):
                B = LevelList()
                C = IntervalList(nr)
                C.max = -1 #arbitrary contemporary max
                B.sublists.append(C)
                self.blists.append(B)
            self.height = height

        ## Getting the to-be-added list
        blist = self.blists[height]

        ## Doing the search to see which Intervallist it should be in
        L = len(blist.sublists)
        i = bisect.bisect_left(blist.sublists, nr)

        ## If it's smaller than all other elements then just insort it
        if i == 0 or L == 1:
            candid = blist.sublists[0]
            bisect.insort_left(candid.indexes, nr)
            candid.max = candid.indexes[-1]
            if len(candid.indexes) == self.load:
                    OverloadSimple(blist, 0, self.load)
        ## If it's bigger than all the other elements than just append it
        elif i == L:
            candid = blist.sublists[-1]
            candid.indexes.append(nr)
            candid.max = nr
            if len(candid.indexes) == self.load:
                    OverloadSimple(blist, i-1, self.load)

            ## Else add it
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
            print("--------" + str(len(i.sublists)) +"-----------")
            for j in i.sublists:
                print(j.indexes)

    def show_minmax(self):
        for i in self.blists:
            print(f'({i.min}, {i.max})')
            