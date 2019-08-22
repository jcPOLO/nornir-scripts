from nornir.plugins.tasks import networking
import logging


def get_config(nr):
    r = nr.run(task=networking.netmiko_send_command,
               name=f"HACER DISPLAY CURRENT PARA EL HOST: {nr.host}",
               command_string='display current',
               severity_level=logging.DEBUG).result
    return r


def get_interfaces_status(nr):
    r = nr.run(task=networking.netmiko_send_command,
               name=f'HACER DISPLAY PORT VLAN PARA EL HOST: {nr.host}',
               command_string='display port vlan',
               use_textfsm=True
               ).result
    return r
