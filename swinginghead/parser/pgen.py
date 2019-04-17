from lark import Lark
from lark.indenter import Indenter


def get_parser():
    return Lark.open("GRAMMAR", parser="lalr", rel_to=__file__)
