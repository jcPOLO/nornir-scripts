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
def import_inventory_file(f: str) -> dict:
    """
    host: <name>
        hostname: <ip>
        platform: <ios|huawei>
        groups:
            - <ios_telnet|ios|huawei>
            - [site code|role type|...]
        [
        data:
            site: '<site code>'
            ip: <migration ip>
        ]

    """
    result = {}
    with open(f, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # next(csv_reader)  # The first line is the header

        for row in csv_reader:

            hostname = row[0] if is_ip(row[0]) else '0.0.0.0'
            host = row[3].replace(" ", "_")
            model = row[4].lower().replace(" ", "_")
            is_telnet = 't' in row[1].lower()

            if host and host not in result.keys():
                result[host] = {
                    'hostname': hostname,
                    'platform': model,
                    'groups': [
                        'ios_telnet' if is_telnet and model == 'ios' else model
                    ],
                }
                if is_telnet and model == 'ios':
                    result[host]['port'] = 23

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


def load_inventory(f: str) -> None:
    d = import_inventory_file(f)
    create_hosts_yaml(d)
