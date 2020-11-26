# O(log n) space skip-list-inspired data structure

## Point of the Project

The main point of the project is create/develop/implement an efficient data structure that adapts the hierarchy of the skip list, randomized height, and possibly the skipping, to only need O(n) complexity, instead of O(n log n).

## Main idea

The main idea is to visualize the skip list as a multiset rendered as a directed hypergraph, in which the traversal direction is from the hyperedge that contains the elements with the biggest multiplicity to the ones with the smallest.

## Current variants

* Linear search hypergraph with skipping

* Binary search hypergraph without skipping

* B+Tree hypergraph

* Binary heap hypergraph (heapq) 

* Multiple nested arrays hypergraph

## Next Step

* Interval Tree for searching

* Splaying

* Access-based distribution