import llvmlite.binding as llvm
from swinginghead.compiler.compiler import Compiler
from swinginghead.parser.pgen import get_parser

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter() 

class Binder:
    def __init__(self, code):
        parser = get_parser()
        compiler = Compiler()
        
        tree = parser.parse(code)
        self.ir = str(compiler.compile(tree))
    
        self.engine = self.get_engine()
        self.mod = self.compile_ir(self.ir)
        
    @classmethod
    def from_file(cls, file):
        with open(file) as f:
            code = f.read()
        return cls(code)
        
    def compile_ir(self, llvm_ir):
        mod = llvm.parse_assembly(llvm_ir)
        mod.verify()
        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    @staticmethod
    def get_engine():
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return engine

    def __getattr__(self, attr):
        return self.engine.get_function_address(attr)
    
if __name__ == '__main__':
    import sys
    import ctypes
    binder = Binder.from_file(*sys.argv[1:])
    cfunc = ctypes.CFUNCTYPE(ctypes.c_float, ctypes.c_float, ctypes.c_float)(binder.head)
    print(cfunc(3.0, 4.0))
