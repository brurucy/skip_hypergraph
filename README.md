# Witchcraft <a href='https://bigdata.cs.ut.ee/'><img src='logo.png' align="right" height="138.5" /></a>

Witchcraft is a library that contains a (small) family of novel, probabilistic, in memory, cheap and easily parallelized, data structures.

Here's some characteristics:

1. O(n) space complexity.
2. The data structures are, **thematically**, named with **incredibly** creative names. `TeleportList` has an interval-tree-like search, while `SplitList` splits its internal sublists in a **very** interesting way.
3. `TeleportList` and `SplitList` make use of `MinMaxList`, which is nothing but an ordered list that provides O(1) access to max and min values.
4. `MaxList` and `MinList` are derivations of `MinMaxList`, that, respectively, do not keep track of min and max, and are, maybe, used as sub levels of the `MinMaxList`.
5. Approximately ~ average O(log n) complexity for search, insert and delete. **TODO** semi-formal complexity reasoning
6. `SkipList`'s geometric-height-sort-of-thing hierarchy is kept.

# Rationale

I wrote this package for you, because things don't excite you anymore.

How many tree-like data structures are out there? ~~more than 8000?(cringy reference I know)~~ I have no idea how many, but, certainly ~~more than we need~~ lots, and, most importantly, you want to try something different, don't you?

This is the right tool for you, if you **really** want to use Skip Lists ~~as long as you don't care about getting the next element in constant time, but let's keep that as a secret~~

So, you might think 🤔, why not just use...Skip Lists?

* **O (n log n) space complexity** 🤢 that is very bad, SAD!.

* **No one seems to care about it?** there's barely any python skip-list libraries. Depressing. 😭

* You want a very cheap, and raw 🍣, kv-store.

* You think `sortedcontainers` is awesome, but you'd prefer to use something that could benefit from the ~~gorillon~~ many different cores your computer has(at some point, because right now it is single threaded 😍). 

## TODO, in order of importance

### Main todos

* ~~make it a kv store~~. // using a dict on the lower level

* ~~Add delete, either as actually deleting an element, or just marking it as deleted.~~ // delete and discard added

* ~~Use bloom filters to speed up recurring queries~~ // roaring bitmaps used

* ~~~Use the abstract classes `collections.abc` to wrap the SplitList and Roaring Stuff 2 - Priority // Rucy~~

* Fix the Readme and Improve the wording on the Notebook 3 - Priority // Rucy

* Clean up the implementations and normalize them 1 - Priority // Rucy

* ~~Complexity stuff and Description~~ // Jonas

* ~~Parallelization Attempt~~ // Nikita

* ~~Improve Bisect / Monobound Binary Search used instead~~ // Nikita

* ~~Final benchmarks // Nikita.~~ 

* ~~Paper-ish thingy // All.~~ // canceled

* ~~Poster Draft. // Johnny~~ 

* Make the graphs // Rucy

* Format/arrange stuff in the Poster // Johnny

* Parallelization Attempt 2.0 // Nikita

### Final Benchmarks considerations

#### Data Structures Classification

We have two data structures.

All the ones indexed by roaring bitmaps, are `SortedDict`

`SortedDict` has indexes distributed over the structure, while the data is in the top level.

`SortedList` has only the indexes, that cannot be Bitmaps. They must be lists/arrays/else.

#### What to benchmark against?

`SortedList` - SplitList, MonoboundSplitList, py-skiplist(whatever the name of the package is), SortedList from sorted containers

`SortedDict` - RoaringSplitList, RoaringTeleportList, SortedDict from sorted containers

#### Ranges to benchmark over

10, 100, 1000, 10000, 100000, 1000000

100/25 repetitions each.

### Extra todos

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