from utils import *
import pytest
import numpy as np
import time

base_n_cases = [
    (500, 32, 'fk'),
    (2324, 7, '6530'),
    (23245, 15, '6d4a'),
    (23245, 36, 'hxp')
]

@pytest.mark.parametrize('num, base, expected', base_n_cases)
def test_base_n(num, base, expected):
    assert base_n(num, base) == expected

clearlink_to_libtime_cases = [
    ('10:00:00.000', '2021-05-02', time.struct_time([2021, 5, 2, 10, 0, 0, 0, 0, 0])),
    ('8:54:23.000', '1999-12-23', time.struct_time([1999, 12, 23, 8, 54, 23, 0, 0, 0]))
]

@pytest.mark.parametrize('clearlink_time, clearlink_date, expected', clearlink_to_libtime_cases)
def test_clearlink_to_libtime(clearlink_time, clearlink_date, expected):
    assert clearlink_to_libtime(clearlink_time, clearlink_date)[:-3] == expected[:-3]

libtime_to_clearlink_cases = [
    (time.struct_time([2022, 6, 12, 15, 23, 1, 0, 0, 0]), '15:23:01.000'),
    (time.struct_time([1952, 4, 3, 8, 0, 0, 0, 0, 0]), '8:00:00.000')
]

@pytest.mark.parametrize('libtime, expected', libtime_to_clearlink_cases)
def test_libtime_to_clearlink(libtime, expected):
    assert libtime_to_clearlink(libtime) == expected

try_dictionary_keys_cases = [
    ({'item_one' : 1, 'itemTwo' : 2, 'itemThree' : 3}, ['item_two', 'itemTwo'], 2),
    ({'item_one' : {'item_two' : 3}, 'item_three' : 3}, ['item_two', 'itemTwo', ['item_one', 'item_two']], 3),
    ({'item_one' : {'item_two' : 3}, 'item_three' : 3}, ['item_two', 'itemTwo'], None)
]

@pytest.mark.parametrize('dictionary, keys, expected', try_dictionary_keys_cases)
def test_try_dictionary_keys(dictionary, keys, expected):
    assert try_dictionary_keys(dictionary, keys) == expected

dictionary_retreive_cases = [
    ({'item_one' : 1, 'itemTwo' : 2, 'itemThree' : 3}, ['itemTwo'], 2),
    ({'item_one' : {'item_two' : 3}, 'item_three' : 3}, ['item_one', 'item_two'], 3)
]

@pytest.mark.parametrize('dictionary, key_list, expected', dictionary_retreive_cases)
def test_dictionary_retreive(dictionary, key_list, expected):
    assert dictionary_retreive(dictionary, key_list) == expected

run_endpoints_cases = [
    ([False, True, True, True, False, True, False], [np.array([1, 4]), np.array([5, 6])]),
    ([0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1], [np.array([3, 7]), np.array([9, 11]), np.array([15, 16]), np.array([17, 18]), np.array([19, 20])])
]

@pytest.mark.parametrize('bits, expected', run_endpoints_cases)
def test_run_endpoints(bits, expected):
    out = run_endpoints(bits)
    print(out)
    match_list = []
    for expected_item, received_item in zip(expected, out):
        match_list.append((expected_item == received_item).all())
    match_list.append(len(expected) == len(out))
    assert all(match_list)
