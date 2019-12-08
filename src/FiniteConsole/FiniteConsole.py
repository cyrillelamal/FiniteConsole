"""
Finite state machine framework simplifies creation of console applications.
Describe your program with oriented graphs
"""
from .exceptions import ProgramExistsException, MenuExistsException, UndeterminedOption


class Program:
    """Singleton"""
    _PROGRAM = None

    def __init__(self, init_menu=None):
        # Check the singleton
        if Program._PROGRAM is not None:
            raise ProgramExistsException

        Program._PROGRAM = self

        self._is_running = False

        # Initial state
        self._init_menu = init_menu
        # Current state
        self._current_menu = init_menu

        # {ID: 'Menu'}
        self.menus = {}
        if isinstance(init_menu, Menu):
            id_ = init_menu.id
            self.menus[id_] = init_menu

        # Actions' parameters and callback
        self.result = None
        self.args = []
        self.kwargs = {}

    @property
    def init_menu(self) -> 'Menu':
        return self._init_menu

    @init_menu.setter
    def init_menu(self, menu):
        """Set the initial menu. If the program is stopped, set the menu as the current menu"""
        self._init_menu = menu
        if not self._is_running:
            self._current_menu = menu

    # New menus will be appended automatically if the program exists
    def append_menus(self, *menus):
        for menu in menus:  # 'Menu'
            new_id = menu.id
            # Check id
            if new_id in self.menus:
                raise MenuExistsException(f'The menu with id "{new_id}" already exists')
            self.menus[new_id] = menu
        return self

    def remove_menus(self, *menus):
        for menu in menus:
            # Remove by id
            if isinstance(menu, str):
                self.menus.pop(menu, None)
            # Remove by 'Menu' object (value)
            elif isinstance(menu, Menu):
                self.menus = {k: v for k, v in self.menus.items() if v != menu}
        return self

    def resolve_dependencies(self) -> str:
        """Check if all options and menus are correct"""
        report = ''

        if self.init_menu is None:
            report += 'The initial menu is undefined.\n'

        for menu in self.menus.values():  # No need of colored graphs
            # The menu has no options and is not a finite state
            if not menu.options and not menu.is_finite:
                report += f'The menu "{menu}" has no options.\n'
                continue

            # Check if all options lead to menus
            for opt in menu.options.values():
                out = opt.out

                # Lazy binding
                if isinstance(out, str):
                    opt.out = self.menus.get(out, None)

                if out is None:
                    report += f'The option "{opt}" in the menu "{menu}" is broken.\n'

        print(report)
        return report

    def start_loop(self):
        """Run the program"""
        # There are problems
        if self.resolve_dependencies():
            return

        self._is_running = True
        while self._is_running:
            # Render
            self._current_menu.render()
            # Get input
            inp = self._current_menu.read_input()
            # # Change the state
            self._do_mapping(inp)

    def stop_loop(self):
        """Stop the program"""
        if self._is_running:
            self._is_running = False

    def _do_mapping(self, inp):
        """Change menu"""
        new_state = self._current_menu.options.get(str(inp)).out  # 'Menu'
        if new_state.is_finite:
            self.result = new_state.action(*self.args, **self.kwargs)
            self.args.clear()
            self.kwargs.clear()
        else:
            self._current_menu = new_state

    @staticmethod
    def get_program() -> 'Program':
        return Program._PROGRAM

    @staticmethod
    def drop():
        """Replace the singleton"""
        Program._PROGRAM = None


class Menu:
    """State"""
    TEST = False

    def __init__(self, id_, action=None):
        self.id = str(id_)  # Must be unique

        # Check if the menu is a finite state
        if callable(action):
            is_finite = True
        else:
            is_finite = False
        self._action = action
        self.is_finite = is_finite

        # {INP: 'Option'}
        self.options = {}

        # Register menu if the program exists
        p = Program.get_program()
        if p is not None:
            p.append_menus(self)

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action_):
        self._action = action_
        self.is_finite = True
        if not action_ or action_ is None:
            self.is_finite = False

    def render(self):
        """Display options in the CLI"""
        str_ = '\n'.join([str(opt) for opt in self.options.values()])
        print(str_)
        return str_

    def read_input(self) -> str:
        """Get input for mapping (by user)"""
        # FOR UNIT TESTS
        if Menu.TEST:
            return '1'

        inp = None
        while inp not in self.options:
            inp = input('Choose an option: ')
        return inp

    def append_options(self, *options):
        """Append 'Option'(s) to the menu"""
        for opt in options:  # 'Option'
            new_inp = opt.inp
            # The option is not registered yet
            if new_inp not in self.options:
                self.options[new_inp] = opt
            else:
                raise UndeterminedOption(f'The same input "{new_inp}" in the menu "{self}"')
        return self

    def remove_options(self, *options):
        """Remove options from the menu by list of inputs or by list of 'Option' objects"""
        # Make list of inputs
        options = [opt.inp if isinstance(opt, Option) else opt for opt in options]
        # Remove by inputs
        self.options = {k: v for k, v in self.options.items() if k not in options}
        return self

    def remove(self):
        """Remove the menu from the program"""
        p = Program.get_program()
        p.remove_menus(self)
        return self

    def __str__(self):
        return f'{self.id}'


class Option:
    """Mapping"""
    def __init__(self, inp, out, description=''):
        # Ready for user's CLI input
        if not isinstance(inp, str):
            inp = str(inp)
        self.inp = inp

        # Bind 'Menu'
        if isinstance(out, (str, Menu,)):
            # Bind 'Menu' or string to lazy binding
            if isinstance(out, str):
                p = Program.get_program()
                if p is not None:
                    out = p.menus.get(out, out)
        else:
            raise AttributeError('Inappropriate type of input')
        self.out = out

        self.description = description

    def __str__(self):
        return f'{self.inp}. {self.description}'
