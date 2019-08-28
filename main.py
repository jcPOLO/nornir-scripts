from nornir import InitNornir
from nornir.plugins.functions.text import print_result
import getpass
from bootstrap import load_inventory
from main_functions import filter_inventory, make_magic
from models.Menu import Menu

CSV = 'inventory.csv'
CFG_FILE = 'config.yaml'
PLATFORM = ['ios', 'huawei']
EXCLUDED_VLANS = [1, 1002, 1003, 1004, 1005]


def main() -> None:
    username = input("Username:")
    password = getpass.getpass()

    try:
        load_inventory(CSV)
    except:
        print('no se ha podido crear el hosts.yaml')

    input("Files loaded. Press a key to continue...")

    nr = InitNornir(config_file=CFG_FILE)

    nr.inventory.defaults.password = password
    nr.inventory.defaults.username = username

    devices = filter_inventory(nr)

    menu = Menu()
    t = menu.run()

    templates = t.templates
    print(templates)

    result = devices.run(task=make_magic,
                         name=f'CONTAINER TASK',
                         templates=templates
                         )

    print_result(result)

    print("""
        Failed HOSTS:
        """)
    print(result.failed_hosts.keys())


if __name__ == '__main__':
    main()
