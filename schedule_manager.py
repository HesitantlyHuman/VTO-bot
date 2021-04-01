from utils import *
import numpy as np
import time

class ScheduleManager():
    '''Stores the current schedule, and the desired schedule as lists of strings 288 long (This is the number of 5 minute increments in a day),
    when given a list of available slots, will return a list of desired slots, which the agent may request based on their current schedule'''
    def __init__(self, agent_schedule = ['none' for i in range(288)], desired_schedule = ['none' for i in range(288)], scheduling_delay = 60):
        self.desired_schedule = np.array(desired_schedule, dtype = '<U10')
        self.agent_schedule = np.array(agent_schedule, dtype = '<U10')
        self.scheduling_delay = scheduling_delay

        assert len(self.desired_schedule) == 288, 'desired_schedule must have length 228'
        assert len(self.agent_schedule) == 288, 'agent_schedule must have length 228'

    def generate_schedule_requests(self, posted_slots, current_time = None):
        '''Takes an iterable of posted slots, and returns an iterable of slot requests'''

        if current_time is None:
            current_time = time.localtime()

        desired_slots = []
        schedule_after_pending = self.agent_schedule

        #To help out in the cases that it is just one slot
        if not isinstance(posted_slots, (list, tuple)):
            posted_slots = [posted_slots]

        for slot in posted_slots:
            #If the name of the slot matches the desired_schedule, and the agent_schedule is not the desired schedule, then we want it
            if isinstance(slot, dict):
                name, start_time, end_time = ScheduleManager._get_slot_details(slot)
            elif isinstance(slot, (tuple, list)):
                name, start_time, end_time = slot
            else:
                raise ValueError('Type of posted_slots must be dict, tuple or list, not {}'.format(type(posted_slots)))

            #Cannot change the schedule for time that has already past, and we need to account for delay in servicing the request
            delayed_current_time = time.struct_time([current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5] + self.scheduling_delay, current_time[6], current_time[7], current_time[8]])
            start_time = max(delayed_current_time, start_time)

            start_time_index, end_time_index = ScheduleManager._time_to_index(start_time), ScheduleManager._time_to_index(end_time)

            #Using 'n/a' so that the slots will not match with a desired schedule of none for times outside of their posted values
            new_slot = np.array(['n/a' for i in range(288)])
            new_slot[start_time_index : end_time_index] = [name for i in range(end_time_index - start_time_index)]

            #Decide which 5 min intervals from the new postings we want
            is_desired = (self.desired_schedule == new_slot) & (schedule_after_pending != new_slot)

            #Find the endpoints for each continuous run we desire
            slot_ranges = run_endpoints(is_desired)

            #For each pair of endpoints, generate a new unique request
            for slot_range in slot_ranges:
                new_slot_request = {
                'name' : name,
                'start_time' : libtime_to_clearlink(ScheduleManager._index_to_time(slot_range[0])),
                'end_time' : libtime_to_clearlink(ScheduleManager._index_to_time(slot_range[1])),
                'oid' : try_dictionary_keys(slot, ['oid'])
                }
                desired_slots.append(new_slot_request)

                #Update the schedule we are using to generate these new requests, so that we don't make overlapping requests
                ScheduleManager.set_slot(new_slot_request, schedule_after_pending)

        return desired_slots

    def set_schedule(slots, schedule = None):
        '''Takes an iterable of agent schedule slots, and saves them to the manager'''
        schedule = np.array(schedule)

    def set_slot(slot, schedule = None):
        '''Overides the current schedule using the passed slot'''
        if isinstance(slot, dict):
            name, start_time, end_time = ScheduleManager._get_slot_details(slot)
        elif isinstance(slot, (tuple, list)):
            name, start_time, end_time = slot
        assert isinstance(start_time, time.struct_time), 'start_time must be a time.struct_time object'
        assert isinstance(end_time, time.struct_time), 'end_time must be a time.struct_time object'

        start_time_index, end_time_index = ScheduleManager._time_to_index(start_time), ScheduleManager._time_to_index(end_time)

        schedule[start_time_index : end_time_index] = [name for i in range(end_time_index - start_time_index)]

    def _get_slot_details(slot):
        name = try_dictionary_keys(slot, ['name', ['activity', 'name']])
        start_time = try_dictionary_keys(slot, ['start_time', ['startTime', 'value']])
        end_time = try_dictionary_keys(slot, ['end_time', ['endTime', 'value']])
        return name.lower(), clearlink_to_libtime(start_time), clearlink_to_libtime(end_time)

    def _time_to_index(time):
        return int((time.tm_hour * 12) + np.ceil((time.tm_min / 5) + (time.tm_sec / 300)))

    def _index_to_time(index):
        d = date.today()
        minutes = (index * 5) % 60
        hours = (index * 5) // 60
        return time.struct_time([d.year, d.month, d.day, hours, minutes, 0, 0, 0, 0])
