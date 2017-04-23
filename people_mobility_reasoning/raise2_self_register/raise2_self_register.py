
import requests
import sys
import json
import socket
import threading
import os
import logging


class Raise2SelfRegister:

    # store all RAISe 2 configuration data
    __raise_config = []


    def __init__(self, config_data):
        self.__raise_config = config_data


    def self_register(self):
        print "Data I know is:"

        for k, v in self.__raise_config.iteritems():
            print k, v
            if isinstance(v, dict):
                print "e DICT"
        print "and that's all."

        # registration workflow:
        # POST devices
        # POST services


    def __http_call(self):
        mcall = HttpCall()



    def register_ugly_way(self):
        url = 'http://raise.uiot.org/client/register/'
        payload = {
            "name": "Raspberry PI",
            "chipset": "AMD 790FX",
            "mac": "FF:FF:FF:FF:FF:FF",
            "serial": "C213",
            "processor": "Intel I3",
            "channel": "Ethernet",
            "client_time": 1317427200,
            "tag": [
                "cebola"
            ]
        }
        headers = {'content-type': 'application/json'}
        device_request = requests.post(url, data=json.dumps(payload), headers=headers)
        print "> status_code", device_request.status_code
        print "> content"
        print device_request.content



class HttpCall:

    def __init__(self, config):
        self.__uri = config["uri"]
        self.__http_method = config["http_method"]
        self.__raise2_api_uri = config["raise2_api_uri"]


    def call(self):
        pass



    # def service_authenticator(self, splitted_message):
    #     service_auth = "http://raise.uiot.org/services?token=%s&name=%s&type=%s&scpdurl=%s&control_url=%s&event_sud_url=%s&refresh_rate=%s" % (
    #         self.token,
    #         splitted_message[3],
    #         "INTEGER",
    #         "raise.uiot.org",
    #         "raise.uiot.org",
    #         "Unecessary, please remove",
    #         splitted_message[5])
    #
    #     service_request = requests.post(service_auth)
    #
    #     if service_request.json()['code'] is 200:
    #         srvc_json = service_request.json()
    #         print srvc_json
    #         self.action_id = service_request.json()['action_id']
    #
    #         self.argument_list.append([splitted_message[3], splitted_message[0], srvc_json['item_id']])
    #
    #         self.argument_authenticator(splitted_message)
    #
    #     elif service_request.json()['code'] is 500:
    #         sys.exit()
