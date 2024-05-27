from build_ast import GetAST
from dsl_info_cre import Nonterminal
from ast_interface import Type, type, name_nonterminal, name_token, name
from digraph import NFA, DFA, TransitionsDfa


def ast_to_nfa(ast, num):
    match type(ast):
        case Type.TOKEN.value:
            dg = NFA(num, num+1, name_token(ast))
            num += 2
            return dg, num
        case Type.NONTERMINAL.value:
            match name_nonterminal(ast):
                case Nonterminal.CRE.value:
                    dg1, num = ast_to_nfa(ast.childs[0], num)
                    for ch in ast.childs[2::2]:
                        dg2, num = ast_to_nfa(ch, num)
                        dg1.concatenation(dg2)
                    return dg1, num
                case Nonterminal.BRACKETS.value:
                    dg1, num = ast_to_nfa(ast.childs[1], num)
                    for ch in ast.childs[3::2]:
                        dg2, num = ast_to_nfa(ch, num)
                        dg1.alternation(dg2)
                    return dg1, num
                case Nonterminal.TSEITIN_ITERATION.value:
                    if len(ast.childs) == 5:
                        dg1, num = ast_to_nfa(ast.childs[1], num)
                        dg2, num = ast_to_nfa(ast.childs[3], num)
                        num = dg1.tseitin(dg2, num)
                        return dg1, num
                    else:
                        if name(ast.childs[1]) == "#":
                            dg, num = ast_to_nfa(ast.childs[2], num)
                            num = dg.tseitin_left(num)
                            return dg, num
                        else:
                            dg, num = ast_to_nfa(ast.childs[1], num)
                            num = dg.tseitin_right(num)
                            return dg, num


def nfa_to_dfa(nfa):
    states_to_process = [eps_closure([nfa.start_state], nfa.transitions)]
    processed_states = []
    dfa_transitions = TransitionsDfa()
    dfa_states = []
    while len(states_to_process) != 0:
        current_states = states_to_process.pop()
        processed_states.append(current_states)
        if current_states not in dfa_states:
            dfa_states.append(current_states)
        for sym in nfa.alphabet:
            new_states = eps_closure(nfa.next_states(current_states, sym), nfa.transitions)
            if len(new_states) == 0:
                continue
            if new_states not in states_to_process and new_states not in processed_states:
                states_to_process.append(new_states)
            if new_states not in dfa_states:
                dfa_states.append(new_states)
            dfa_transitions.add_transition(dfa_states.index(current_states), sym, dfa_states.index(new_states))
    dfa_accept_states = []
    for i, st in enumerate(dfa_states):
        if nfa.start_state in st:
            dfa_start_state = i
        if nfa.accept_state in st:
            dfa_accept_states.append(i)
    dfa_states = list(range(0,len(dfa_states)))
    return DFA(dfa_start_state, dfa_accept_states, nfa.alphabet, dfa_transitions, dfa_states)


def eps_closure(states, transitions):
    eps_cl = states.copy()
    while len(states)!= 0:
        st = states.pop()
        next_st = transitions.get_next_state(st, 'eps')
        for n_st in next_st:
            if n_st not in eps_cl:
                eps_cl.append(n_st)
                states.append(n_st)
    return eps_cl


def split_states(dfa, states_set, states_set_next, sym):
    S1, S2 = set(), set()
    for st in states_set:
        next_st = dfa.next(st, sym)
        if next_st in states_set_next:
            S1.add(st)
        else:
            S2.add(st)
    return S1, S2


def minimize_dfa(dfa):
    S2 = dfa.accept_states
    S1 = dfa.states.difference(S2)
    states_sets = []
    if len(S1) > 0:
        states_sets.append(S1)
    states_sets.append(S2)
    queue = [S1] if len(S1)< len(S2) else [S2]
    while len(queue) > 0:
        splitter = queue.pop(0)
        for sym in dfa.alphabet:
            for st_s in states_sets:
                S1, S2 = split_states(dfa, st_s, splitter, sym)
                if len(S1) > 0:            
                    if st_s in states_sets:
                        states_sets.remove(st_s)
                    if S1 not in states_sets:
                        states_sets.append(S1)
                    if len(S2) > 0 and S2 not in states_sets:
                        states_sets.append(S2)        
                    if st_s in queue:
                        queue.remove(st_s)
                        queue.append(S1)
                        if len(S2) > 0:
                            queue.append(S2)
                    else:
                        if len(S1) <= len(S2):
                            queue.append(S1)
                        elif len(S1) > len(S2) and len(S2) > 0:
                            queue.append(S2)   
    if len(states_sets) == len(dfa.states):
        return dfa  
    dfa_accept_states = []
    for i, st_s in enumerate(states_sets):
        if dfa.start_state in st_s:
            dfa_start_state = i
        if st_s.intersection(dfa.accept_states):
            dfa_accept_states.append(i)
    dfa_transitions = TransitionsDfa()
    # + удаление состояний, в которые не ведет ни один переход
    for i, st_s in enumerate(states_sets):
        for st in st_s:
            for sym in dfa.transitions.get_transitions_sym(st):
                n = dfa.next(st, sym)
                for s in states_sets:
                    if n in s:
                        next_st = states_sets.index(s)
                        break
                dfa_transitions.add_transition(i, sym, next_st)
    dfa_states = list(range(0,len(states_sets)))
    return DFA(dfa_start_state, dfa_accept_states, dfa.alphabet, dfa_transitions, dfa_states)


def get_min_dfa(ast, is_render_all):
    nfa, _ = ast_to_nfa(ast, 0)
    dfa = nfa_to_dfa(nfa)
    if is_render_all:
        nfa.render("Result graph/nfa")
        dfa.render("Result graph/dfa")
    min_dfa = minimize_dfa(dfa)
    return min_dfa


if __name__ == "__main__":
    jsonFile = 'cre.json'
    codeFile = 'cre.txt'
    ast = GetAST(jsonFile, codeFile, False)
    get_min_dfa(ast)