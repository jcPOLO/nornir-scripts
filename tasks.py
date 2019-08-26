from nornir.plugins.tasks import networking, text
import main
from models import huawei, ios
import os
import errno
from netmiko.ssh_exception import NetMikoTimeoutException
import configparser


def get_ini_vars() -> dict:
    config = configparser.RawConfigParser()
    config.read('.global.ini')
    r = config
    return dict(r['GLOBAL'])


def get_interfaces_status(nr) -> list:
    r = ''
    if nr.host.platform == 'huawei':
        # print(f'... trying display port vlan for Huawei host: {nr.host}...\n')
        r = huawei.get_interfaces_status(nr)

    if nr.host.platform == 'ios':
        # print(f'... trying show interface status for Cisco host: {nr.host}...\n')
        r = ios.get_interfaces_status(nr)

    return r


def basic_configuration(template, nr) -> None:

    ini_vars = get_ini_vars()
    # Transform inventory data to configuration via a template file
    print(f'... applying config template for host: { nr.host } ...\n')
    r = nr.run(task=text.template_file,
               name=f"APLICAR PLANTILLA LOTE 7 PARA {nr.host.platform}",
               template=template,
               path=f"templates/{nr.host.platform}",
               nr=nr,
               ini_vars=ini_vars,
               )

    # Save the compiled configuration into a host variable
    nr.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    print(f'... write mem config for { nr.host } ...\n')
    nr.run(task=networking.netmiko_send_config,
           config_commands=nr.host["config"].splitlines())


def backup_config(nr) -> None:
    r = ''
    file = f'{nr.host}-{nr.host.hostname}.cfg'
    path = './backups/'
    filename = f'{path}{file}'

    print(f'... exporting running-config for host: {nr.host} ...\n')
    if nr.host.platform == 'huawei':

        # print(f'... trying for Huawei host: {nr.host} by SSH ...\n')
        r = huawei.get_config(nr)

    if nr.host.platform == 'ios':

        # print(f'... trying for Cisco host: {nr.host} by SSH ...\n')
        try:
            ssh = True
            r = ios.get_config(nr)

        except:
            print(f'...SSH not working for {nr.host} IP {nr.host.hostname} , closing connection attempt...')
            ssh = False
            pass
            try:
                nr.host.close_connections()
            except ValueError:
                print('...trying TELNET instead....')
                pass

        if not ssh:

            # nr.host.connection_options['netmiko'] = ConnectionOptions(
            #     extras={"device_type": 'cisco_ios_telnet'})

            main.change_to_telnet(nr)

            print(f'Telnet {nr.host} IP {nr.host.hostname} ...')
            try:
                r = ios.get_config(nr)
            finally:
                print(f'Unable to connect to {nr.host} - {nr.host.hostname} by telnet\n')

    print(f'Saving config for {nr.host} to file {filename}')
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, 'a') as f:
        f.write(r)


def get_interface_description(interfaces, nr) -> list:
    r = ''
    result = []
    for interface in interfaces:
        if nr.host.platform == 'huawei':
            # print(f'... trying display port vlan for Huawei host: {nr.host}...\n')
            r = huawei.get_interface_description(interface, nr)

        if nr.host.platform == 'ios':
            # print(f'... trying show interface status for Cisco host: {nr.host}...\n')
            r = ios.get_interface_description(interface, nr)

        # do not duplicate interface name in description if it already exists
        if interface in r[0]['description']:
            r[0]['description'] = r[0]['description'].replace(interface, '').strip()

        port_dict = {
            'interface': interface,
            'description': r[0]['description'],
        }
        result.append(port_dict)

    return result


