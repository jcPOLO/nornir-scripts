import tasks
from helpers import check_directory
from nornir.core.inventory import ConnectionOptions
from nornir.core.filter import F

PLATFORM = ['ios', 'huawei']


def get_templates(templates) -> list:
    result = []
    for template in templates:
        answer = input(f'{template.prompt}\n')
        if answer == 'y':
            template.answer = True
            result.append(template)
    return result


def config(nr) -> None:
    # record configuration in the device
    template = 'final.j2'
    tasks.basic_configuration(template, nr)


def session_log(nr) -> str:
    file = f'{nr.host}-{nr.host.hostname}-output.txt'
    path = './outputs/'
    filename = f'{path}{file}'
    check_directory(path)
    group_object = nr.host.groups.refs[0]
    group_object.connection_options["netmiko"].extras["session_log"] = filename
    return filename


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


def trunk_description(nr) -> None:
    data = tasks.get_interfaces_status(nr)
    interfaces = process_data_trunk(data)
    nr.host['interfaces'] = interfaces
    tasks.get_interface_description(interfaces, nr)


def filter_inventory(nr) -> object:
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
