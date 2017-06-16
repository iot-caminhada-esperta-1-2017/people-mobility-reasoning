import json
import logging
import datetime
import os.path
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty


LOCALS_FILE_NAME = 'bin/locals.json'


"""
  {
    "client_time": 1481817887000,
    "service_id": 2102,
    "data_values": {
      "latitude": -15.8187426,
      "longitude": -47.8938472
    },
    "tag": [
      "CaminhadaData"
    ],
    "server_time": 1496005131202
  },
"""


class MobilityReasoning:

    def __init__(self):
        self.__data = None

    def set_data(self, data):
        data_normalized = []
        for item in data:
            del(item['tag'])
            del(item['server_time'])

            item['client_time'] = int(item['client_time'])/1000

            if isinstance(item['data_values'], list):
                print "it IS list with %s values" % len(item['data_values'])
                print item['data_values']

                new_list = []
                for value in item['data_values']:
                    new_item = dict()
                    new_item['service_id'] = item['service_id']
                    new_item['client_time'] = item['client_time']
                    new_item['latitude'] = value['latitude']
                    new_item['longitude'] = value['longitude']
                    new_list.append(new_item)

                del(item)
                data_normalized = data_normalized + new_list

            else:
                item['latitude'] = item['data_values']['latitude']
                item['longitude'] = item['data_values']['longitude']

                del(item['data_values'])
                data_normalized.append(item)

        self.__data = data_normalized

    def persist_data(self):
        logging.debug("data")
        logging.debug(self.__data)

    def do_the_magic(self):
        self.persist_data()

        number_data = len(self.__data)
        print (number_data)

        it_ref = (self.__data[1]['latitude'], self.__data[1]['longitude']) #['data_values']
        print("Base id is %s" % self.__data[1]['service_id'])
        for item in self.__data:
            # time_str = datetime.datetime.fromtimestamp(int(item['client_time'])).strftime('%Y-%m-%d %H:%M:%S')
            cc = int(item['client_time'])
            tt = datetime.datetime.fromtimestamp(cc) #cc/1000
            time_str = tt.strftime('%Y-%m-%d %H:%M:%S')
            # if isinstance(item['data_values'], list):
            #     print "it IS list with %s values" % len(item['data_values'])
            #     print item['data_values']
            # else:
            #     print "is not list"
            #     print item['data_values']
            it_act = item['latitude'], item['longitude'] #['data_values']
            dist = self.get_distance(it_ref, it_act)
            print("Distance between %s and id %s %s is %s meters (at %s)" % (it_ref, item['service_id'], it_act, dist, time_str))

        # self.build_time_partitions()
        self.build_locals_list()
        for l in self.__locals:
            print l

    def get_location_description(self, place):
        geolocator = Nominatim()
        # location = geolocator.reverse("52.509669, 13.376294")
        str_coords = "%s, %s" % (place[0], place[1])
        location = geolocator.reverse(str_coords)
        # print "\n -----------"
        # print(location.address)
        # print((location.latitude, location.longitude))
        # print(location.raw)
        return location.address

    def get_distance(self, a, b):
        d = vincenty(a, b).meters
        return d

    def get_locals_from_file(self):
        if os.path.isfile(LOCALS_FILE_NAME):
            f = open(LOCALS_FILE_NAME, 'r')
            print f

            raw_data = f.read()
            print raw_data

            f.close()

            locals_from_file = json.loads(raw_data)
        else:
            locals_from_file = []

        return locals_from_file

    def save_locals_to_file(self, locals_list):
        f = open(LOCALS_FILE_NAME, 'w')
        json.dump(locals_list, f)
        f.close()

    def build_locals_list(self):
        locations = self.get_locals_from_file()
        for item_data in self.__data:
            tp = (item_data['latitude'], item_data['longitude']) #['data_values']
            rr= any(item for item in locations if item[0][0] == tp[0] and item[0][1] == tp[1])
            if not rr:
                desc = self.get_location_description(tp)
                locations.append((tp, desc))
        self.save_locals_to_file(locations)
        self.__locals = locations

    def build_time_partitions(self):
        five_minutes = datetime.timedelta(minutes=5)
        all_times = [item['client_time'] for item in self.__data]
        all_times.sort()
        time_part = []
        # for item in all_times:
        #     if
        #
        #     print item['client_time']
