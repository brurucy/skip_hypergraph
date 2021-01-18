# -*- coding: utf-8 -*-

import pytest
from random import randint
from witchcraft.sortedlist import SplitList

__author__ = "brurucy"
__copyright__ = "brurucy"
__license__ = "mit"


def test_split_list_in():
    list_instance = SplitList()
    list_instance.insert(1)
    list_instance.insert(2)
    assert list_instance.lookup(1)
    assert list_instance.lookup(2)


def test_split_list_not_in():
    list_instance = SplitList()
    list_instance.insert(1)
    list_instance.insert(2)
    assert not list_instance.lookup(3)


def test_split_list_many():
    list_instance = SplitList()
    random_integers = [randint(0, 2000000) for i in range(100000)]
    for i in random_integers:
        list_instance.insert(i)
    for i in random_integers:
        assert list_instance.lookup(i)
