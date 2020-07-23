import os, sys
from helpers import is_int
from models.Template import Template


class Menu(object):
    platforms = ['ios', 'huawei', 'nxos']
    template_files = [
        '',
        'common.j2',
        'snmp.j2',
        'trunk_description.j2',
        'management.j2',
        'ssh.j2'
    ]

    def __init__(self) -> None:
        self.choices = {
            "1": self.template_files[1],
            "2": self.template_files[2],
            "3": self.template_files[3],
            "4": self.template_files[4],
            "5": self.template_files[5],
            "a": self.apply,
            "s": self.show,
            "z": self.clear,
            "e": self.exit,

        }
        self.final_choices = []

    @staticmethod
    def display_menu() -> None:
        os.system('clear')
        print("""
        Select the number one by one. When finished, press 'a' to run:

        1. Common configuration (local users, logging, line vty config, timeouts, etc.)
        2. SNMP configuration (ACLs, WR and RO communities)
        3. Description for trunk interfaces
        4. Management network (mgmt vlan l2 & l3, trunk allowed add)
        5. SSH configuration.

        a. Apply      s. Show template      z. Clear selections             e. Exit
        
        """)

    def display_final_choices(self) -> None:
        print(f' Templates selected: {self.final_choices}\n')

    # TODO: Review this method that probable should return None instead
    def run(self, printable='') -> callable:

        self.display_menu()
        print(printable)

        if self.final_choices:
            self.display_final_choices()
        while True:
            self.get_choice()

    def apply(self) -> Template:
        if self.final_choices:
            try:
                print(f"applied: -> {self.final_choices} <-")
                t = Template(self.final_choices)
                for platform in self.platforms:
                    t.create_final_template(platform)
                return t
            except exit():
                raise print('---------------- Error ----------------')
        else:
            print("{0} choices selected are not valid".format(self.final_choices))

    def show(self) -> None:
        if self.final_choices:
            print(f"Which platform? {self.platforms}")
            platform = input("Enter an option: ")
            result = []
            if platform in self.platforms:

                for t in self.final_choices:
                    with open(f'templates/{platform}/{t}') as f:
                        result.append(f.read())
                result_str = ''.join(result)
                self.run(result_str)
            else:
                print("{0} is not a valid choice".format(platform))

    def clear(self) -> None:
        self.final_choices = []
        self.run()
        print(f'Selected templates cleared.\n')

    def exit(self) -> None:
        self.final_choices = []
        print(f'Bye!\n')
        sys.exit()

    def get_choice(self):
        choice = input("Enter an option: ")
        template = self.choices.get(choice)

        if is_int(choice) and 0 < int(choice) < len(Menu.template_files):
            if template not in self.final_choices:
                self.final_choices.append(template)
            self.display_menu()
            self.display_final_choices()
        elif choice in self.choices.keys():
            return template()
        else:
            print("{0} is not a valid choice".format(choice))
