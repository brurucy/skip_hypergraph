# -*- coding: utf-8 -*-

import pytest
from random import randint
from witchcraft.sorteddict import RoaringTeleportList, RoaringSplitList

__author__ = "brurucy"
__copyright__ = "brurucy"
__license__ = "mit"


def test_roaring_teleport_list_in():
    list_instance = RoaringTeleportList()
    list_instance.insert(1, 'value')
    list_instance.insert(2, 'value')
    assert list_instance.lookup(1) == 'value'
    assert list_instance.lookup(2) == 'value'


def test_roaring_teleport_list_not_in():
    list_instance = RoaringTeleportList()
    list_instance.insert(1, 'value')
    list_instance.insert(2, 'value')
    assert not list_instance.lookup(3)


def test_roaring_teleport_list_many():
    list_instance = RoaringTeleportList()
    random_integers = [randint(0, 2000000) for i in range(100000)]
    for i in random_integers:
        list_instance.insert(i, 'value')
    for i in random_integers:
        assert list_instance.lookup(i) == 'value'


def test_roaring_split_list_in():
    list_instance = RoaringSplitList(load=2000)
    list_instance.insert(1, 'value')
    list_instance.insert(2, 'value')
    assert list_instance.lookup(1) == 'value'
    assert list_instance.lookup(2) == 'value'


def test_roaring_split_list_not_in():
    list_instance = RoaringSplitList(load=2000)
    list_instance.insert(1, 'value')
    list_instance.insert(2, 'value')
    assert not list_instance.lookup(3)


def test_roaring_split_list_many():
    list_instance = RoaringSplitList(load=2000)
    random_integers = [randint(0, 2000000) for i in range(100000)]
    for i in random_integers:
        list_instance.insert(i, 'value')
    for i in random_integers:
        assert list_instance.lookup(i) == 'value'
