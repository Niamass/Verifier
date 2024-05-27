#import dsl_info
from dsl_token import Token
import sys
import re


def __SkipSpaces(code, pos):
    for i in range(pos, len(code)):
        if not code[i].isspace():
            return i
    return len(code)


def __GetCurrentToken(code, pos, dsl_info):
    for terminal, regex in dsl_info.tokenRegularExpressions:
        result = re.match(regex, code[pos:])
        if not result:
            continue

        token = Token(Token.Type.TERMINAL)
        token.terminalType = terminal
        token.str = result.group(0)
        return token, pos + len(token.str)
    raise SyntaxError("Failed to recognize token")


def Tokenize(code, dsl_info):
    size = len(code)
    pos = 0
    tokens = []
    pos = __SkipSpaces(code, pos)
    while pos < size:
        token, pos = __GetCurrentToken(code, pos, dsl_info)
        tokens.append(token)
        pos = __SkipSpaces(code, pos)
    return tokens


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need only one argument: program text path")
        sys.exit()
    with open(sys.argv[1], 'r') as file:
        tokenList = Tokenize(file.read())
        print("tokens:")
        for token in tokenList:
            print(f"TYPE: '{token.terminalType.name}', STRING: '{token.str}'.")
