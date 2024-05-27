from enum import Enum
from digraph import TransitionsDfa

class Type(Enum):
    TOKEN = 'TOKEN'
    NONTERMINAL = 'NONTERMINAL'


def type(ast):
    return ast.type.name


def name_nonterminal(ast):
    return ast.nonterminalType.name


def name_token(ast):
    return ast.token.str


def name(ast):
    if type(ast) == Type.NONTERMINAL.value:
        return name_nonterminal(ast)
    else:
        return name_token(ast)
    

def get_objects(ast):
    objects = {}
    objects_ast = ast.childs[-2].childs[1].childs[1:]
    for obj in objects_ast:
        obj_name = name_token(obj.childs[0])
        class_name = name_token(obj.childs[3])
        start_state = name_token(obj.childs[-2].childs[0])
        objects[obj_name] = [class_name, start_state]
    return objects


def get_interface(ast, is_param):
    interface = name_token(ast.childs[0])
    if not is_param or len(ast.childs) == 1:
        return interface
    interface+= "("
    flag_first = False
    for ch in ast.childs[2::2]:
        if flag_first:
            interface+= ","
        interface+=name_token(ch.childs[0])
    flag_first = True
    interface+= ")"
    return interface


def get_initial(ast, is_param):
    interfaces_ast = ast.childs[-2].childs[-1]
    if len(interfaces_ast.childs) > 0:
        if name_token(interfaces_ast.childs[0]) == "public":
            initial_object = name_token(interfaces_ast.childs[1])
            #initial_event = get_interface(interfaces_ast.childs[3], is_param)
            return initial_object
    return None, None


def get_links(ast, is_param):
    links_ast = ast.childs[-2].childs[2].childs[1:]
    links = {}
    for link in links_ast:
        to_obj = name_token(link.childs[0])
        from_obj = name_token(link.childs[2])
        command = get_interface(link.childs[4], is_param)
        if links.get(to_obj) == None:
            links[to_obj] = [[from_obj],[command]]
        else:
            links[to_obj][0].append(from_obj)
            links[to_obj][1].append(command)
    return links


def get_expression(ast):
    match len(ast.childs):
        case 1:
            return name_token(ast.childs[0])
        case 2:
            return "!" + get_expression(ast.childs[1])
        case 3:
            if type(ast) == Type.TOKEN.value:
                return "(" + get_expression(ast.childs[1]) + ")"
            else:
                return get_expression(ast.childs[0]) + \
                    name_token(ast.childs[1]) + get_expression(ast.childs[2]) 


def get_call(ast, is_param):
    call = name_token(ast.childs[0]) 
    if not is_param or len(ast.childs) == 1:
        return call
    call += "("
    flag_first = False
    for ch in ast.childs[2::2]:
        if flag_first:
            call+= ","
        call+= get_expression(ch)
    flag_first = True
    call+= ")"
    return call


def get_actions(ast, is_param):
    actions = []
    for ch in ast.childs[0::2]:
        match name_nonterminal(ch):
            case "CALL" :
                actions.append(get_call(ch, is_param))
            case "ASSIGNMENT":
                actions.append(name_token(ch.childs[0]) /
                               + ":=" + get_expression(ch.childs[2]))
    return actions


def add_actions_tr(actions, num_states, next_state, num, class_states):
    for act in actions[:-1]:
        class_states.add_transition(num, act, num + 1)
        num+=1
    prew_num = num
    num, num_states = add_state(num_states, next_state, num + 1)
    class_states.add_transition(prew_num, actions[-1], num_states[next_state])
    return max(num, prew_num) + 1, class_states


def add_state(num_states, state, num):
    if num_states.get(state) == None: 
        num_states[state] = num
        num+=1
    return num, num_states


def get_states(ast, objects, is_param):
    states = {}
    num = 0
    for a_class in ast.childs[2:-2]:
        class_name = name_token(a_class.childs[1])
        class_states = TransitionsDfa()
        num_states = {} # назначение номеров именованным состояниям во избежание их повторения в разных АО
        for st in a_class.childs[-1].childs[1:]:
            state_name = name_token(st.childs[0])
            num, num_states = add_state(num_states, state_name, num)
            for tr in st.childs[1:]:
                call = get_call(tr.childs[1], is_param)
                class_states.add_transition(num_states[state_name], call, num)
                match name_nonterminal(tr.childs[2]):
                    case "STRIGHT":
                        next_state = name_token(tr.childs[2].childs[-1])
                        if len(tr.childs[2].childs) == 4:
                            actions = get_actions(tr.childs[2].childs[1], is_param)
                            num, class_states = add_actions_tr(actions, num_states, next_state, num, class_states)
                        else:
                            num, num_states = add_state(num_states, next_state, num)
                            class_states.add_transition(num_states[state_name], call, num_states[next_state])
                    case "DECISION":
                        if name_nonterminal(tr.childs[2].childs[1]) == "CALL":
                            cond = get_call(tr.childs[2].childs[1], is_param)
                        else:
                            cond = get_expression(tr.childs[2].childs[1])
                        num_if_else = num
                        num +=1
                        class_states.add_transition(num_if_else, "[" + cond + "]", num)
                        actions_if = get_actions(tr.childs[2].childs[4], is_param)
                        state_if = name_token(tr.childs[2].childs[6])
                        num, class_states = add_actions_tr(actions_if, num_states, state_if, num, class_states)

                        class_states.add_transition(num_if_else, "[!" + cond + "]", num)
                        actions_else = get_actions(tr.childs[2].childs[-3], is_param)
                        state_else = name_token(tr.childs[2].childs[-1])
                        num, class_states = add_actions_tr(actions_else, num_states, state_else, num, class_states)
        states.update({class_name : class_states}) 

        for obj, [cl,st] in objects.items():
            if cl == class_name:
                objects[obj] = [cl, num_states[st]]
            
    return states, objects, num
