from network.wfm_network_interface import WFMInterface
from schedule_manager import ScheduleManager
from utils import *
import time
import json
import re
import configparser
import numpy as np
import httpx

print('Initializing...')
config = configparser.ConfigParser()
config.read('config.ini')
log_file = open(config['logging']['log_file'], 'w+')

def start_interface(interface, config):
    print('VTObot is logging in...')
    r = interface.login(config['login']['username'], config['login']['password'])
    print('Login : {}'.format(r))

def set_agent_schedule(interface, schedule_manager, config):
    print('Querying agent schedule...')
    r, schedule = interface.query_agent_schedule()
    print('Query : {}'.format(r))

    schedule_slots = []
    match_string = '[0-9]+:[0-9]{2} [A-Za-z]{2}'
    for schedule_item in schedule:
        name = schedule_item[0]
        times = re.findall(match_string, schedule_item[1])
        start_time = libtime_to_clearlink(time.strptime(times[0], '%I:%M %p'))
        end_time = libtime_to_clearlink(time.strptime(times[1], '%I:%M %p'))
        schedule_slots.append({
            'name' : name,
            'start_time' : start_time,
            'end_time' : end_time
        })

    for slot in schedule_slots:
        ScheduleManager.set_slot(slot, schedule_manager.agent_schedule)

    desired_schedule = json.loads(config['schedule']['prefered_schedule'])
    for slot in desired_schedule:
        ScheduleManager.set_slot(slot, schedule_manager.desired_schedule)

    if config.getboolean('logging', 'log_schedule'):
        log_file.write('Agent Schedule:\n')
        log_file.write(np.array2string(schedule_manager.agent_schedule))
        log_file.write('\n')
        log_file.write('Desired Schedule:\n')
        log_file.write(np.array2string(schedule_manager.desired_schedule))
        log_file.write('\n')
        log_file.flush()

    print('Agent schedule saved')

def vto_step(interface, schedule_manager, config):
    print('Checking for VTO..    ', end = '\r')
    posted_slots = interface.query_vto()
    desired_requests = schedule_manager.generate_schedule_requests(posted_slots)
    if len(desired_requests) == 0: print('No desired slots found', end = '\r')
    else: print('Requesting VTO!      ')
    for desired_request in desired_requests:
        response = interface.request_vto(desired_request['oid'], desired_request['start_time'], desired_request['end_time'])
        if response.status_code == 200:
            j = json.loads(response.text)
            if j['messages'][0].lower() == 'the status of your request is approved':
                print('VTO Recieved!         ')
                ScheduleManager.set_slot(desired_request, schedule_manager.agent_schedule)
            else:
                pass
        if config.getboolean('logging', 'log_requests'):
            log_file.write('Time : {}\n'.format(time.localtime()))
            log_file.write('Request : ' + json.dumps(desired_request))
            log_file.write('\n')
            log_file.write('Response : ' + response.text)
            log_file.write('\n')
            log_file.flush()

interface = WFMInterface()
schedule_manager = ScheduleManager()

#time_out_length = 450 #7.5 minutes
#login_time = time.time()
start_interface(interface, config)
set_agent_schedule(interface, schedule_manager, config)

if config.getboolean('logging', 'log_requests'):
    log_file.write('Requests:\n')
    log_file.flush()

print('Starting VTO search...')
running = True
while running:
    try:
        vto_step(interface, schedule_manager, config)
    except (httpx.RemoteProtocolError, httpx.ReadTimeout):
        print('An error has occured...')
        interface = WFMInterface()
        start_interface(interface, config)
        time.sleep(5)

    #if time.time() > (time_out_length + login_time):
    #    print('Connection time out')
    #    interface = WFMInterface()
    #    start_interface(interface, config)

    time.sleep(1)
