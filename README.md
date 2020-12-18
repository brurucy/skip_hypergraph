# O(log n) space skip-list-inspired data structure

## Point of the Project

The main point of the project is create/develop/implement an efficient data structure that adapts the hierarchy of the skip list, randomized height, and possibly the skipping, to only need O(n) complexity, instead of O(n log n).

## Main idea

The main idea is to visualize the skip list as a multiset rendered as a directed hypergraph, in which the traversal direction is from the hyperedge that contains the elements with the biggest multiplicity to the ones with the smallest.

## Current variants

* Linear search hypergraph with skipping // done, awful lol

* Binary search hypergraph without skipping // done, very nice(read as borat)

* B+Tree hypergraph // in the works, takes advantage of sorting many n lists of very small size

* Binary heap hypergraph // done! can be optimized much more if it uses the `heapq` module

* Ultra Hyper Graph 😡 // done! Benchmark Hypergraph, done with the most efficient sorted list implementation out there ![sortedcontainers](http://www.grantjenks.com/docs/sortedcontainers/)

## Next Step

* Interval Tree for searching -- done

* Splaying

* Access-based distribution

* Hypergraph Set search : 

## Interesting papers and resources:

* [Hypergraph coverage with ant colony optimization](https://blizzard.cs.uwaterloo.ca/~apat/projects/ACO-Hypergraph.pdf?fbclid=IwAR2VaxtnG11zyXvQsfvs5GmV_a7PwHPjvd86S2TorQJVyAf5JPdi8bHd3tY)
* [Sorted containers](http://www.grantjenks.com/docs/sortedcontainers/)
* [Higher-Dimensional models of networks](https://arxiv.org/pdf/0909.4314v1.pdf)
* Splay Lists
* BB-Tree
* [The hypergraph bible](http://compalg.inf.elte.hu/~tony/Oktatas/Algoritmusok-hatekonysaga/Berge-hypergraphs.pdf)
* [B-Skip-List](https://arxiv.org/pdf/1005.0662.pdf)
* [Nice skip list implementation with fast RNG](https://github.com/geertj/pyskiplist/blob/master/pyskiplist/skiplist.py)