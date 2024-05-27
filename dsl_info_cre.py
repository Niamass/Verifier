from enum import Enum

class Terminal(Enum):
    name = "name"
    char_key = "char_key"

    

tokenRegularExpressions = [
    (Terminal.name, r"[\w^\d][\w]*(:=[^#,\s]*)?|\[(!?[\w^\d][\w]*|[^#,\s]*)\]"),
    #(Terminal.name, r"[\w^\d][\w]*|\[([\w^\d][\w]*)\]"),
    (Terminal.char_key, r"\(|\)|\,|\#|\||\{|\}")
]


keys = [
    ("(", Terminal.char_key),
    (")", Terminal.char_key),
    ("#", Terminal.char_key),
    (",", Terminal.char_key),
    ("|", Terminal.char_key),
    ("{", Terminal.char_key),
    ("}", Terminal.char_key),
]


class Nonterminal(Enum):
    CRE = "CRE"
    BRACKETS = "BRACKETS"
    TSEITIN_ITERATION = "TSEITIN_ITERATION"

axiom = Nonterminal.CRE
