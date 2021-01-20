# Witchcraft <a href='https://bigdata.cs.ut.ee/'><img src='logo.png' align="right" height="138.5" /></a>

Witchcraft is a library that contains a (small) family of novel, probabilistic, in memory, cheap and easily parallelized, data structures.

Here's some characteristics:

1. O(n) space complexity.
2. The data structures are, **thematically**, named with **incredibly** creative names. `TeleportList` has an interval-tree-like search, while `SplitList` splits its internal sublists in buckets, similarly to a B-Tree.
3. `TeleportList` and `SplitList` make use of `MinMaxList`, which is an ordered list that provides O(1) access to max and min values.
4. Approximately ~ average O(log n) complexity for search, insert and delete.
5. `SkipList`'s geometric-height-sort-of-thing hierarchy is kept.

## How to install

1. `git clone https://github.com/brurucy/witchcraft`
2. `python3 -m pip install -e .`
3. `python3 -m setup pytest`
4. then, wherever you want to use it: `import witchcraft as wc`

## TODO, in order of importance

### Main todos

* ~~make it a kv store~~. // using a dict on the lower level

* ~~Add delete, either as actually deleting an element, or just marking it as deleted.~~ // delete and discard added

* ~~Use bloom filters to speed up recurring queries~~ // roaring bitmaps used

* ~~Use the abstract classes `collections.abc` to wrap the SplitList and Roaring Stuff 2~~ // Rucy

* ~~Fix the Readme and Improve the wording on the Notebook~~ - Priority // Rucy

* ~~Clean up the implementations and normalize them~~ // Rucy

* ~~Complexity stuff and Description~~ // Jonas

* ~~Parallelization Attempt~~ // Nikita

* ~~Improve Bisect / Monobound Binary Search used instead~~ // Nikita

* ~~Final benchmarks~~ // Nikita.

* ~~Paper-ish thingy~~ // canceled

* ~~Poster Draft~~ // Johnny 

* ~~Make the graphs~~ // Rucy

* ~~Format/arrange stuff in the Poster~~ // Johnny

* ~~Parallelization Attempt 2.0~~ // Nikita // canceled

## Data Structures Classification

We have two data structures.

All the ones indexed by roaring bitmaps, are `SortedDict`

`SortedDict` has indexes distributed over the structure, while the data is in the top level.

`SortedList` has only the indexes, that cannot be Bitmaps, and can be any sort of complex python object.

## Extra todos

* Caching, LFU. experiments. We could make it so that every time we add a new element it goes straight to a cache, and once it is overflown, then it evicts it to the actual data structure. [This could be a starting point](https://github.com/luxigner/lfu_cache)

* Inverted Indexes. Index all mins/max.

* [Learned Index](https://github.com/gvinciguerra/PyGM)

## Interesting papers and resources:

* [Hypergraph coverage with ant colony optimization](https://blizzard.cs.uwaterloo.ca/~apat/projects/ACO-Hypergraph.pdf?fbclid=IwAR2VaxtnG11zyXvQsfvs5GmV_a7PwHPjvd86S2TorQJVyAf5JPdi8bHd3tY)
* [Sorted containers](http://www.grantjenks.com/docs/sortedcontainers/)
* [Higher-Dimensional models of networks](https://arxiv.org/pdf/0909.4314v1.pdf)
* [Splay Lists](https://arxiv.org/pdf/2008.01009.pdf)
* [The hypergraph bible](http://compalg.inf.elte.hu/~tony/Oktatas/Algoritmusok-hatekonysaga/Berge-hypergraphs.pdf)
* [B-Skip-List](https://arxiv.org/pdf/1005.0662.pdf)
* [Nice skip list implementation with fast RNG](https://github.com/geertj/pyskiplist/blob/master/pyskiplist/skiplist.py)

at first we really wanted to turn this into a hypergraph problem, but in the end we didn't 🤙.