from nornir.core import Task
from nornir.plugins.tasks import networking, text
from models import huawei, ios
from bootstrap import get_ini_vars
from helpers import check_directory
import logging


def get_interfaces_status(task: Task) -> list:
    r = ''
    if task.host.platform == 'huawei':
        r = huawei.get_interfaces_status(task)
    if task.host.platform == 'ios':
        r = ios.get_interfaces_status(task)

    return r


def basic_configuration(template: str, task: Task) -> None:

    ini_vars = get_ini_vars()
    # Transform inventory data to configuration via a template file
    # print(f'... applying config template for host: { task.host } ...\n')
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

    # Deploy that configuration to the device using NAPALM
    # print(f'... write mem config for { task.host } ...\n')
    task.run(task=networking.netmiko_send_config,
             name=f"APLICAR PLANTILLA PARA {task.host.platform}",
             config_commands=task.host["config"].splitlines(),
             )


def backup_config(task: Task) -> None:
    r = ''
    file = f'{task.host}-{task.host.hostname}.cfg'
    path = './backups/'
    filename = f'{path}{file}'

    if task.host.platform == 'huawei':
        r = huawei.get_config(task)
    if task.host.platform == 'ios':
        try:
            ssh = True
            r = ios.get_config(task)
        except ConnectionError:
            # print(f'...SSH not working for {task.host} IP {task.host.hostname} , closing connection attempt...')
            ssh = False
            pass
            try:
                task.host.close_connections()
            except ValueError:
                # print('...trying TELNET instead....')
                pass

        if not ssh:
            # task.host.connection_options['netmiko'] = ConnectionOptions(
            #     extras={"device_type": 'cisco_ios_telnet'})
            from main_functions import change_to_telnet
            change_to_telnet(task)
            # print(f'Telnet {task.host} IP {task.host.hostname} ...')
            try:
                r = ios.get_config(task)
            except ConnectionError:
                # print(f'Unable to connect to {task.host} - {task.host.hostname} by telnet\n')
                pass

    # print(f'Saving config for {task.host} to file {filename}')
    check_directory(filename)
    with open(filename, 'a') as f:
        f.write(r)


def get_interface_description(interfaces: list, task: Task) -> list:
    r = ''
    result = []
    for interface in interfaces:
        if task.host.platform == 'huawei':
            r = huawei.get_interface_description(interface, task)
        if task.host.platform == 'ios':
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
