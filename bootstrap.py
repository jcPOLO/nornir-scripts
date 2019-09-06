import configparser
import csv
from helpers import is_ip, check_directory, get_platforms
import yaml


def get_ini_vars() -> configparser:
    try:
        config = configparser.RawConfigParser()
        config.read('.global.ini')
        return config
    except Exception as e:
        raise e


# Return a dictionary from imported csv file
def import_inventory_file(f: str = 'inventory.csv') -> dict:
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
    platforms = get_platforms()
    try:
        result = {}

        with open(f, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            # next(csv_reader)  # The first line is the header

            for row in csv_reader:

                hostname = row[1] if is_ip(row[1]) else None
                host = row[4].replace(" ", "_") or None
                model = row[5].lower().replace(" ", "_") if row[5].lower().replace(" ", "_") in platforms else None
                is_telnet = 't' in row[2].lower() and 's' not in row[2].lower()

                # remove duplicated hostnames
                if None not in (hostname, host, model) and host not in result.keys():
                    result[host] = {
                        'hostname': hostname,
                        'platform': model,
                        'groups': [
                            'ios_telnet' if is_telnet and model == 'ios' else model
                        ],
                    }
                    if is_telnet and model == 'ios':
                        result[host]['port'] = 23

        return result
    except Exception as e:
        print(platforms)
        raise e


def create_hosts_yaml(d: dict) -> None:
    try:
        file = 'hosts.yaml'
        path = './inventory/'
        filename = f'{path}{file}'
        yml = yaml.dump(d)

        check_directory(path)

        with open(filename, 'w') as f:
            f.write(yml)
    except Exception as e:
        raise e


def load_inventory(csv_file: str = 'inventory.csv') -> None:
    if csv_file is None:
        csv_file = 'inventory.csv'
    d = import_inventory_file(csv_file)
    create_hosts_yaml(d)
