from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
import getpass
from nornir.core.inventory import ConnectionOptions
import tasks
import os
import errno


CFG_FILE = 'config.yaml'
PLATFORM = ['ios', 'huawei']
EXCLUDED_VLANS = [1, 1002, 1003, 1004, 1005]


def change_to_telnet(nr) -> None:
    nr.host.port = 23
    nr.host.connection_options['netmiko'] = ConnectionOptions(
        extras={"device_type": 'cisco_ios_telnet', "session_log": session_log(nr)}
    )


def process_data_trunk(data) -> list:
    result = []
    for interface in data:

        if 'vlan' in interface.keys():
            interface['link'] = interface['vlan']
        if interface['link'] == 'trunk':
            result.append(interface['port'])

    return result
 

def filter_inventory(nr):
    devices = nr
    platform = input("Platform to filter: [ios/huawei]").lower()
    site = str(input("Cod Inm:"))

    if platform in PLATFORM:
        print(f'Filter by platform: { platform }')
        devices = nr.filter(F(platform=platform))
    else:
        print(f'All platforms selected.')
    if site in nr.inventory.groups:
        print(f'Filter by site: { site }')
        devices = nr.filter(F(site=site))
    else:
        print(f'All sites selected.')

    try:
        return devices
    except ValueError:
        print(f'Error: no filter applied')


def session_log(nr) -> str:
    file = f'{nr.host}-output.txt'
    path = './outputs/'
    filename = f'{path}{file}'

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    group_object = nr.host.groups.refs[0]
    group_object.connection_options["netmiko"].extras["session_log"] = filename
    return filename


def make_magic(nr) -> None:
    # 'pasar vlan 1099 por los trunks?'
    #
    # 'crear interface capa 3 vlan 1099?'
    #
    # 'cambiar descripcion a los trunks?'
    #
    # 'agregar configuracion snmp?'
    #
    # 'agregar configuracion tacacs?'
    #
    # 'agregar usuarios locales?'
    # makes a log file output for every device accessed
    session_log(nr)
    # backup config
    tasks.backup_config(nr)
    # issue the command in the device and gets the output as a dict
    # data = tasks.get_interfaces_status(nr)
    # takes all trunk interfaces
    # interfaces = process_data_trunk(data)
    # nr.host['interfaces'] = interfaces
    # tasks.get_interface_description(interfaces, nr)

    config(nr)


def config(nr) -> None:
    # record configuration in the device
    template = 'snmp.j2'
    tasks.basic_configuration(template, nr)


def main() -> None:
    username = input("Username:")
    password = getpass.getpass()

    nr = InitNornir(config_file=CFG_FILE)

    nr.inventory.defaults.password = password
    nr.inventory.defaults.username = username

    devices = filter_inventory(nr)

    result = devices.run(task=make_magic)
    print_result(result)
 
 
if __name__ == '__main__':
    main()
