from nornir import InitNornir
from nornir.plugins.functions.text import print_result
import getpass
import tasks
from bootstrap import load_inventory
from models.Template import Template
from models.TemplateManager import TemplateManager
from main_functions import get_templates, config, session_log, trunk_description, filter_inventory

CSV = 'inventory.csv'
CFG_FILE = 'config.yaml'
PLATFORM = ['ios', 'huawei']
EXCLUDED_VLANS = [1, 1002, 1003, 1004, 1005]


def make_magic(nr, if_trunk) -> None:
    # makes a log file output for every device accessed
    session_log(nr)
    # backup config
    tasks.backup_config(nr)

    if if_trunk:
        print('trunk dafdafdsafds')
        trunk_description(nr)

    config(nr)


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

    if_trunk = False
    template_prompts = [
        'common.j2',
        'snmp.j2',
        'trunk_description.j2',
        'ssh.j2'
        # 'tacacs.j2',
        # 'vlan1099.j2',
    ]

    templates = [
        Template(template, template) for template in template_prompts
    ]

    templates = get_templates(templates)
    template_m = TemplateManager(templates)
    template_m.create_final_template('huawei')
    template_m.create_final_template('ios')
    for template in templates:
        print(f'Template applied: {str(template)}')
        if 'trunk' in template.prompt:
            if_trunk = True
        else:
            print('Trunk false')

    result = devices.run(task=make_magic, if_trunk=if_trunk)
    print_result(result)
    print(result.failed_hosts.keys())


if __name__ == '__main__':
    main()
