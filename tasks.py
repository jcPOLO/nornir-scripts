from nornir.core import Task
from nornir.plugins.tasks import networking, text
from models import huawei, ios
from bootstrap import get_ini_vars
from helpers import check_directory
from typing import List, Dict
import logging


def get_interfaces_status(task: Task) -> List[Dict[str, str]]:
    r = ''
    if task.host.platform == 'huawei':
        r = huawei.get_interfaces_status(task)
    if task.host.platform == 'ios' or task.host.platform == 'nxos':
        r = ios.get_interfaces_status(task)

    return r


def basic_configuration(template: str, task: Task) -> None:
    ini_vars = get_ini_vars()
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name=f"PLANTILLA A APLICAR PARA {task.host.platform}",
                 template=template,
                 path=f"templates/{task.host.platform}",
                 ini_vars=ini_vars,
                 nr=task,
                 severity_level=logging.DEBUG,
                 )
    # Save the compiled configuration into a host variable
    task.host["config"] = r.result
    # Send final configuration template using netmiko
    task.run(task=networking.netmiko_send_config,
             name=f"APLICAR PLANTILLA PARA {task.host.platform}",
             config_commands=task.host["config"].splitlines(),
             # severity_level=logging.DEBUG,
             )


def backup_config(task: Task) -> None:
    r = ''
    file = f'{task.host}-{task.host.hostname}.cfg'
    path = './backups/'
    filename = f'{path}{file}'

    if task.host.platform == 'huawei':
        r = huawei.get_config(task)
    if task.host.platform == 'ios' or task.host.platform == 'nxos':
        r = ios.get_config(task)

    check_directory(filename)
    with open(filename, 'a') as f:
        f.write(r)


def get_interface_description(interfaces: List, task: Task) -> List[Dict[str, str]]:
    r = ''
    result = []
    for interface in interfaces:
        if task.host.platform == 'huawei':
            r = huawei.get_interface_description(interface, task)
        if task.host.platform == 'ios' or task.host.platform == 'nxos':
            r = ios.get_interface_description(interface, task)

        if 'description' in r[0]:
            # do not duplicate interface name in description if it already exists
            if interface in r[0]['description']:
                r[0]['description'] = r[0]['description'].replace(interface, '').strip()
            port_dict = {
                'interface': interface,
                'description': r[0]['description'],
            }
        else:
            port_dict = {
                'interface': interface,
                'description': '',
            }
        result.append(port_dict)

    return result


def get_tmp(task: Task):
    r = task.run(task=networking.netmiko_send_command,
                 name='MUESTRA EL USO DE MEMORIA PARA TMP DE STACKS',
                 command_string=f'show platform software mount switch active R0 | i ^tmpfs.*\/tmp ',
                 use_textfsm=False
                 ).result
