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
        # logging.info("trying to self register in the pretty way")
        url = "%s%s" % (self.__config["base_uri"], self.__config["uri"])
        headers = {'content-type': 'application/json', 'Accept': 'application/json'}
        req = None
        try:
            p = json.dumps(data_to_sent)
            logging.debug("{} {} headers={} payload={}".format(self.__config["method"], url, headers, p))
            req = requests.request(self.__config["method"], url, data=p, headers=headers, timeout=self.__config["timeout"]) #p=json.dumps(data_to_sent)
            # logging.debug(req.content)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            return None
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            logging.error(err)
            return None
        except requests.exceptions.TooManyRedirects as err:
            # Tell the user their URL was bad and try a different one
            logging.error(err)
            return None
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            logging.error(e)

        # logging.debug(req.content)
        # logging.debug("JSON")
        # logging.debug(req.json()['code'])
#        if req and req.json()['code'] is 200:
        code_result = req.json()['code']
        if code_result == '200':
            # logging.debug("> content: %s" % req.content)
            return req.content
        else:
            return None


class Raise2SelfRegister:
    # store all RAISe 2 configuration data
    __raise_config = []

    def __init__(self, config_data):
        self.__raise_config = config_data

    """
    # TODO put this documentation in the pythonic way.

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
                "name": "PeopleMobilityReasoning",
                "chipset": "VM",
                "mac": "FF:FF:FF:FF:FF:FF",
                "serial": "D123",
                "processor": "VMs",
                "channel": "Ethernet",
                "client_time": time.time(),
                "tag": [
                    "topicos_1", "TrafegoPessoas", "simulacao", "teste_conexao"
                ]
            }
        elif service_key == HttpRaise2Call.SERVICE_REGISTER:
            # TODO: build the payload for real
            payload_data = {
                    "services": [
                        {
                            "name": "PeopleMobilityReasoning",
                            "parameters": {
                               # "example_parameter": "float"
                            },
                            "return_type": "string"
                        }
                    ],
                    "tokenId": self.__token_id,
                    "client_time": time.time(),
                    "tag": [
                        "topicos_1", "TrafegoPessoas", "simulacao", "teste_conexao"
                ]
            }
        elif service_key == HttpRaise2Call.DATA_REGISTER:
            # TODO: build the payload for real
            payload_data = {

                    "token": self.__token_id,
                    "client_time": time.time(),
                    "tag": [
                        "topicos_1", "TrafegoPessoas", "simulacao", "teste_conexao"
                    ],
                    "data": [
                        {
                            "service_id": self.__service_id,
                            "data_values": {
                                "info": "I know nothing yet but I'll learn something soon."
                            }
                        }
                    ]

                #     "services": [
                #         {
                #             "name": "PeopleMobilityReasoning",
                #             "parameters": {
                #                # "example_parameter": "float"
                #             },
                #             "return_type": "string"
                #         }
                #     ],
                #     "tokenId": self.__token_id,
                #     "client_time": time.time(),
                #     "tag": [
                #         "topicos_1", "TrafegoPessoas"
                # ]
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
        if self.__do_register_client():
            i = 0
            while True:
                i += 1
                if i > 1:
                    logging.info("MAIS UMA TENTANTIVA {}".format(i))
                n = self.__do_register_service()
                if n:
                    self.__do_register_data()

                    self.__do_list_data()
                    break
                elif i > 3:
                    break

    def __do_service_call(self, service_key):
        service_config = self.__get_config__(service_key)
        service_runner = HttpRaise2Call(service_config)
        payload_data = self.__build_payload_data__(service_key)
        return service_runner.call(payload_data)

    def __do_register_client(self):
        res = self.__do_service_call(HttpRaise2Call.CLIENT_REGISTER)
        if res:
            json_res = json.loads(res)
            self.__token_id = json_res['tokenId']
            logging.debug("we got this token id: %s" % self.__token_id)
            return True
        else:
            logging.error("something's got wrong and we got no token")
            return False

    def __do_register_service(self):
        res = self.__do_service_call(HttpRaise2Call.SERVICE_REGISTER)
        if res:
            services_registered = json.loads(res)
            logging.debug(services_registered)
            #TODO tornar o codigo dinamico para o caso de varios servicos
            self.__service_id = services_registered['services'][0]['service_id']
            return True
        else:
            logging.error("something's got wrong when we tried to register our service")
            return False

    def __do_register_data(self):
        res = self.__do_service_call(HttpRaise2Call.DATA_REGISTER)
        if res:
            data_registered = json.loads(res)
            logging.debug(data_registered)
            return True
        else:
            logging.error("something's got wrong when we tried to register data at our service")
            return False

    def __do_list_data(self):
        res = self.__do_service_call(HttpRaise2Call.DATA_LIST)
        if res:
            data = json.loads(res)
            logging.debug("data from RAISe: %s" % data)
            return True
        else:
            logging.error("something's got wrong when we tried to register data at our service")
            return False
