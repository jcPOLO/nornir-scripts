from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
import getpass
from nornir.core.inventory import ConnectionOptions
import tasks
from bootstrap import load_inventory
from helpers import check_directory
from models.Template import Template
from models.TemplateManager import TemplateManager

CSV = 'inventario_extendido.csv'
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
    file = f'{nr.host}-{nr.host.hostname}-output.txt'
    path = './outputs/'
    filename = f'{path}{file}'
    check_directory(path)
    group_object = nr.host.groups.refs[0]
    group_object.connection_options["netmiko"].extras["session_log"] = filename
    return filename


def trunk_description(nr):
    data = tasks.get_interfaces_status(nr)
    interfaces = process_data_trunk(data)
    nr.host['interfaces'] = interfaces
    tasks.get_interface_description(interfaces, nr)


def make_magic(nr, if_trunk) -> None:
    # 'pasar vlan 1099 por los trunks?'
    #
    # 'crear interface capa 3 vlan 1099?'
    #
    # 'cambiar descripcion a los trunks?
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

    if if_trunk:
        trunk_description(nr)
    # issue the command in the device and gets the output as a dict
    # data = tasks.get_interfaces_status(nr)
    # takes all trunk interfaces
    # interfaces = process_data_trunk(data)
    # nr.host['interfaces'] = interfaces
    # tasks.get_interface_description(interfaces, nr)

    # config(nr)


def get_templates(templates) -> list:
    result = []
    for template in templates:
        answer = input(f'{template.prompt}\n')
        if answer == 'y':
            template.answer = True
            result.append(template)
    print(f'Applied these templates: {result}\n')
    return result


def config(nr) -> None:
    # record configuration in the device
    template = 'final.j2'
    tasks.basic_configuration(template, nr)


def main() -> None:
    username = input("Username:")
    password = getpass.getpass()

    try:
        load_inventory(CSV)
    except:
        print('no se ha podido crear el hosts.yaml')

    input("Files loaded. Press a key to continue...")

    nr = InitNornir(config_file=CFG_FILE)

    nr.inventory.defaults.password = password
    nr.inventory.defaults.username = username

    devices = filter_inventory(nr)

    if_trunk = False
    template_prompts = [
        'common.j2',
        'snmp.j2',
        'trunk_description.j2',
        # 'tacacs.j2',
        # 'vlan1099.j2',
        # 'ssh_rsa.j2',
    ]

    templates = [
        Template(template, template) for template in template_prompts
    ]

    templates = get_templates(templates)
    template_m = TemplateManager(templates)
    template_m.create_final_template('huawei')
    template_m.create_final_template('ios')
    for template in templates:
        if 'trunk' in template.prompt:
            if_trunk = True

    result = devices.run(task=make_magic, if_trunk=if_trunk)
    print_result(result)


if __name__ == '__main__':
    main()
