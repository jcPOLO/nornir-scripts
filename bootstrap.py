import configparser
import csv
from helpers import is_ip, check_directory
import yaml


def get_ini_vars() -> dict:
    config = configparser.RawConfigParser()
    config.read('.global.ini')
    r = config
    return dict(r['GLOBAL'])


# Return a dictionary from imported csv file
def import_inventory_file(f):
    result = {}
    with open(f, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # next(csv_reader)  # The first line is the header

        for row in csv_reader:

            ip = row[0] if is_ip(row[0]) else '0.0.0.0'
            host = row[1].replace(" ", "_")
            model = row[2].lower().replace(" ", "_")

            if host and host not in result.keys():
                result[host] = {
                    'hostname': ip,
                    'platform': model,
                    'groups': [
                        model
                    ],
                }

    if not result:
        raise ValueError('{result} empty for import_inventory_file"')
    return result


def create_hosts_yaml(d: dict) -> None:
    file = 'hosts.yaml'
    path = './inventory/'
    filename = f'{path}{file}'
    yml = yaml.dump(d)

    check_directory(path)

    with open(filename, 'w') as f:
        f.write(yml)


def load_inventory(f):
    d = import_inventory_file(f)
    create_hosts_yaml(d)
