from enum import Enum

class Terminal(Enum):
    number = "number"
    name = "name"
    char_key = "char_key"

    

tokenRegularExpressions = [
    (Terminal.number, r"[0-9]+(.[0-9]*)?"),
    (Terminal.name, r"[\w^\d][\w]*"),
    (Terminal.char_key, r"\(|\)|\,|\.|\:|\[|\]|\-\>|\<\-|\;|\:\=|\=|\||\&|\/|\*|\-|\+|\!")
]


keys = [
    ("ciao", Terminal.name),
    ("class", Terminal.name),
    ("scheme", Terminal.name),
    ("events", Terminal.name),
    ("effects", Terminal.name),
    ("conditions", Terminal.name),
    ("assertions", Terminal.name),
    ("variables", Terminal.name),
    ("states", Terminal.name),
    ("objects", Terminal.name),
    ("links", Terminal.name),
    ("else", Terminal.name),
    ("new", Terminal.name),
    ("public", Terminal.name),
    ("private", Terminal.name),
    ("[", Terminal.char_key),
    ("]", Terminal.char_key),
    ("(", Terminal.char_key),
    (")", Terminal.char_key),
    ("!", Terminal.char_key),
    ("+", Terminal.char_key),
    ("-", Terminal.char_key),
    ("*", Terminal.char_key),
    ("/", Terminal.char_key),
    ("->", Terminal.char_key),
    ("<-", Terminal.char_key),
    ("&", Terminal.char_key),
    ("|", Terminal.char_key),
    ("=", Terminal.char_key),
    (":=", Terminal.char_key),
    (":", Terminal.char_key),
    (";", Terminal.char_key),
    (",", Terminal.char_key),
    (".", Terminal.char_key),
]


class Nonterminal(Enum):
    CIAO_PROGRAM = "CIAO_PROGRAM"
    AUTO_CLASS = "AUTO_CLASS"
    AUTO_SCHEME = "AUTO_SCHEME"
    EVENTS = "EVENTS"
    EFFECTS = "EFFECTS"
    CONDITIONS = "CONDITIONS"
    ASSERTIONS = "ASSERTIONS"
    INTERFACE = "INTERFACE"
    DECLARATION = "DECLARATION"
    VARIABLES = "VARIABLES"
    STATES = "STATES"
    STATE = "STATE"
    TRANSITION = "TRANSITION"
    STRIGHT = "STRIGHT"
    DECISION = "DECISION"
    CALL = "CALL"
    ACTIONS = "ACTIONS"
    ASSIGNMENT = "ASSIGNMENT"
    OBJECTS = "OBJECTS"
    OBJECT = "OBJECT"
    INITIAL = "INITIAL"
    LINKS = "LINKS"
    LINK = "LINK"
    INTERFACES = "INTERFACES"
    EXPRESSION = "EXPRESSION"
    

axiom = Nonterminal.CIAO_PROGRAM
