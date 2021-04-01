import time
from datetime import date
from functools import reduce
import numpy as np
import operator

def base_n(num, base, numerals = "0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (base_n(num // base, base, numerals).lstrip(numerals[0]) + numerals[num % base])

def clearlink_to_libtime(clearlink_time, clearlink_date = str(date.today())):
    date_and_time = clearlink_date + ' ' + clearlink_time[:-4]
    return time.strptime(date_and_time, '%Y-%m-%d %H:%M:%S')

def libtime_to_clearlink(libtime):
    return '{}:{:02d}:{:02d}.000'.format(libtime.tm_hour, libtime.tm_min, libtime.tm_sec)

def try_dictionary_keys(dictionary, keys):
    for key in keys:
        if not isinstance(key, (list, tuple)):
            key = [key]
        try:
            return dictionary_retreive(dictionary, key)
        except KeyError:
            pass
    return None

def dictionary_retreive(dictionary, key_list):
    return reduce(operator.getitem, key_list, dictionary)

def run_endpoints(bits):
    bits = np.array(bits, dtype = bool)
    bits = np.hstack(([0], bits, [0]))
    runs = np.where(bits[1:] != bits[:-1])[0]
    return list(np.reshape(runs, (2, -1), order = 'F').T)
