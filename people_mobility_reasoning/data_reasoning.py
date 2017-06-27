import json
import logging
import datetime
import os.path
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import time


LOCALS_FILE_NAME = 'bin/locals.json'
POSITIONS_FILE_NAME = 'bin/positions.json'
DATE_LIMIT = 1497967200
TWO_MINUTES = 120


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
        self.__locals = None
        self.__interactions = None

    def set_data(self, data):
        data_normalized = []
        for item in data:
            # print("service_id=%s, client_time=%s and server_time=%s" % (item['service_id'],
            #                                                             datetime.datetime.fromtimestamp(int(item['client_time']) / 1000).strftime('%Y-%m-%d %H:%M:%S'),
            #                                                             datetime.datetime.fromtimestamp(int(item['server_time']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            # ))
            if int(item['client_time']) <= DATE_LIMIT:
                print("This data (%s) is before the new version date (%s)" % (item, DATE_LIMIT))
            else:

                del(item['tag'])
                del(item['server_time'])
                item['time'] = int(item['client_time']) #/1000
                item['original_time'] = int(item['client_time'])
                del(item['client_time'])

                if isinstance(item['data_values'], list):
                    # print "it IS list with %s values" % len(item['data_values'])
                    # print item['data_values']
                    new_list = []
                    for value in item['data_values']:
                        if 'latLng' in value: #'latLng' in item['data_values']
                            new_item = dict()
                            new_item['service_id'] = item['service_id']
                            new_item['time'] = value['time'] #/1000
                            new_item['original_time'] = value['time']
                            new_item['latitude'] = value['latLng']['latitude']
                            new_item['longitude'] = value['latLng']['longitude']
                            new_list.append(new_item)

                        data_normalized = data_normalized + new_list

                    del(item)

                else:
                    item['latitude'] = item['data_values']['latitude']
                    item['longitude'] = item['data_values']['longitude']

                    del(item['data_values'])
                    data_normalized.append(item)

        self.__data = data_normalized

    def persist_data(self):
        logging.debug("data")
        logging.debug(self.__data)

        f = open(POSITIONS_FILE_NAME, 'w')
        json.dump(self.__data, f)
        f.close()


    def do_the_magic(self):
        self.persist_data()

        number_data = len(self.__data)
        print (number_data)

        # it_ref = (self.__data[1]['latitude'], self.__data[1]['longitude']) #['data_values']
        # print("Base id is %s" % self.__data[1]['service_id'])
        # for item in self.__data:
        #     # time_str = datetime.datetime.fromtimestamp(int(item['client_time'])).strftime('%Y-%m-%d %H:%M:%S')
        #     cc = int(item['client_time'])
        #     tt = datetime.datetime.fromtimestamp(cc) #cc/1000
        #     time_str = tt.strftime('%Y-%m-%d %H:%M:%S')
        #     # if isinstance(item['data_values'], list):
        #     #     print "it IS list with %s values" % len(item['data_values'])
        #     #     print item['data_values']
        #     # else:
        #     #     print "is not list"
        #     #     print item['data_values']
        #     it_act = item['latitude'], item['longitude'] #['data_values']
        #     dist = self.get_distance(it_ref, it_act)
        #     print("Distance between %s and id %s %s is %s meters (at %s)" % (it_ref, item['service_id'], it_act, dist, time_str))

        # self.build_time_partitions()
        self.build_locals_list()
        # for l in self.__locals:
        #     print l

        response_data = []
        self.build_interactions_list()
        for k, v in self.__interactions.iteritems():
            tt = datetime.datetime.fromtimestamp(int(k))
            time_str = tt.strftime('%Y-%m-%d %H:%M:%S')
            ids = [zzz['service_id'] for zzz in v]
            ids = list(set(ids))
            ids.sort()
            ponto = (v[0]['latitude'], v[0]['longitude'])
            ponto_list = []
            ponto_list.append(ponto[0])
            ponto_list.append(ponto[1])
            desc_local = [l[1] for l in self.__locals if l[0] == ponto_list]
            response_data.append({
                "time": k,
                "place": {
                    'latitude': ponto[0],
                    'longitude': ponto[1]
                },
                "quantity": len(ids)
            })
            # desc_local = self.__locals[ponto]
            print("%s:\nAt '%s' %s,\nthese devices were together: %s" % (time_str, desc_local[0], ponto, ids))

        return response_data

    def bla(self):
        return "(lat,long),xpessoas,tempo"

    def build_interactions_list(self):
        time_list = self.get_time_list()
        time_list = sorted(time_list)

        iteractions = dict()

        print "Beginning to reason about crowd"
        for t1 in time_list:
            persons = []

            locations = self.get_locations_of_a_time(t1)

            for item in locations:
                if item not in persons:
                    prox = [loc for loc in locations if (vincenty((item['latitude'], item['longitude']), (loc['latitude'], loc['longitude'])).meters <= 20) and (item['service_id'] != loc['service_id'])]
                    if prox:
                        persons += [item] + prox

            if persons:
                iteractions[t1] = persons

        print "Found %s groups of people" % len(iteractions)
        self.__interactions = iteractions

    def get_locations_of_a_time(self, location_time):
        locations = [item for item in self.__data if (item['time'] >= location_time-TWO_MINUTES) and (item['time'] <= location_time+TWO_MINUTES)]
        return locations

    def get_time_list(self):
        time_list = [item['time'] for item in self.__data]
        list2 = set(time_list)
        return list2

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
            # print raw_data

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
        i = 0
        for item_data in self.__data:
            tp = (item_data['latitude'], item_data['longitude'])
            rr= any(item for item in locations if item[0][0] == tp[0] and item[0][1] == tp[1])
            if not rr:
                i += 1
                if i == 3:
                    i = 0
                    print('pause to avoid service rejection')
                    self.save_locals_to_file(locations)
                    time.sleep(1)
                # desc = self.get_location_description(tp)
                desc = ''
                print tp, desc
                locations.append((tp, desc))
        self.save_locals_to_file(locations)
        self.__locals = locations

    # def build_time_partitions(self):
    #     five_minutes = datetime.timedelta(minutes=5)
    #     all_times = [item['time'] for item in self.__data]
    #     all_times.sort()
    #     time_part = []
    #     # for item in all_times:
    #     #     if
    #     #
    #     #     print item['time']
