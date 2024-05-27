from scanner import Tokenize
from afterscan import Afterscan
from dsl_token import *
from syntax import *
import graphviz
import json
import pathlib
import os


def __RenderAst(diagramName, ast, debugInfoDir):
    if debugInfoDir is None:
        return
    h = graphviz.Digraph(diagramName, format='svg')
    i = 1
    nodes = [(ast, 0)]
    while len(nodes):
        node = nodes[0]
        if TreeNode.Type.NONTERMINAL == node[0].type:
            h.node(str(i),
                   f"NONTERMINAL\ntype: {node[0].nonterminalType}" + (f"\nattribute: {node[0].attribute}" if node[0].attribute else ""),
                   shape='box')
            if node[1] != 0:
                h.edge(str(node[1]), str(i))
            nodes += [(child, i) for child in node[0].childs]
        else:
            token = node[0].token
            if Token.Type.TERMINAL == token.type:
                h.node(str(i),
                       f"TERMINAL\ntype: {token.terminalType.name}\nstring: {token.str}" + (f"\nattribute: {token.attribute}" if token.attribute else ""),
                       shape='diamond')
            elif Token.Type.KEY == token.type:
                h.node(str(i), f"KEY\nstring: {token.str}" + (f"\nattribute: {token.attribute}" if token.attribute else ""), shape='oval')
            h.edge(str(node[1]), str(i))
        nodes = nodes[1:]
        i += 1
    h.render(directory=debugInfoDir, view=True)


def __GetRCode(node):
    key = "$ATTRIBUTE$"
    if TreeNode.Type.NONTERMINAL != node.type:
        return ""
    res = node.commands[0]
    if -1 != res.find(key):
        raise RuntimeError("Attribute must not be used in first edge")
    for i in range(len(node.childs)):
        childCode = __GetRCode(node.childs[i])
        if len(childCode) != 0:
            res = res + ("\n" if len(res) != 0 else "") + childCode
        if len(node.commands[i + 1]) != 0:
            res = res + ("\n" if len(res) != 0 else "") + node.commands[i + 1].replace(key, repr(node.childs[i].attribute))
    return res



def GetAST(jsonFile, codeFile, is_render):
    with open(jsonFile, 'r') as jsonFile:
        jsonData = json.loads(jsonFile.read())
    syntaxInfo, dsl_info = GetSyntaxDesription(jsonData["syntax"])
    if "debugInfoDir" in jsonData:
        debugInfoDir = pathlib.Path(jsonData["debugInfoDir"])
        if not debugInfoDir.exists():
            os.mkdir(debugInfoDir)
    else:
        debugInfoDir = None
    with open(codeFile, 'r') as codeFile:
        code = codeFile.read()

    tokenList = Tokenize(code, dsl_info)
    # __RenderTokenStream('token_stream_after_scanner', tokenList, debugInfoDir)
    tokenList = Afterscan(tokenList, dsl_info)
    # __RenderTokenStream('token_stream_after_afterscan', tokenList, debugInfoDir)
    ast = BuildAst(syntaxInfo, dsl_info.axiom, tokenList)
    if (is_render):
        __RenderAst('ast', ast, debugInfoDir)
    return ast