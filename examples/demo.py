from swinginghead.compiler import Binder
from ctypes import *
    
def demo():
    demo = Binder.from_file('demo.shl')
    print(demo.head(5.0, 4.0))
    
demo()
