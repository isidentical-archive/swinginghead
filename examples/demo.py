from swinginghead.compiler import Binder
from ctypes import *
    
def demo():
    demo = Binder.from_file('demo.shl')
    print(demo.ir)
    head = CFUNCTYPE(c_float, c_float, c_float)(demo.head)
    print(head(5.0, 4.0), head(3.0, 4.0))
    
demo()
