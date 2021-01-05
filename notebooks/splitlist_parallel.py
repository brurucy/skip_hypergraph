from operator import attrgetter
from sortedcontainers import SortedList
import bisect
import math
import random as random
from pyroaring import BitMap

from multiprocessing import Process, Queue, cpu_count, Pool, Value, Array
from functools import partial
import timeit
import numpy as np
SENTINEL = 'SENTINEL'

def cleanup_processes(processes):
    for process in processes:
        process.terminate()


def binarysearch(a, x):
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        # print(a[i], x)
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
    # B.i = - blist.sublists[i].i - 1
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


class LookupWorker(object):
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def lookup_subprocess(self, heights, nr, batch_indices):
        # TODO: maybe get args from shared memory instead
        start, end = batch_indices
        for he in heights[start:end]:
            if nr <= he.sublists[-1].max:
                i = bisect.bisect_left(he.sublists, nr)

                if i != len(he.sublists) and he.sublists[i].indexes[0] <= nr:
                    if binarysearch(he.sublists[i].indexes, nr):
                        self.output_queue.put(True)
                        return

        self.output_queue.put(False)
        return


class SplitList:  # Rucy, rename it!
    def __init__(self):
        self.height = -1
        self.blists = []
        self.load = 2000
        self.lookup_input_queue = None
        self.lookup_output_queue = None

    def initWorkers(self):
        self.lookup_input_queue = Queue()
        self.lookup_output_queue = Queue()
        self.n_workers = cpu_count() - 1
        self.pool = Pool(self.n_workers, self.run, (self.lookup_input_queue, self.lookup_output_queue))

    def callback(self, result):
        for found_in_height in result:
            if found_in_height:
                self.lookup_result = True
                break

    # this runs inside each forked process
    def run(self, input_queue, output_queue):
        while True:
            query = input_queue.get()
            if query == SENTINEL:
                break
            shared_heights, shared_nr, shared_batch_indices = query
            worker = LookupWorker(output_queue)
            worker.lookup_subprocess(shared_heights, shared_nr.value, shared_batch_indices)

    def done(self):
        for i in range(self.n_workers):
            self.lookup_input_queue.put(SENTINEL)
        
        self.pool.terminate()
        self.pool.close()
        self.pool.join()

    def lookup(self, nr):
        if self.lookup_input_queue is None:
            self.initWorkers()
        
        batch_size, batch_left = divmod(len(self.blists), self.n_workers)
        shared_heights = Array(f'heights', self.blists)
        shared_nr = Value('nr', nr)

        for i in range(self.n_workers):
            take_heights = batch_size
            if batch_left > 0:
                take_heights += 1
                batch_left -= 1       
            shared_batch_indices = Array('indices', (i*take_heights, i*take_heights+take_heights))
            
            # print((i*take_heights, i*take_heights+take_heights))     
            self.lookup_input_queue.put((shared_heights, shared_nr, shared_batch_indices))

        result = False
        for i in range(self.n_workers):
            # waits
            result = self.lookup_output_queue.get() or result

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
