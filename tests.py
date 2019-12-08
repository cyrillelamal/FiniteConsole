import unittest
import threading


from src.FiniteConsole.FiniteConsole import Program, Menu, Option
from src.FiniteConsole import ProgramExistsException, MenuExistsException, UndeterminedOption


class TestProgram(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Program()
        Menu.TEST = True

    def tearDown(self) -> None:
        self.p.drop()

    def test_singleton(self):
        self.assertEqual(Program.get_program(), self.p)
        try:
            self.assertRaises(ProgramExistsException, Program())
        except ProgramExistsException:
            pass
        self.assertEqual(Program.get_program(), self.p)

    def test_dependencies_resolver(self):
        p = self.p

        def func():
            pass

        empty_menu = Menu('empty')
        self.assertIn('no options', p.resolve_dependencies())
        empty_menu.action = func
        self.assertNotIn('no options', p.resolve_dependencies())

        self.assertIn('The initial', p.resolve_dependencies())
        p.init_menu = empty_menu
        self.assertNotIn('The initial', p.resolve_dependencies())

        Menu('main').append_options(Option(1, 'a'))
        Menu('a', func)
        self.assertFalse(p.resolve_dependencies())

    def test_loop(self):
        p = self.p
        self.assertFalse(p._is_running)
        t = threading.Thread(target=p.start_loop())
        t.start()
        t.join()
        self.assertFalse(p._is_running)

        p.init_menu = Menu('main')
        p.init_menu.append_options(Option(1, 'A', 'Go to A'), Option(2, 'B', 'Go to B'))
        Menu('A', lambda x: x*x)
        Menu('B', lambda x: x*x)

        def for_lambda():
            yield 5

        p.args.append(next(for_lambda()))
        t = threading.Thread(target=p.start_loop)
        t.start()
        while not p._is_running:
            pass

        p.stop_loop()

    def test_mapping(self):
        p = self.p
        p.init_menu = Menu('main').append_options(Option(1, 'inner', 'Go to inner'))
        Menu('inner').append_options(Option(1, 'main', 'Go back'))
        self.assertFalse(p.resolve_dependencies())
        self.assertEqual(p._current_menu, p.menus['main'])
        p._do_mapping(1)
        self.assertEqual(p._current_menu, p.menus['inner'])
        p._do_mapping(1)
        self.assertEqual(p._current_menu, p.menus['main'])


class TestMenu(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Program()

    def tearDown(self) -> None:
        self.p.drop()

    def test_registration(self):
        p = self.p
        self.assertFalse(p.menus)
        menus = [Menu('main'), Menu('exit')]
        self.assertEqual(len(menus), len(p.menus))
        try:
            self.assertRaises(MenuExistsException, Menu('main'))
        except MenuExistsException:
            pass
        self.assertEqual(len(menus), len(p.menus))

        for menu in menus:
            id_ = menu.id
            self.assertIn(id_, p.menus)
            self.assertIn(menu, p.menus.values())
            self.assertEqual(menu, p.menus.get(id_))

        for menu, length in zip(menus, range(len(menus), -1)):
            menu.remove()
            self.assertEqual(length, p.menus)

    def test_finite_state(self):
        main = Menu('main')
        self.assertFalse(main.is_finite)
        self.assertIsNone(main.action)
        alg1 = Menu('counter', lambda x: x*x)
        self.assertTrue(alg1.is_finite)
        self.assertTrue(callable(alg1.action))

    def test_options_management(self):
        menu = Menu('main')
        self.assertFalse(menu.options)
        opt = Option(1, 'unpinned')
        menu.append_options(opt)
        self.assertEqual(1, len(menu.options))
        self.assertEqual(opt, menu.options.get('1'))

        menu.options.clear()
        options = [Option(1, 'one'), Option(2, 'two'), Option(3, 'three')]
        menu.append_options(*options)
        for opt in options:
            inp = opt.inp
            self.assertEqual(opt, menu.options.get(inp))
        self.assertEqual(len(options), len(menu.options))

        for opt in options:
            menu.remove_options(opt)
            self.assertTrue(menu.options.get(opt.inp, True))
        self.assertEqual(0, len(menu.options))
        menu.append_options(*options)
        for opt in options:
            menu.remove_options(opt.inp)
            self.assertTrue(menu.options.get(opt.inp, True))
        self.assertEqual(0, len(menu.options))

    def test_remove(self):
        p = self.p
        menus = [Menu('1'), Menu('2'), Menu('3'), Menu(4)]
        for menu in menus:
            self.assertIn(menu, p.menus.values())
            menu.remove()
            self.assertNotIn(menu, p.menus.values())

    def test_undetermined_options(self):
        menu = Menu(1).append_options(Option(1, 'repeated'))
        options = [Option(1, 'a'), Option(1, 'b'), Option(1, 'c')]
        for opt in options:
            try:
                self.assertRaises(UndeterminedOption, menu.append_options(opt))
            except UndeterminedOption:
                pass


class TestOption(unittest.TestCase):
    def setUp(self) -> None:
        self.p = Program()

    def tearDown(self) -> None:
        self.p.drop()

    def test_type_binding(self):
        main = Menu('main')
        exit_ = Menu('exit')
        try:
            self.assertRaises(AttributeError, Option(None, None))
        except AttributeError:
            pass
        opt = Option(1, 'main')
        self.assertEqual(opt.out, main)
        opt = Option(1, 'exit')
        self.assertEqual(opt.out, exit_)
        opt = Option(1, main)
        self.assertEqual(opt.out, main)
        opt = Option(1, exit_)
        self.assertEqual(opt.out, exit_)


if __name__ == '__main__':
    unittest.main()
