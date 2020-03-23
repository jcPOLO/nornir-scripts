from tasks import backup_config, basic_configuration, get_interface_description, get_interfaces_status, get_tmp
from helpers import check_directory
from nornir.core.inventory import ConnectionOptions
from nornir.core.filter import F
from nornir.core import Nornir, Task
from typing import Dict, List

PLATFORM = ['ios', 'huawei', 'nxos']


def make_magic(task: Task, templates: str) -> None:
    # makes a log file output for every device accessed
    session_log(task)
    # backup config
    backup_config(task)
    # if option 2 or 3 is selected
    if 'trunk_description.j2' in templates or 'management.j2' in templates:
        print(f"{'trunk_description.j2' in templates} y {'management.j2' in templates}")
        trunk_description(task)
    # apply final template
    config(task)


def servet_bug(task: Task) -> None:
    # makes a log file output for every device accessed
    session_log(task)
    # backup config
    backup_config(task)
    get_tmp(task)


def config(task: Task) -> None:
    # record configuration in the device
    template = 'final.j2'
    basic_configuration(template, task)


def session_log(task: Task) -> str:
    file = f'{task.host}-{task.host.hostname}-output.txt'
    path = './outputs/'
    filename = f'{path}{file}'
    check_directory(path)
    group_object = task.host.groups.refs[0]
    group_object.connection_options["netmiko"].extras["session_log"] = filename
    return filename


def change_to_telnet(task: Task) -> None:
    task.host.port = 23
    task.host.connection_options['netmiko'] = ConnectionOptions(
        extras={"device_type": 'cisco_ios_telnet', "session_log": session_log(task)}
    )


def process_data_trunk(data: List) -> List[str]:
    result = []
    for interface in data:

        if 'vlan' in interface.keys():
            interface['link'] = interface['vlan']
        if interface['link'] == 'trunk':
            result.append(interface['port'])

    return result


def trunk_description(task: Task) -> None:
    data = get_interfaces_status(task)
    interfaces = process_data_trunk(data)
    task.host['interfaces']: Dict[str, str] = get_interface_description(interfaces, task)


def filter_inventory(nr: Nornir) -> Nornir:
    devices = nr
    platform = input("Platform to filter: [ios/huawei/nxos]").lower()
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
