from swinginghead.compiler import Binder
from code import InteractiveConsole
from ctypes import *

def main(file):
    binder = Binder.from_file(file)
    InteractiveConsole(locals={'binder': binder, **globals()}).interact()

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
