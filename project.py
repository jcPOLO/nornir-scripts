from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from nornir.plugins.tasks.networking import napalm_get, napalm_cli, napalm_configure
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_save_config
from typing import List
from nornir.core.task import Result, Task

import getpass


def hi(task):  # nr.run(task=hi, num_workers=1)
    print(f"hi! My name is {task.host.name} and I live in {task.host['site']}")


def get_facts(nr):
    r = nr.run(task=napalm_get, getters=['facts'])
    #import ipdb; ipdb.set_trace()
    nr.host['facts'] = r.result['facts']


def get_r(nr, command_string):
    # r = nr.run(task=netmiko_send_command, command_string=command_string, use_textfsm=True)
    r = nr.run(task=napalm_cli, commands=[command_string])
    return r


def get_num_interfaces(d) -> None:
    print(f'hay { d } cacharro{ "s" if d > 1 else "" } para chequear.')


def get_trunk_interfaces(d) -> None:
    for host in d:
    # import ipdb; ipdb.set_trace()
        for interface in d[host].result:
            for key,value in interface.items():
                if key == 'vlan' and value == 'trunk':
                    print(f'El valor es {value} y la interfaz es {interface["port"]}')


def main() -> None:
    username = input("Username:")
    password = getpass.getpass()

    nr = InitNornir(config_file="config.yaml")

    nr.inventory.defaults.password = password
    nr.inventory.defaults.username = username

    ios = nr.filter(F(platform='ios') & ~F(port=23))
    ce = nr.filter(F(platform='ce') & ~F(port=23))
    ios_telnet = nr.filter(F(platform='ios') & F(port=23))

    # facts_result = ios.run(task=get_facts)
    # vlans_result = get_r(ios, 'show vlan')
    a = get_r(ios, 'show interfaces status')
    b = get_r(ios_telnet, 'show interfaces status')
    result = []
    result.append(a)
    # import ipdb; ipdb.set_trace()
    result.append(b)
    print(result)

    for r in result:
        get_num_interfaces(len(r.items()))
        # get_trunk_interfaces(r)

    # for host in interfaces_result:
    #     # import ipdb; ipdb.set_trace()
    #     for interface in interfaces_result[host].result:
    #         for key,value in interface.items():
    #             if key == 'vlan' and value == 'trunk':
    #                 print(f'El valor es {value} y la interfaz es {interface["port"]}')


        # print(interfaces_result[host].result[6])


    # import ipdb; ipdb.set_trace()

    # print_result(facts_result)
    # print_result(vlans_result)
    # print_result(interfaces_result)
    # pp interfaces_result['host1'].result
    # pp interfaces_result['host1'].result[6]


if __name__ == '__main__':
    main()

# result = cmh_spines.run(task=networking.napalm_get,
#                         getters=["facts"])
# print_result(result)






