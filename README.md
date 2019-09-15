# FiniteConsole
A way to simplify development of CLI applications.
## Getting started
This module is based on the finite state machine pattern. It may be logic to represent 
a list of options in the terminal (a page) as a state. So the other lists of 
options (pages) are the other states. The program can be represented as an 
oriented graph with mappings from one state to another one.  
Further the terms "menu" and "option" are interchangeable with the terms 
"state" and "mapping".
### Create the program
Use the `Program` class to create the program object which is singleton. You can 
initialize the program with a `Menu` or append it later.
```python
from FiniteConsole import Program, Menu

p = Program()  # Empty
p.init_menu = Menu('main')

p.drop()
p = Program(Menu('initial'))
```
The program can be dropped with the `drop` method.
### Define a state (a menu)
The states are instances of `Menu` class.  
The constructor takes a required parameter `id_` which is its id. **It must be unique 
for a whole program!**
```python
from FiniteConsole import Menu

main_menu = Menu('main')
```
After you have created the `Program` instance, all new `Menu` instances 
will be appended to the program automatically.
```python
from FiniteConsole import Program, Menu

p = Program(Menu('main'))
Menu(1)
Menu('another_one')
print(p.menus)
# {'main': <Menu object...>, '1': <Menu object...>, 'another_one': <Menu object...>}
```
The second parameter `action` is a function, basically it is None. It means the 
state is not finite.  
Finite states do something and then returns to the precedent state.
```python
import sys
from FiniteConsole import Menu

main_menu = Menu('main')
exit_menu = Menu('exit', lambda: sys.exit())
```
If the program state changes on "exit", the function will be executed.  
Parameters are passed to the function via `args` and `kwargs` attributes of 
the program, they are cleared at every loop iteration. Returned value is in the
`result` attribute of the program, it is conserved until the function returns a 
new value.
```python
from FiniteConsole import Program, Menu

finite = Menu('calc', lambda x: x*x)
p = Program(finite)
p.start_loop()  # E.g. as a thread
p.args = [5]
...
print(p.result)
# 25
```
To remove states use `remove_menus` method of the `Program` instance. You can 
pass either `str` containing ids or `Menu` instances.
### Append a mapping (an option)
Use `append_options` of `Menu` instance to append options to the menu. 
It takes `Option` object, which parameters are `inp` - input name, 
`out` - output name, `description` - text for CLI.
```python
import sys
from FiniteConsole import Menu, Option

main_menu = Menu('main').append_options(
    Option('1', 'exit', 'Quit'),
    Option('2', 'do_stuff_1', 'Amazing stuff'),
    Option('yes', 'Another menu', 'Go to another menu, etc.')
)
```
To remove options use `remove_options` method of a `Menu` instance.
### Run
Just use `start_loop` and `stop_loop` methods to run and stop the program.  
If your graph has faults, e.g. options leading nowhere, you will see report about 
these faults in the CLI. 
## Extensions
You can change representation of options and input method. 
### Render
Redefine the method `render` of the `Menu` class. It is responsible for CLI 
presentation of menus.
### Input for mapper
Redefine the method `read_input` of the `Menu` class. It is responsible for getting 
of a new input for mapping. The returned value must be a `str` with id of a new 
state.
## Example
```python
import sys
from FiniteConsole import Menu, Option, Program


def func():
    x = float(input('Enter a number: '))
    print(x*x)


main_menu = Menu('main').append_options(
    Option('0', 'exit', 'Quit'),  # Finite
    Option('1', 'stuff_1', 'Square'),  # Finite
    Option('3', 'submenu', 'Go to another menu')
)
p = Program(main_menu)

Menu('submenu').append_options(Option('back', 'main', 'Go back'))

# Finite states
Menu('exit', lambda: sys.exit())
Menu('stuff_1', func)


p.start_loop()
```
And yes. You can change program's comportment while runtime: append other menus, 
options, etc.