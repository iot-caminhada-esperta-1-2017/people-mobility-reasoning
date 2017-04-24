
import requests
import sys
import json
import socket
import threading
import os
import logging

class HttpRaise2Call:

    CLIENT_LIST      = 'client_list'
    CLIENT_REGISTER  = 'client_register'
    SERVICE_LIST     = 'service_list'
    SERVICE_REGISTER = 'service_service'
    DATA_LIST        = 'data_list'
    DATA_REGISTER    = 'data_register'

    def __init__(self, config):
        self.__config = {}
        # logging.debug("config is:")
        # logging.debug(config)
        self.__config["uri"] = config['uri']
        self.__config["method"] = config["http_method"]
        self.__config["base_uri"] = config["raise2_api_uri"]

    def call(self, data):
        logging.info("trying to self register in the pretty way")
        url = "%s%s" % (self.__config["base_uri"], self.__config["uri"])
        headers = {'content-type': 'application/json', 'Accept': 'application/json'}
        if self.__config["method"] == 'get':
            req = requests.get(url, data=json.dumps(data), headers=headers)
        elif self.__config["method"] == 'post':
            req = requests.post(url, data=json.dumps(data), headers=headers)
        else:
            req = None
        # logging.debug("> status_code %s" % req.status_code)
        logging.debug("> content: %s" % req.content)
        # logging.debug(req.content)

        if req.json()['code'] is 200:
            return req.content
        else:
            return None

        # if req.json()['code'] is 200:
        #     token_id = req.json()['token_id']
        #     logging.info("client register worked")
        #     logging.debug("we got this token id: %s" % token_id)
        #
        # elif req.json()['code'] in (400, 500):
        #     logging.info("something's got wrong and we got %s" % (req.json()['code']))


class Raise2SelfRegister:

    # store all RAISe 2 configuration data
    __raise_config = []

    def __init__(self, config_data):
        self.__raise_config = config_data
        # print "Data I know is:"
        # for k, v in self.__raise_config.iteritems():
        #     print k, v
        #     if isinstance(v, dict):
        #         print "e DICT"
        # print "and that's all."

    def __get_config__(self, config_data):
        new_config_data = {}
        for k, v in self.__raise_config.iteritems():
            if not isinstance(v, dict):
                new_config_data[k] = v
            elif k == 'services':
                # print "em DIC = services"
                for ks, vs in v.iteritems():
                    # print "rodando dentro do sub dict"
                    if ks == config_data:
                        # print "acei o meu config: ", config_data
                        for kc, vc in vs.iteritems():
                            new_config_data[kc] = vc

        # logging.debug("config filtrado:")
        # logging.debug(new_config_data)
        return new_config_data

    def __build_payload_data__(self, config_data):
        payload_data = {
            "name": "RaspberryPI",
            "chipset": "AMD790FX",
            "mac": "FF:FF:FF:FF:FF:FF",
            "serial": "C213",
            "processor": "IntelI3",
            "channel": "Ethernet",
            "client_time": 1317427200,
            "tag": [
                "cebola"
            ]
        }
        return payload_data

    def self_register(self):
        # registration workflow:

        # POST devices
        res = self.__do_service_call(HttpRaise2Call.CLIENT_REGISTER)
        if res:
            token_id = res.json()['token_id']
            logging.info("client register worked")
            logging.debug("we got this token id: %s" % token_id)
        else:
            # logging.info("something's got wrong and we got %s" % (res.json()['code']))
            logging.info("something's got wrong and we got no token")

        # POST services
        if res:
            self.__do_service_call(HttpRaise2Call.SERVICE_REGISTER)

        # res = self.__do_client_registry()
        # if res:
        #     token_id = res.json()['token_id']
        #     logging.info("client register worked")
        #     logging.debug("we got this token id: %s" % token_id)
        # else:
        #     # logging.info("something's got wrong and we got %s" % (res.json()['code']))
        #     logging.info("something's got wrong and we got")
        #
        # # POST services
        # self.__do_service_registry()

    def __do_service_call(self, service_key):
        service_config = self.__get_config__(service_key)
        # logging.debug("> service_config - trabalhado")
        # logging.debug(service_config)
        service_runner = HttpRaise2Call(service_config)
        payload_data = self.__build_payload_data__(service_key)
        return service_runner.call(payload_data)

    # def __do_client_registry(self):
    #     service_config = self.__get_config__(HttpRaise2Call.CLIENT_REGISTER)
    #     # logging.debug("> service_config - trabalhado")
    #     # logging.debug(service_config)
    #     client_register = HttpRaise2Call(service_config)
    #     payload_data = {
    #         "name": "RaspberryPI",
    #         "chipset": "AMD790FX",
    #         "mac": "FF:FF:FF:FF:FF:FF",
    #         "serial": "C213",
    #         "processor": "IntelI3",
    #         "channel": "Ethernet",
    #         "client_time": 1317427200,
    #         "tag": [
    #             "cebola"
    #         ]
    #     }
    #     return client_register.call(payload_data)

    # def __do_service_registry(self):
    #     service_register = HttpRaise2Call(HttpRaise2Call.SERVICE_REGISTER)
    #     payload_data = {
    #         "name": "RaspberryPI",
    #         "chipset": "AMD790FX",
    #         "mac": "FF:FF:FF:FF:FF:FF",
    #         "serial": "C213",
    #         "processor": "IntelI3",
    #         "channel": "Ethernet",
    #         "client_time": 1317427200,
    #         "tag": [
    #             "cebola"
    #         ]
    #     }
    #     return service_register.call(payload_data)






class Raise2SelfRegisterUglyWay:

    def __init__(self, config_data):
        pass

    def self_register(self):
        logging.info("trying to self register in the ugly way")

        url = 'http://raise.uiot.org/client/register/'
        payload = {
            "name": "RaspberryPI",
            "chipset": "AMD790FX",
            "mac": "FF:FF:FF:FF:FF:FF",
            "serial": "C213",
            "processor": "IntelI3",
            "channel": "Ethernet",
            "client_time": 1317427200,
            "tag": [
                "cebola"
            ]
        }
        headers = {'content-type': 'application/json'}
        device_request = requests.post(url, data=json.dumps(payload), headers=headers)
        logging.debug("> status_code %s" % device_request.status_code)
        logging.debug("> content")
        logging.debug(device_request.content)

        token_id = None

        if device_request.json()['code'] is 200:
            token_id = device_request.json()['token_id']
            logging.info("client register worked")
            logging.debug("we got this token id: %s" % token_id)

        elif device_request.json()['code'] in (400, 500):
            logging.info("something's got wrong and we got %s" % (device_request.json()['code']))

        if token_id:
            url = 'http://raise.uiot.org/service/register/'
            payload = {
                {
                    "services": [
                        {
                            "name": "Get temp",
                            "parameters": {
                                "example_parameter": "float"
                            },
                            "return_type": "float"
                        }
                    ],
                    "tokenId": token_id,
                    "client_time": 1317427200,
                    "tag": [
                        "Cebola"
                    ]
                }
            }
            headers = {'content-type': 'application/json'}
            device_request = requests.post(url, data=json.dumps(payload), headers=headers)
            logging.debug("> status_code %s" % device_request.status_code)
            logging.debug("> content")
            logging.debug(device_request.content)

            if device_request.json()['code'] is 200:
                pass

            elif device_request.json()['code'] in (400, 500):
                logging.info("something's got wrong and we got %s" % (device_request.json()['code']))

        else:
            logging.debug("There's no token.")

