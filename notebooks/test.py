#
# This file serves for easy profiling of the parallelized SplitList with `py-spy`
#

from multiprocessing import freeze_support
import random

def test_insert_SplitListParallelized(lst, nr):
    for i in range(nr):
        lst.insert(ten_thousand_integers[i])


def test_lookup_SplitListParallelized(lst, nr):
    for i in range(nr):
        lst.lookup(ten_thousand_integers[i])

if __name__ == '__main__':
    freeze_support()
    from splitlist_parallel import SplitList as SplitListParallelized
    random.seed(0)

    split_list_parallel = SplitListParallelized()

    size = 1_000_000
    ten_thousand_integers = [random.randint(1, 2000000) for i in range(size)]

    reps = 100
    test_insert_SplitListParallelized(split_list_parallel, reps)
    test_lookup_SplitListParallelized(split_list_parallel, reps)
    split_list_parallel.done()
