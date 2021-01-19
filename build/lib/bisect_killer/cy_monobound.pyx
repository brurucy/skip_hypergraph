import numpy as np
cimport numpy as np
ctypedef np.npy_intp INTP

# monobound_binary_search from https://github.com/scandum/binary_search/blob/master/binary-search.c
cpdef bint binary_search(long[:] array, int array_size, int key):
	cdef INTP bot, mid, top

	bot = 0
	top = array_size

	while top > 1:
		mid = top / 2


		if key >= array[bot + mid]:
			bot += mid
		top -= mid

	if key == array[bot]:
		return bot
	return -1