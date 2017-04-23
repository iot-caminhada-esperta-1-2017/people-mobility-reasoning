
import json


def get_dict_from_file(file_name):

    #TODO: check if the file exists

    #TODO: protect parse exceptions
    with open(file_name) as data_file:
        data = json.load(data_file)

    return data



if __name__ == '__main__':
    pass
