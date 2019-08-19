from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
import getpass
from nornir.core.inventory import ConnectionOptions


CFG_FILE = 'config.yaml'
PLATFORM = ['cisco', 'huawei']
 
 
def get_interfaces_status(nr):
    r = ''
    if nr.host.platform == 'huawei':
        print(f'... doing display port vlan for Huawei host: {nr.host} ...\n')
        r = nr.run(task=networking.netmiko_send_command,
                   name='MUESTRA EL ESTADO DE LOS PUERTOS',
                   command_string='display port vlan',
                   use_textfsm=True
                   ).result
        process_data_trunk(r, nr)
    if nr.host.platform == 'ios':
        print(f'... doing show interface status for Cisco host: {nr.host} ...\n')
        try:
            ssh = True
            r = nr.run(task=networking.netmiko_send_command,
                       name='MUESTRA EL ESTADO DE LOS PUERTOS',
                       command_string='show interfaces status',
                       use_textfsm=True
                       ).result
        except:
            ssh = False
            try:
                nr.host.close_connections()
            except ValueError:
                pass
        if not ssh:
            change_to_telnet(nr.host)
            r = nr.run(task=networking.netmiko_send_command,
                       name='MUESTRA EL ESTADO DE LOS PUERTOS',
                       command_string='show interfaces status',
                       use_textfsm=True
                       ).result

    process_data_trunk(r, nr)


def change_to_telnet(host):
    host.port = 23
    host.connection_options['netmiko'] = ConnectionOptions(
        extras={"device_type": 'cisco_ios_telnet'}
    )


def process_data_trunk(data, nr):
    result = []
    for interface in data:

        if 'vlan' in interface.keys():
            interface['link'] = interface['vlan']
        if interface['link'] == 'trunk':
            # trunk_dict = {
            #     'interface': interface['port'],
            #     'status': interface['status']
            # }
            result.append(interface['port'])
 
    nr.run(task=basic_configuration(result, nr))
 
 
def basic_configuration(port, nr):

    # Transform inventory data to configuration via a template file
    print(f'... applying config template for host: { nr.host } ...\n')
    r = nr.run(task=text.template_file,
               name=f"APLICAR PLANTILLA LOTE 7 PARA {nr.host.platform}",
               template="snmp.j2",
               path=f"templates/{nr.host.platform}",
               port=port,
               nr=nr)

    # Save the compiled configuration into a host variable
    nr.host["config"] = r.result
 
    # Deploy that configuration to the device using NAPALM
    print(f'... write mem config for { nr.host } ...\n')
    nr.run(task=networking.netmiko_send_config,
           config_commands=nr.host["config"].splitlines())
 

def filter_inventory(nr):
    devices = ''
    platform = input("Platform to filter: [ios/huawei]").lower()
    site = str(input("Cod Inm with underscore prefix to filter by [i.e _0094}:"))

    if platform in PLATFORM:
        print(f'Filter by platform: { platform }')
        devices = nr.filter(F(platform=platform))
    else:
        print(f'Does not exist: { platform }.')
    if site in nr.inventory.groups:
        print(f'Filter by site: { site }')
        devices = nr.filter(F(site=site))
    else:
        print(f'Does not exist: { site } as cod_inm')

    try:
        return devices
    except ValueError:
        print(f'Error: no filter applied')


def session_log(nr):
    filename = f'{nr.host}-output.txt'
    group_object = nr.host.groups.refs[0]
    group_object.connection_options["netmiko"].extras["session_log"] = filename

 
def main() -> None:
    username = input("Username:")
    password = getpass.getpass()

    nr = InitNornir(config_file=CFG_FILE)

    nr.inventory.defaults.password = password
    nr.inventory.defaults.username = username

    devices = filter_inventory(nr)

    result = devices.run(task=get_interfaces_status)

    print_result(result)
 
 
if __name__ == '__main__':
    main()
