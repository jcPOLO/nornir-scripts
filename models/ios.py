from nornir.plugins.tasks import networking
import logging


def get_config(nr):
    r = nr.run(task=networking.netmiko_send_command,
               name=f"HACER SHOW RUN PARA EL HOST: {nr.host}",
               command_string='show run',
               severity_level=logging.DEBUG).result
    return r


def get_interfaces_status(nr):
    r = nr.run(task=networking.netmiko_send_command,
               name=f'HACER SHOW INTERFACE STATUS PARA EL HOST: {nr.host}',
               command_string='show interfaces status',
               use_textfsm=True
               ).result
    return r
