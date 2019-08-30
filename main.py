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

    # Python program to show time by perf_counter()
    from time import perf_counter
    # Start the stopwatch / counter
    t1_start = perf_counter()

    result = devices.run(task=make_magic,
                         name=f'CONTAINER TASK',
                         templates=templates
                         )

    print_result(result)

    print(
        """
        Failed HOSTS:
        --------------------------------------
        """
    )
    for host in result.failed_hosts:
        print(f'Host: {host}')
        print(f'|__{result.failed_hosts[host].exception.__class__.__name__}')
    print(
        """
        --------------------------------------
        """
    )
    t1_stop = perf_counter()

    elapsed_time = t1_stop - t1_start
    print("Elapsed time during the whole program in seconds:",
          '{0:.2f}'.format(elapsed_time))


if __name__ == '__main__':
    main()
