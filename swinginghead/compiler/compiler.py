import llvmlite.ir as ir
from ast import literal_eval
from lark import Transformer
from swinginghead.parser.pgen import get_parser
from swinginghead.parser.elm import elmer


class Compiler(Transformer):
    def start(self, tokens):
        print(tokens)

    def literal(self, tokens):
        vmtype, value = tokens
        if isinstance(vmtype, (ir.VectorType, ir.Aggregate)):
            return vmtype([literal_eval(token.value) for token in value.children])
        return vmtype(literal_eval(value))

    def typedecl(self, tokens):
        vmtype = tokens.pop(0)
        vmtype = getattr(ir, f"{vmtype.capitalize()}Type")
        try:
            if issubclass(vmtype, (ir.VectorType, ir.Aggregate)):
                element, count = [tree.children.pop() for tree in tokens]
                vmtype = vmtype(element, literal_eval(count))
            else:
                vmtype = vmtype(literal_eval(tokens.pop().children.pop()))
        except IndexError:
            vmtype = vmtype()

        return vmtype

    def compile(self, tree):
        nodes = self.transform(tree)
        return nodes


if __name__ == "__main__":
    parser = get_parser()
    compiler = Compiler()
    tree = parser.parse(
        """
    (`int<32>`->15)
    (`int<64>`->323443)
    (`float`->3.35)
    (`vector<`int<32>`, 4>`->@32~44~55~66@)
    (`array<`int<32>`, 4>`->@32~44~55~66@)
    """
    )
    compiler.compile(tree)
