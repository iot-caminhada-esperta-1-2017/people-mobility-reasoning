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

    def call(self, **params): #data_to_sent
        # logging.info("----> trying to call RAISe")

        query_string = ''
        if 'query' in params and params['query']:
            query_string = '?' + params['query']

        if 'payload' in params:
            data_to_sent = params['payload']
        else:
            data_to_sent = ''

        url = "%s%s%s" % (self.__config["base_uri"], self.__config["uri"], query_string)
        headers = {'Accept': 'application/json'}
        if data_to_sent:
            headers['content-type'] = 'application/json'
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
        if code_result == '200' or code_result == 200:
            return req.content
        else:
            return None


class Raise2Handler(object):
    # store all RAISe 2 configuration data
    __raise_config = []

    def __init__(self, config_data):
        self.__raise_config = config_data
        self._token_id = None
        self._service_id = None

    def get_token_id(self):
        return self._token_id

    def set_token_id(self, token_id):
        self._token_id = token_id

    def get_service_id(self):
        return self._service_id

    def set_service_id(self, service_id):
        self._service_id = service_id

    """
    # TODO put this documentation in the pythonic way.

    global configuration is in the dictionary's root.
    specific configuration is in a sub dictionary into 'services' object.
    """
    def _get_config__(self, config_data):
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

    def _build_payload_data__(self, service_key):
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
                    "tokenId": self.get_token_id(),
                    "client_time": time.time(),
                    "tag": [
                        "topicos_1", "TrafegoPessoas", "simulacao", "teste_conexao"
                ]
            }
        elif service_key == HttpRaise2Call.DATA_REGISTER:
            # TODO: build the payload for real
            payload_data = {

                    "token": self.get_token_id(),
                    "client_time": time.time(),
                    "tag": [
                        "topicos_1", "TrafegoPessoas", "simulacao", "teste_conexao"
                    ],
                    "data": [
                        {
                            "service_id": self.get_service_id(),
                            "data_values": {
                                "info": "I know nothing yet but I'll learn something soon."
                            }
                        }
                    ]
            }
        else:
            payload_data = {}
        return payload_data

    def _do_service_call(self, service_key, **params):
        service_config = self._get_config__(service_key)
        service_runner = HttpRaise2Call(service_config)

        query_string = ''
        if 'query' in params and params['query']:
            query_string = params['query']

        payload_data = self._build_payload_data__(service_key)
        # query_string = self._build_query_string(service_key)
        return service_runner.call(query=query_string, payload=payload_data)


class Raise2SelfRegister(Raise2Handler):

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
                    return True
                    break
                elif i > 3:
                    return False
                    break
        else:
            return False

    def __do_register_client(self):
        res = self._do_service_call(HttpRaise2Call.CLIENT_REGISTER)
        if res:
            json_res = json.loads(res)
            self.set_token_id(json_res['tokenId'])
            logging.debug("we got this token id: %s" % self.get_token_id())
            return True
        else:
            logging.error("something's got wrong and we got no token")
            return False

    def __do_register_service(self):
        res = self._do_service_call(HttpRaise2Call.SERVICE_REGISTER)
        if res:
            services_registered = json.loads(res)
            logging.debug(services_registered)
            #TODO tornar o codigo dinamico para o caso de varios servicos
            self.set_service_id(services_registered['services'][0]['service_id'])
            return True
        else:
            logging.error("something's got wrong when we tried to register our service")
            return False


class Raise2DataHandler(Raise2Handler):

    def __do_register_data(self):

        res = self._do_service_call(HttpRaise2Call.DATA_REGISTER)
        if res:
            data_registered = json.loads(res)
            logging.debug(data_registered)
            return True
        else:
            logging.error("something's got wrong when we tried to register data at our service")
            return False

    def __do_list_data(self):
        res = self._do_service_call(HttpRaise2Call.DATA_LIST, query=self._build_query_string())
        if res:
            data = json.loads(res)
            logging.debug("data from RAISe: %s" % data)
            if data['code'] == 200:
                return data['values']
            else:
                return None
        else:
            logging.error("something's got wrong when we tried to register data at our service")
            return None

    def send_fake_data(self):
        return self.__do_register_data()

    def get_data_pos(self):
        res = self.__do_list_data()
        logging.debug("There's %s position data" % len(res))
        return res

    #TODO check if the service_key parameter is necessary
    def _build_query_string(self):
        return "tokenId=%s&tag=%s" % (self.get_token_id(), 'CaminhadaData') #, self.get_service_id()
