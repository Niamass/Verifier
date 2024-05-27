from digraph import TransitionsDfa, DFA
from ast_interface import get_objects, get_initial, get_links, get_states
from copy import deepcopy


def build(obj, states, objects, links, graph_tr):
    def get_tr():
        return states[objects[obj][0]]
    def get_cur_st():
        return objects[obj][1]
    def get_link_syms():
        return links[obj][1]
    def get_link_from(sym):
        return links[obj][0][get_link_syms().index(sym)]

    visited_states = set()

    tr = []
    queue = [[obj, objects, tr]]

    while(len(queue) > 0):
        obj, objects, tr = queue.pop()
        state = get_cur_st()
        visited_states.add(state)
        
        syms = get_tr().get_transitions_sym(state)
        if len(syms) == 0:
            continue
        
        if len(tr) > 0 and tr[1] in syms: # предоставляется
            next_st = get_tr().get_next_state(state, tr[1])  
            graph_tr.add_transition(tr[0], tr[1], next_st)
            new_objects = objects.copy()
            new_objects[obj][1] = next_st
            queue.append([obj, new_objects, []])
            continue
        elif len(tr) > 0:
            next_st = get_tr().get_next_state(state, syms[0]) # по грамматике в таком случае всегда один переход
            new_objects = objects.copy()
            new_objects[obj][1] = next_st
            queue.append([obj, new_objects, tr])
            continue
        
        for sym in syms:
            next_st = get_tr().get_next_state(state, sym)    
            new_objects = deepcopy(objects)
            new_objects[obj][1] = next_st
            if sym in get_link_syms(): #требуется у другого
                tr = [state, sym]
                queue.append([get_link_from(sym), new_objects, tr])
            else:
                graph_tr.add_transition(state, sym, next_st)
                if next_st not in visited_states:
                    queue.append([obj, new_objects, tr])
    return graph_tr, visited_states


def build_semantic_graph(ast, is_param):
    objects = get_objects(ast) # {object_name : [class_name, start_state]}
    initial_object = get_initial(ast, is_param)
    if initial_object == None:
        print("Objects don't have public interface")
        return None
    links = get_links(ast, is_param) # {object_to : [objects_from], [commands]}
    states, objects, _ = get_states(ast, objects, is_param) # {class_name : transitions}

    start_state = objects[initial_object][1]
    graph_tr, _ = build(initial_object, states, objects, links, TransitionsDfa())
    
    return DFA(start_state, [], [], graph_tr, [])