from operator import attrgetter
from sortedcontainers import SortedList
import bisect
import math
import random as random
from pyroaring import BitMap
from multiprocessing import Process, Queue
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

class SplitList:# Rucy, rename it!
    def __init__(self):
        self.height = -1
        self.blists = []
        self.load = 2000

    def lookup_process(self, queue, he, nr):
        i = bisect.bisect_left(he.sublists, nr)

        if i != len(he.sublists) and he.sublists[i].indexes[0] <= nr:
            if binarysearch(he.sublists[i].indexes, nr):
                queue.put(True)
            
        queue.put(False)

    def lookup(self, nr):
        processes = []
        queue = []
        
        for he in self.blists: 
            if nr <= he.sublists[-1].max:
                p = Process(lookup_process, (queue, he, nr))
                p.start()
                processes.append(p)
        
        for i in processes:
            process_result = queue.get() # blocks until *some* process finishes
            if process_result is True:
                cleanup_processes(processes)
                return True      
            
        cleanup_processes(processes)
        
        #print(nr) #can be used to detect if the search works or not
        return nr

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

            
# benchmarks

def test():
    
    random.seed(0)

    splist = SplitList()

    nr = 1000000

    ten_thousand_integers = [random.randint(1, 2000000) for i in range(nr)]
    
    def lookup_nlist(novus):
        for i in range(nr):
            novus.lookup(ten_thousand_integers[i])
    
    lookup_nlist(splist)
    print('done')

            
if __name__ == '__main__':
    from timeit import Timer, timeit, repeat
    runs = 3
    loops = 1
    times = repeat("test()", "from __main__ import test", number=loops, repeat=runs)
    
    print(f'{np.mean(times):.2f} s ± {(np.std(times) * 1000):.2f} ms per loop (mean ± std. dev. of {runs} runs, {loops} loop each)', )
    
#     %timeit -r 10 -n 1 lookup_tlist(tlist)
#     %timeit -r 10 -n 1 lookup_rslist(rslist)
#     %timeit -r 10 -n 1 lookup_slist(slist)
#     %timeit -r 10 -n 1 lookup_nlist(splist)