import requests
import json
import logging
import time


class HttpRaise2Call:
    CLIENT_LIST = 'client_list'
    CLIENT_REGISTER = 'client_register'
    SERVICE_LIST = 'service_list'
    SERVICE_REGISTER = 'service_service'
    DATA_LIST = 'data_list'
    DATA_REGISTER = 'data_register'

    def __init__(self, config):
        self.__config = {}
        self.__config["uri"] = config['uri']
        self.__config["method"] = config["http_method"]
        self.__config["base_uri"] = config["raise2_api_uri"]
        self.__config["timeout"] = config["timeout"]

    def call(self, data_to_sent):
        logging.info("trying to self register in the pretty way")
        url = "%s%s" % (self.__config["base_uri"], self.__config["uri"])
        headers = {'content-type': 'application/json', 'Accept': 'application/json'}
        req = None
        # if self.__config["method"] == 'get':
        #     req = requests.get(url, data=json.dumps(data_to_sent), headers=headers, timeout=self.__config["timeout"])
        # elif self.__config["method"] == 'post':
        try:
            req = requests.request(self.__config["method"], url, data=json.dumps(data_to_sent), headers=headers, timeout=self.__config["timeout"])
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            # sys.exit(1)
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            logging.error(err)
        except requests.exceptions.TooManyRedirects as err:
            # Tell the user their URL was bad and try a different one
            logging.error(err)
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            logging.error(e)
            # sys.exit(1)

        if req and req.json()['code'] is 200:
            logging.debug("> content: %s" % req.content)
            return req.content
        else:
            return None


class Raise2SelfRegister:
    # store all RAISe 2 configuration data
    __raise_config = []

    def __init__(self, config_data):
        self.__raise_config = config_data

    """
    # TODO: put this documentation in the pythonic way.

    global configuration is in the dictionary's root.
    specific configuration is in a sub dictionary into 'services' object.
    """
    def __get_config__(self, config_data):
        new_config_data = {}
        for k, v in self.__raise_config.iteritems():
            if not isinstance(v, dict):
                new_config_data[k] = v
            elif k == 'services':
                for ks, vs in v.iteritems():
                    if ks == config_data:
                        for kc, vc in vs.iteritems():
                            new_config_data[kc] = vc
        return new_config_data

    def __build_payload_data__(self, service_key):
        if service_key == HttpRaise2Call.CLIENT_REGISTER:
            # TODO: build the payload for real
            payload_data = {
                "name": "RaspberryPI",
                "chipset": "AMD790FX",
                "mac": "FF:FF:FF:FF:FF:FF",
                "serial": "C213",
                "processor": "IntelI3",
                "channel": "Ethernet",
                "client_time": time.time(),
                "tag": [
                    "cebola"
                ]
            }
        elif service_key == HttpRaise2Call.SERVICE_REGISTER:
            # TODO: build the payload for real
            payload_data = {
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
                    "tokenId": self.__token_id,
                    "client_time": time.time(),
                    "tag": [
                        "Cebola"
                    ]
                }
            }
        else:
            payload_data = {}
        return payload_data

    """
    registration workflow:
    POST devices
    POST services
    """
    def self_register(self):
        res = self.__do_service_call(HttpRaise2Call.CLIENT_REGISTER)
        if res:
            self.__token_id = res.json()['token_id']
            logging.info("client register worked")
            logging.debug("we got this token id: %s" % self.__token_id)
        else:
            logging.error("something's got wrong and we got no token")

        if res:
            self.__do_service_call(HttpRaise2Call.SERVICE_REGISTER)

    def __do_service_call(self, service_key):
        service_config = self.__get_config__(service_key)
        service_runner = HttpRaise2Call(service_config)
        payload_data = self.__build_payload_data__(service_key)
        return service_runner.call(payload_data)



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
