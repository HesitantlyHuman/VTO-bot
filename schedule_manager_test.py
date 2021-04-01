import pytest
import time
from datetime import date
from schedule_manager import *

today = date.today()

time_to_index_cases = [
    (time.struct_time([2000, 5, 2, 5, 30, 0, 0, 0, 0]), 66),
    (time.struct_time([1995, 12, 23, 22, 30, 0, 0, 0, 0]), 270),
    (time.struct_time([2021, 3, 19, 15, 30, 30, 0, 0, 0]), 187),
    (time.struct_time([2021, 3, 19, 15, 32, 56, 0, 0, 0]), 187)
]

@pytest.mark.parametrize('time, expected', time_to_index_cases)
def test_time_to_index(time, expected):
    assert ScheduleManager._time_to_index(time) == expected

index_to_time_cases = [
    (66, time.struct_time([today.year, today.month, today.day, 5, 30, 0, 0, 0, 0])),
    (270, time.struct_time([today.year, today.month, today.day, 22, 30, 0, 0, 0, 0]))
]

@pytest.mark.parametrize('index, expected', index_to_time_cases)
def test_index_to_time(index, expected):
    assert ScheduleManager._index_to_time(index) == expected

set_slot_cases = [
    #Test case #1
    ({'date': {'value': '2021-03-17', 'description': '3/17/21'}, 'startTime': {'value': '12:55:00.000', 'description': '12:55 PM'}, 'endTime': {'value': '13:45:00.000', 'description': '1:45 PM'}, 'slotCount': 15, 'activity': {'oid': '8a81a18c4d01ed2e014d445ca41a0189', 'name': 'VTO', 'iconOid': '2c991199169cd16001169cd16dd301a9'}, 'visible': True, 'minLength': {'value': 300000, 'description': '00:05:00'}, 'adg': {'oid': None, 'name': None, 'type': None}, 'skillLogicalOperation': None, 'notes': None, 'schedChangesExist': False, 'entity': {'oid': '8a80a9b977ed6b290177f463f7fd17ca', 'name': 'Phint_Core_Total', 'id': 4006, 'type': 'muset', 'timeZone': 'America/Denver'}, 'oid': '8a80a9b977ed6d9001784187de733020'},
    ['none' for i in range(288)],
    ['none' for i in range(155)] + ['vto' for i in range(10)] + ['none' for i in range(123)]),
    #Test case #2
    ({'name' : 'vto', 'start_time' : '8:00:00.000', 'end_time' : '12:00:00.000', 'oid' : '1k230dsf0j2r2'},
    ['none' for i in range(145)] + ['open' for i in range(12)] + ['none' for i in range(131)],
    ['none' for i in range(96)] + ['vto' for i in range(48)] + ['none' for i in range(1)] + ['open' for i in range(12)] + ['none' for i in range(131)])
]

@pytest.mark.parametrize('slot, schedule, expected', set_slot_cases)
def test_set_slot(slot, schedule, expected):
    assert len(schedule) == len(expected), 'The test case is incorrect'
    ScheduleManager.set_slot(slot, schedule)
    assert schedule == expected

generate_schedule_requests_cases = [
    #Test case #1 (Generating a valid request)
    ({'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'},
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(33)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.localtime(1000000),
    [{'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}]),
    #Test case #2 (Abutting against other vto)
    ({'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'},
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(3)] + ['vto' for i in range(16)] + ['open' for i in range(14)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.localtime(1000000),
    [{'name' : 'vto', 'start_time' : '15:20:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}]),
    #Test case #3 (Generating multiple requests)
    ({'name' : 'vto', 'start_time' : '14:00:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'},
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(13)] + ['vto' for i in range(6)] + ['open' for i in range(14)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.localtime(1000000),
    [{'name' : 'vto', 'start_time' : '14:00:00.000', 'end_time' : '14:50:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}, {'name' : 'vto', 'start_time' : '15:20:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}]),
    #Test case #4 (Abutting against current time)
    ({'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'},
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(33)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.struct_time([today.year, today.month, today.day, 15, 30, 0, 0, 0, 0]),
    [{'name' : 'vto', 'start_time' : '15:35:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}]),
    #Test case #5 (Abutting against current time, unaligned)
    ({'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'},
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(33)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.struct_time([today.year, today.month, today.day, 15, 34, 12, 0, 0, 0]),
    [{'name' : 'vto', 'start_time' : '15:35:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}]),
    #Test case #6 (Multiple posted slots)
    ([{'name' : 'vto', 'start_time' : '15:10:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}, {'name' : 'vto', 'start_time' : '15:20:00.000', 'end_time' : '16:30:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17mn'}],
    ['none' for i in range(150)] + ['open' for i in range(12)] + ['break' for i in range(3)] + ['open' for i in range(33)] + ['break' for i in range(3)] + ['open' for i in range(9)] + ['none' for i in range(78)],
    ['none' for i in range(150)] + ['vto' for i in range(60)] + ['none' for i in range(78)],
    time.struct_time([today.year, today.month, today.day, 15, 34, 12, 0, 0, 0]),
    [{'name' : 'vto', 'start_time' : '15:35:00.000', 'end_time' : '16:00:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17ca'}, {'name' : 'vto', 'start_time' : '16:00:00.000', 'end_time' : '16:30:00.000', 'oid' : '8a80a9b977ed6b290177f463f7fd17mn'}])
]

@pytest.mark.parametrize('slots, schedule, desired, current_time, expected', generate_schedule_requests_cases)
def test_generate_schedule_requests(slots, schedule, desired, expected, current_time):
    sc = ScheduleManager(agent_schedule = schedule, desired_schedule = desired)
    assert sc.generate_schedule_requests(slots, current_time = current_time) == expected

get_slot_details_cases = [
    ({'date': {'value': '2021-03-17', 'description': '3/17/21'}, 'startTime': {'value': '12:55:00.000', 'description': '12:55 PM'}, 'endTime': {'value': '13:45:00.000', 'description': '1:45 PM'}, 'slotCount': 15, 'activity': {'oid': '8a81a18c4d01ed2e014d445ca41a0189', 'name': 'VTO', 'iconOid': '2c991199169cd16001169cd16dd301a9'}, 'visible': True, 'minLength': {'value': 300000, 'description': '00:05:00'}, 'adg': {'oid': None, 'name': None, 'type': None}, 'skillLogicalOperation': None, 'notes': None, 'schedChangesExist': False, 'entity': {'oid': '8a80a9b977ed6b290177f463f7fd17ca', 'name': 'Phint_Core_Total', 'id': 4006, 'type': 'muset', 'timeZone': 'America/Denver'}, 'oid': '8a80a9b977ed6d9001784187de733020'},
    ('vto', time.struct_time([today.year, today.month, today.day, 12, 55, 0, 0, 0, 0]), time.struct_time([today.year, today.month, today.day, 13, 45, 0, 0, 0, 0])))
]

@pytest.mark.parametrize('slot, expected', get_slot_details_cases)
def test_get_slot_details(slot, expected):
    out = ScheduleManager._get_slot_details(slot)
    name_matches = out[0] == expected[0]
    start_matches = out[1][:-3] == expected[1][:-3]
    end_matches = out[2][:-3] == expected[2][:-3]
    assert all([name_matches, start_matches, end_matches])
