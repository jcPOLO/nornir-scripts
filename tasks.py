from nornir.plugins.tasks import networking, text
from nornir.core.exceptions import NornirSubTaskError
import main


TEMPLATE = 'test.j2'


def get_interfaces_status(nr):
    r = ''
    if nr.host.platform == 'huawei':

        print(f'... doing display port vlan for Huawei host: {nr.host} ...\n')
        r = nr.run(task=networking.netmiko_send_command,
                   name=f'DOING DISPLAY PORT VLAN FOR {nr.host}',
                   command_string='display port vlan',
                   use_textfsm=True
                   ).result
        return r

    if nr.host.platform == 'ios':

        print(f'... doing show interface status for Cisco host: {nr.host} ...\n')
        try:
            ssh = True
            r = nr.run(task=networking.netmiko_send_command,
                       name=f'DOING SHOW INTERFACE STATUS FOR {nr.host} BY SSH',
                       command_string='show interfaces status',
                       use_textfsm=True
                       ).result

        except NornirSubTaskError:
            print('Al parecer, SSH no funciona asi que cerrando conexion...')
            ssh = False
            try:
                nr.host.close_connections()
            except ValueError:
                print('... y abriendo un telnet en su lugar ....')
                pass

        if not ssh:

            main.change_to_telnet(nr.host)

            r = nr.run(task=networking.netmiko_send_command,
                       name=f'DOING SHOW INTERFACE STATUS FOR {nr.host} BY TELNET',
                       command_string='show interfaces status',
                       use_textfsm=True
                       ).result

    return r


def basic_configuration(interfaces, nr):

    # Transform inventory data to configuration via a template file
    print(f'... applying config template for host: { nr.host } ...\n')
    r = nr.run(task=text.template_file,
               name=f"APLICAR PLANTILLA LOTE 7 PARA {nr.host.platform}",
               template=TEMPLATE,
               path=f"templates/{nr.host.platform}",
               interfaces=interfaces,
               nr=nr)

    # Save the compiled configuration into a host variable
    nr.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    print(f'... write mem config for { nr.host } ...\n')
    nr.run(task=networking.netmiko_send_config,
           config_commands=nr.host["config"].splitlines())


def get_interface_description(interfaces, nr):
    result = []
    for interface in interfaces:
        r = nr.run(task=networking.netmiko_send_command,
                   name='MUESTRA LA DESCRIPTION DE LOS PUERTOS',
                   command_string=f'show interface {interface}',
                   use_textfsm=True
                   ).result

        # do not duplicate interface name in description if it already exists
        if interface in r[0]['description']:
            r[0]['description'] = r[0]['description'].replace(interface, '').strip()

        port_dict = {
            'interface': interface,
            'description': r[0]['description'],
        }
        result.append(port_dict)

    return result


def get_neighbor(interface, nr):
    r = nr.run(task=networking.netmiko_send_command,
               name='MUESTRA LA DESCRIPTION DE LOS PUERTOS',
               command_string=f'show cdp nei {interface} det',
               use_textfsm=True
               ).result
