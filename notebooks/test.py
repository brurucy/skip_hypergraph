#
# This file serves for easy profiling of the parallelized SplitList with `py-spy`
#

from splitlist_parallel import SplitList as SplitListParallelized
import random

random.seed(0)

split_list_parallel = SplitListParallelized()

nr = 100
ten_thousand_integers = [random.randint(1, 2000000) for i in range(nr)]

def test_insert_SplitListParallelized():
    for i in range(nr):
        split_list_parallel.insert(ten_thousand_integers[i])
  
def test_lookup_SplitListParallelized():
    for i in range(nr):
        split_list_parallel.lookup(ten_thousand_integers[i] + 1)


if __name__ == '__main__':
  test_insert_SplitListParallelized()
  test_lookup_SplitListParallelized()
