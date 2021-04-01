from network.httpx_client_wrapper import FlexableCookiesClient
from bs4 import BeautifulSoup
import json

from datetime import date
import time

import random
from utils import *

vto_activity_oid = '8a81a18c4d01ed2e014d445ca41a0189'

class WFMInterface():
    def __init__(self, http2 = True):
        self.client = FlexableCookiesClient(http2 = http2)
        self.login_active = False

        self.default_headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
            'Connection' : 'keep-alive'
        }

        #Hidden variables
        self._recieved_vto_JSESSIONID = False
        self._recieved_schedule_JSESSIONID = False

    def login(self, username, password):
        '''Provides login credentials to the server, and recieves the approprate cookies'''
        login_payload = {
            'username' : username,
            'password' : password,
            'login' : 'Login'
        }

        #Recieve the AuthState variable required for a successful login attempt
        response = self.client.get('https://wfm.clearlink.com')

        #Parse the html response to find the hidden variable
        soup = BeautifulSoup(response.text, 'html.parser')
        login_payload['AuthState'] = soup.find('input', {'name' : 'AuthState'})['value']

        #Make a login post and recive an additional html file with SAMLResponse and RelayState hidden variables
        response = self.client.post('https://saml2.clearlink.com/saml2/module.php/core/loginuserpass.php?', data = login_payload)

        #Create the SAML payload
        saml_payload = {}
        soup = BeautifulSoup(response.text, 'html.parser')
        saml_payload['SAMLResponse'] = soup.find('input', {'name' : 'SAMLResponse'})['value']
        saml_payload['RelayState'] = soup.find('input', {'name' : 'RelayState'})['value']

        #Create our new liferay LFR_SESSION_STATE cookie (This uses the agent ID, which should be received from the network)
        self.client.cookies.set('LFR_SESSION_STATE_164960', str(int(time.time() * 1000)), secure = True)

        #Post the SAML payload back to the server, to establish the liferay LFR_SESSION_STATE_164960 and WFM csrf token cookies
        response = self.post_secure('https://wfm.clearlinkdata.com/', data = saml_payload, headers = self.default_headers)

        self.login_active = True

        return response

    #CURRENTLY NOT WORKING
    def clear_pending_requests(self, n_pending):
        '''Clears a specified number of pending requests and returns a list of responses'''
        assert self.login_active, 'Must call the login function of WFMInterface before calling query_slot'

        self.client.get('https://wfm.clearlinkdata.com/delegate/forwarderServlet/process.do?url=https%3A%2F%2Fwfm.clearlinkdata.com%3A443%2Fagent%2FscheduleViewerAction.mvc%3FsvtgST%3Dsvcrt%26lang%3Den_US&initpage=https://wfm.clearlinkdata.com:443/agent/sso.mvc&appid=wfm-agent')
        self.client.get('https://wfm.clearlinkdata.com/agent/scheduleViewerAction.mvc?svtgST=svcrt&lang=en_US')

        r = []
        for i in range(n_pending):
            r.append(self.client.get('https://wfm.clearlinkdata.com/agent/schChgRqstCancelPending.mvc?row=0'))

        return r

    def query_slot(self, slot_oid):
        '''Returns the number of available slots left for each portion of a time board posting'''
        assert self.login_active, 'Must call the login function of WFMInterface before calling query_slot'

        #Recieve a JSESSIONID cookie for making the final query, if necessary
        if not self._recieved_vto_JSESSIONID:
            #First request returns a 302 to route to second request, the second request requires cookies from the first, and we require the cookies from the second for our final request
            self.client.get('https://wfm.clearlinkdata.com/delegate/forwarderServlet/process.do?url=https://wfm.clearlinkdata.com/TV4/services/rs/system/config&initpage=https://wfm.clearlinkdata.com/TV4/services/rs/auth/platform/sso&appid=TV4')
            self.client.get('https://wfm.clearlinkdata.com/TV4/services/rs/system/config')

            self._recieved_vto_JSESSIONID = True

        raw_json = self.client.get('https://wfm.clearlinkdata.com/TV4/services/rs/timeboard/slotstatus?slotOid={}&locale=en_US&timeZone=America/Denver'.format(slot_oid))
        return json.loads(raw_json.text)

    def query_vto(self):
        '''Returns the currently posted vto in JSON format and handles the relevant machinery. In particular, we need to recieve a JSESSIONID for wfm.clearlinkdata.com/TV4 if necessary, and then query the approprate url'''
        assert self.login_active, 'Must call the login function of WFMInterface before calling query_vto'

        #Recieve a JSESSIONID cookie for making the final query, if necessary
        if not self._recieved_vto_JSESSIONID:
            #First request returns a 302 to route to second request, the second request requires cookies from the first, and we require the cookies from the second for our final request
            self.client.get('https://wfm.clearlinkdata.com/delegate/forwarderServlet/process.do?url=https://wfm.clearlinkdata.com/TV4/services/rs/system/config&initpage=https://wfm.clearlinkdata.com/TV4/services/rs/auth/platform/sso&appid=TV4')
            self.client.get('https://wfm.clearlinkdata.com/TV4/services/rs/system/config')

            self._recieved_vto_JSESSIONID = True

        #Return the VTO JSON data
        raw_json = self.client.get('https://wfm.clearlinkdata.com/TV4/services/rs/timeboard/agentslots?locale=en_US')

        #Process out only VTO
        slots = json.loads(raw_json.text)
        vto = []
        try:
            for slot in slots['slots']:
                if slot['activity']['name'].lower() == 'vto':
                    vto.append(slot)
        except KeyError:
            pass
        return vto

    def query_agent_schedule(self):
        '''Returns today's schedule for the agent currently logged into the WFMInterface.'''
        assert self.login_active, 'Must call the login function of WFMInterface before calling query_agent_schedule'
        #For who knows what reason, agent schedules are only exposed via html subdocuments loaded into iframes, so we will request and then parse the document for the daily schedule
        #Also, we have yet another 302 to navigate here
        if not self._recieved_schedule_JSESSIONID:
            self.client.get('https://wfm.clearlinkdata.com/delegate/forwarderServlet/process.do?url=https%3A%2F%2Fwfm.clearlinkdata.com%3A443%2Fagent%2FbuildDesktopAction.mvc%3Flang%3Den_US&initpage=https://wfm.clearlinkdata.com:443/agent/sso.mvc&appid=wfm-agent')
            self._recieved_schedule_JSESSIONID = True

        response = self.client.get('https://wfm.clearlinkdata.com/agent/buildDesktopAction.mvc?lang=en_US')
        #Grabbing the schedule section out of the html
        schedule_table = BeautifulSoup(response.text, 'html.parser').find('table', {'class' : 'agent-today-schedule'}).find('table', {'class' : 'today-schedule-daily-not-null'})

        schedule = []
        for schedule_item in schedule_table.find_all('tr'):
            schedule_item = schedule_item.find_all('td')
            #There is an empty item at the bottom of the table for some reason, and this way we will catch anything strange and avoid an IndexError
            if len(schedule_item) < 4:
                break
            #Add the schedule item and its type to the schedule list
            type = schedule_item[1].get_text()
            time = schedule_item[3].get_text()
            schedule.append((type, time))

        return response, schedule

    def request_vto(self, slot_oid, start_time, end_time, date = str(date.today())):
        #Figure out what the hell is happening here
        request_payload = {
            'activityCodeOid' : vto_activity_oid,
            'date' : date,
            'endTime' : end_time,
            'slotOid' : slot_oid,
            'startTime' : start_time,
            'localeParam' : 'en_US'
        }

        request_payload = json.dumps(request_payload).encode('utf8')

        headers = self.default_headers
        headers.update({
            'Origin' : 'https://wfm.clearlinkdata.com',
            'Referer' : 'https://wfm.clearlinkdata.com/group/webstation/time-board',
            'Accept' : '*/*',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'en-US;en,q=0.5',
            'Content-Length' : str(len(request_payload)),
            'Content-Type' : 'application/json; charset=UTF-8'
        })

        return self.post_secure('https://wfm.clearlinkdata.com/TV4/services/rs/timeboard/addactivity', data = request_payload, headers = self.default_headers)

    def post_secure(self, url, headers = {}, **kwargs):
        csrf_token = WFMInterface._generate_csrf_token()
        headers['wfm_csrf_token'] = csrf_token

        self.client.cookies.set('wfm_csrf_token', csrf_token, domain = 'wfm.clearlinkdata.com', secure = True)
        return self.client.post(url, headers = headers, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self):
        self.client.close()

    def _generate_csrf_token():
        n = random.random()
        csrf = base_n(int(n * (32 ** 12)), 32)[-9 : -1]
        return csrf
