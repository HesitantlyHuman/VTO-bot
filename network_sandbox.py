from network.wfm_network_interface import WFMInterface
from schedule_manager import ScheduleManager
from utils import *
import time
import json
import re
import configparser
import numpy as np

print('Initializing...')
config = configparser.ConfigParser()
config.read('config.ini')

interface = WFMInterface()
print('VTObot is logging in...')
r = interface.login(config['login']['username'], config['login']['password'])
print('Login : {}'.format(r))

r = interface.clear_pending_requests(1)

for res in r:
    print(res)
    print(res.text)
