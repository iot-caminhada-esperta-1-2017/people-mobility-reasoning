import json
import logging
import datetime
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

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

    def MobilityReasoning(self):
        self.__data = None

    def set_data(self, data):
        self.__data = data
        for item in self.__data:
            del(item['tag'])

    def persist_data(self):
        logging.debug("data")
        logging.debug(self.__data)

    def do_the_magic(self):
        self.persist_data()

        number_data = len(self.__data)
        print (number_data)

        it_ref = (self.__data[1]['data_values']['latitude'], self.__data[1]['data_values']['longitude'])
        print("Base id is %s" % self.__data[1]['service_id'])
        for item in self.__data:
            # time_str = datetime.datetime.fromtimestamp(int(item['client_time'])).strftime('%Y-%m-%d %H:%M:%S')
            cc = int(item['client_time'])
            tt = datetime.datetime.utcfromtimestamp(cc/1000)
            time_str = tt.strftime('%Y-%m-%d %H:%M:%S')
            it_act = item['data_values']['latitude'], item['data_values']['longitude']
            dist = self.get_distance(it_ref, it_act)
            print("Distance between %s and id %s %s is %s meters (at %s)" % (it_ref, item['service_id'], it_act, dist, time_str))


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
