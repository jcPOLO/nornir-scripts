#!/usr/bin/python3
#

import napalm
import sys
from models.device import Device
from models.user import User


# Device, User
def connect_to_device(device_obj: Device, user_obj: User) -> napalm:

    optional_args = {
        'transport': device_obj.protocol
    }

    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver(device_obj.driver)

    # Connect
    c = driver(device_obj.ip_address, user_obj.username,
               user_obj.password, optional_args=optional_args)

    return c


def main():

    if len(sys.argv) < 2:
        return print('faltan argumentos <ip> [ios|ce|telnet]')

    ip_address = sys.argv[1]
    device = Device(ip_address)
    user = User()

    if len(sys.argv) > 2:
        if sys.argv[2] != 'ios' and sys.argv[2] != 'ce':
            return print('argumento 2 no valido: debe ser ios (para cisco) o ce (para huawei)')

        device.driver = sys.argv[2]

    print('\nConectando a ' + device.ip_address +
          ' usando ' + device.protocol +
          ' con driver ' + device.driver)

    connection = connect_to_device(device, user)

    print('Opening ...')

    try:
        connection.open()
    except napalm.base.exceptions.ConnectionException:
        print('Error conectando por SSH, probando telnet...')
        device.protocol = 'telnet'
        connection = connect_to_device(device, user)
        connection.open()
    except ValueError:
        return print('jare')

    # config = connection.get_config()
    facts = connection.get_facts()

    connection.close()
    print('Done.')

    print(facts['hostname'])
    print(facts['vendor'])
    print(facts['os_version'])
    print(facts['serial_number'])
    print(facts['model'])


main()
