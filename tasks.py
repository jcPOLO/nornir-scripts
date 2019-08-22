from nornir.plugins.tasks import networking, text
from nornir.core.exceptions import NornirSubTaskError
import main
from models import huawei, ios
import os
import errno


# def get_interfaces_status(nr):
#     r = ''
#     if nr.host.platform == 'huawei':
#
#         print(f'... trying display port vlan for Huawei host: {nr.host} by SSH ...\n')
#         r = huawei.get_interfaces_status(nr)
#         return r
#
#     if nr.host.platform == 'ios':
#
#         print(f'... trying show interface status for Cisco host: {nr.host} by SSH ...\n')
#         try:
#             ssh = True
#             r = ios.get_interfaces_status(nr)
#
#         except NornirSubTaskError:
#             print('...SSH not working, closing connection attempt...')
#             ssh = False
#             try:
#                 nr.host.close_connections()
#             except ValueError:
#                 print('...trying TELNET instead....')
#                 pass
#
#         if not ssh:
#
#             # nr.host.connection_options['netmiko'] = ConnectionOptions(
#             #     extras={"device_type": 'cisco_ios_telnet'})
#
#             main.change_to_telnet(nr)
#
#             print(f'Trying SHOW INTERFACE STATUS FOR {nr.host} BY TELNET')
#             r = ios.get_interfaces_status(nr)
#
#     return r

def get_interfaces_status(nr):
    r = ''
    if nr.host.platform == 'huawei':
        print(f'... trying display port vlan for Huawei host: {nr.host}...\n')
        r = huawei.get_interfaces_status(nr)

    if nr.host.platform == 'ios':
        print(f'... trying show interface status for Cisco host: {nr.host}...\n')
        r = ios.get_interfaces_status(nr)

    return r


def basic_configuration(nr, template):

    # Transform inventory data to configuration via a template file
    print(f'... applying config template for host: { nr.host } ...\n')
    r = nr.run(task=text.template_file,
               name=f"APLICAR PLANTILLA LOTE 7 PARA {nr.host.platform}",
               template=template,
               path=f"templates/{nr.host.platform}",
               nr=nr)

    # Save the compiled configuration into a host variable
    nr.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    print(f'... write mem config for { nr.host } ...\n')
    nr.run(task=networking.netmiko_send_config,
           config_commands=nr.host["config"].splitlines())


def backup_config(nr):
    r = ''
    file = f'{nr.host}-{nr.host.hostname}.cfg'
    path = './backup/'
    filename = f'{path}{file}'

    print(f'... exporting running-config for host: {nr.host} ...\n')
    if nr.host.platform == 'huawei':

        print(f'... trying for Huawei host: {nr.host} by SSH ...\n')
        r = huawei.get_config(nr)

    if nr.host.platform == 'ios':

        print(f'... trying for Cisco host: {nr.host} by SSH ...\n')
        try:
            ssh = True
            r = ios.get_config(nr)

        except:
            print('...SSH not working, closing connection attempt...')
            ssh = False
            try:
                nr.host.close_connections()
            except ValueError:
                print('...trying TELNET instead....')
                pass

        if not ssh:

            # nr.host.connection_options['netmiko'] = ConnectionOptions(
            #     extras={"device_type": 'cisco_ios_telnet'})

            main.change_to_telnet(nr)

            print(f'Trying FOR {nr.host} BY TELNET')
            r = ios.get_config(nr)

    print(f'Saving config for {nr.host} to file {filename}')
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, 'a') as f:
        f.write(r)







