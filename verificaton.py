from digraph import TransitionsDfa
import graphviz
from copy import deepcopy
from build_ast import GetAST
from cre_to_dfa import get_min_dfa
from build_semantic_graph import build_semantic_graph


def render_match_result(graph, tran, dir):
    g = graphviz.Digraph()
    g.attr('node', shape='circle', label = '', width='0.3')
    g.node('', _attributes={'fillcolor' : 'black', 'style' : 'filled'})
    g.edge('', str(graph.start_state))
    gr_tran = deepcopy(graph.transitions)
    source_states = tran.get_source_states()
    for st in source_states:
        symbols = tran.get_transitions_sym(st)
        for sym in symbols:
            next_st = tran.get_next_state(st, sym)
            g.edge(str(st), str(next_st), label =" "+sym)
            gr_tran.del_transition(st, sym)

    g.attr('edge', style='dashed', color='red')
    source_states = gr_tran.get_source_states()
    for st in source_states:
        symbols = gr_tran.get_transitions_sym(st)
        for sym in symbols:
            next_st = gr_tran.get_next_state(st, sym)
            g.edge(str(st), str(next_st), label =" "+sym)

    g.attr('graph', ranksep='0.2', nodesep='0.3')
    #g.engine = 'neado'
    #g.attr(rankdir='LR')
    g.render(dir, view=True)


def subs(syms_gr, syms_dfa):
    for sg in syms_gr:
        if sg not in syms_dfa:
            if "A" in syms_dfa:
                continue
            return False
    return True


def match(gr, dfa, gr_st, dfa_st, gr_dfa_states, transitions):
    res = True
    syms = gr.transitions.get_transitions_sym(gr_st)
    for sym in syms:
        next_gr_st = gr.next(gr_st, sym)        
        next_dfa_st = dfa.next(dfa_st, sym)
        if next_dfa_st == None:
            if sym not in dfa.alphabet: 
                next_dfa_st = dfa.next(dfa_st, "A")
                if next_dfa_st == None:
                    return False, transitions
            else:
                return False, transitions
        
        gr_dfa_states[gr_st] = dfa_st
        if next_gr_st in gr_dfa_states.keys():
            if gr_dfa_states[next_gr_st] != next_dfa_st:
                if subs(gr.transitions.get_transitions_sym(next_gr_st), dfa.transitions.get_transitions_sym(next_dfa_st)):
                    is_correct, transitions = match(gr, dfa, next_gr_st, next_dfa_st, gr_dfa_states, transitions)
                    if not is_correct:            
                        return False, transitions
                else:
                    return False, transitions
            transitions.add_transition(gr_st, sym, next_gr_st)
            continue
        

        transitions.add_transition(gr_st, sym, next_gr_st)
        is_correct, transitions = match(gr, dfa, next_gr_st, next_dfa_st, gr_dfa_states, transitions)
        if not is_correct:            
            res = False
    return res, transitions


if __name__ == "__main__":

    dir = "Result graph/"

    ciao_json_file = 'ciao.json'
    ciao_programm_file = 'ciao_program.ciao'
    ast = GetAST(ciao_json_file, ciao_programm_file, False)
    graph = build_semantic_graph(ast, False)
    graph.render(dir+"semantic_graph")    

    cre_json_file = 'cre.json'
    cre_file = 'cre.txt'
    ast = GetAST(cre_json_file, cre_file, False)
    dfa  = get_min_dfa(ast, is_render_all=False)
    dfa.render(dir + "min_dfa")

    is_correct, transitions = match(graph, dfa, graph.start_state, dfa.start_state, {}, TransitionsDfa())
    print(is_correct)
    if not is_correct:
        render_match_result(graph, transitions, dir+"verification_result")
        