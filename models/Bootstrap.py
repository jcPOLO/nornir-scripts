import configparser
import csv
import yaml
from helpers import get_platforms, is_ip, check_directory
from typing import Dict


class Bootstrap(object):

    def __init__(self, ini_file='.global.ini', csv_file='inventory.csv', **kwargs):

        self.ini_file = ini_file
        self.csv_file = csv_file
        self.load_inventory()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_ini_vars(self) -> configparser:
        try:
            config = configparser.RawConfigParser()
            config.read(self.ini_file)
            return config
        except Exception as e:
            raise e

    def get_config_vars(self) -> dict:
        try:
            config = configparser.RawConfigParser()
            config.read(self.ini_file)
            r = config
            return dict(r['GLOBAL'])
        except Exception as e:
            raise e

    # Return a dictionary from imported csv file
    def import_inventory_file(self) -> dict:
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

            with open(self.csv_file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                # next(csv_reader)  # The first line is the header

                for row in csv_reader:

                    site_code = row[0]
                    ip = row[5]
                    mask = row[6]
                    current_dg = row[7]
                    new_dg = row[8]

                    hostname = row[2] if is_ip(row[2]) else None
                    host = row[1].replace(" ", "_") or None
                    platform = row[3].lower().replace(" ", "_") if row[3].lower().replace(" ", "_") in platforms else None
                    # model = row[3].replace(" ", "_") or None
                    # serial = row[7].replace(" ", "_") or None
                    is_telnet = 't' in row[4].lower() and 's' not in row[4].lower()

                    # remove duplicated hostname
                    if None not in (hostname, host, platform) and host not in result.keys():
                        result[host] = {
                            'hostname': hostname,
                            'platform': platform,
                            'groups': [
                                'ios_telnet' if is_telnet and platform == 'ios' else platform
                            ],
                            'data': {
                                'site_code': site_code,
                                'model': platform,
                                # 'serial': serial,
                                'ip': ip,
                                'mask': mask,
                                'current_dg': current_dg,
                                'new_dg': new_dg,
                                'role': {}
                            }

                        }
                        if is_telnet and platform == 'ios':
                            result[host]['port'] = 23

            return result
        except Exception as e:
            print(platforms)
            raise e

    def load_inventory(self) -> None:
        self.create_hosts_yaml(self.import_inventory_file())

    @staticmethod
    def create_hosts_yaml(d: Dict) -> None:
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
