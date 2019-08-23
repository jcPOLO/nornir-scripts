from nornir.plugins.tasks import networking
import logging


def get_config(nr) -> str:
    r = nr.run(task=networking.netmiko_send_command,
               name=f"SHOW RUN PARA EL HOST: {nr.host}",
               command_string='show run',
               severity_level=logging.DEBUG,
               ).result
    return r


def get_interfaces_status(nr) -> list:
    r = nr.run(task=networking.netmiko_send_command,
               name=f'SHOW INTERFACE STATUS PARA EL HOST: {nr.host}',
               command_string='show interfaces status',
               use_textfsm=True,
               severity_level=logging.DEBUG,
               ).result
    return r


def get_interface_description(interface, nr) -> list:
    r = nr.run(task=networking.netmiko_send_command,
               name=f'SHOW INTERFACE {interface} PARA EL HOST: {nr.host}',
               command_string=f'show interface {interface}',
               use_textfsm=True,
               severity_level=logging.DEBUG,
               ).result
    return r


# TODO: this and this return type
def get_neighbor(interface, nr):
    r = nr.run(task=networking.netmiko_send_command,
               name='MUESTRA LOS VECINOS LOS PUERTOS',
               command_string=f'show cdp nei {interface} det',
               use_textfsm=True
               ).result
