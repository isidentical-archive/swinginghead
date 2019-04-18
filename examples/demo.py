from swinginghead.compiler import Binder
from ctypes import *

def demo():
    demo = Binder.from_file('demo.shl')
    head = CFUNCTYPE(c_float, c_float, c_float)(demo.head)
    assert head(3.0, 4.0) == 12.0
    assert head(1.5, 1.5) == 2.25
    
demo()
