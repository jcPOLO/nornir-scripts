from nornir.plugins.tasks import networking
import logging


def get_config(nr) -> str:
    r = nr.run(task=networking.netmiko_send_command,
               name=f"DISPLAY CURRENT PARA EL HOST: {nr.host}",
               command_string='display current',
               severity_level=logging.DEBUG,
               ).result
    return r


def get_interfaces_status(nr) -> list:
    r = nr.run(task=networking.netmiko_send_command,
               name=f'DISPLAY PORT VLAN PARA EL HOST: {nr.host}',
               command_string='display port vlan',
               use_textfsm=True,
               severity_level=logging.DEBUG,
               ).result
    return r


def get_interface_description(interface, nr) -> list:
    r = nr.run(task=networking.netmiko_send_command,
               name=f'DISPLAY INTERFACE {interface} PARA EL HOST: {nr.host}',
               command_string=f'display interface {interface}',
               use_textfsm=True,
               severity_level=logging.DEBUG,
               ).result
    return r


# TODO: this and this return type
def get_neighbor(interface, nr):
    r = nr.run(task=networking.netmiko_send_command,
               name='MUESTRA LA DESCRIPTION DE LOS PUERTOS',
               command_string=f'dis ldp nei {interface}',
               use_textfsm=True
               ).result
