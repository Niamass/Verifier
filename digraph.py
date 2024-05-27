import graphviz
from copy import deepcopy

class TransitionsNfa():
    def __init__(self, source_state, symbol, target_state):
        self.states = {source_state : {symbol : [target_state]}}

    def get_source_states(self):
        return self.states.keys()
    
    def get_transitions_sym(self, state):
        if self.get_transitions(state)!=None:
            return self.states[state].keys()
        return None
    
    def get_transitions(self, state):
        return self.states.get(state)
    
    def get_next_state(self, state, sym):
        if self.get_transitions(state) != None:
            return self.get_transitions(state).get(sym, [])
        return []
    
    def add_transition(self, source_state, symbol, target_state):
        self.add_transitions(source_state, {symbol : [target_state]})

    def add_transitions(self, source_state, transitions): # transitions = {symbol : [target_state],...}
        if self.get_transitions(source_state) == None:
            self.states[source_state] = transitions
        else:
            for sym in transitions.keys():
                if self.get_next_state(source_state, sym) == []:
                    self.states[source_state][sym] = transitions[sym]
                else:
                    self.get_next_state(source_state, sym).extend(transitions[sym])

    def states_unification(self, other, self_state, other_state):
        for tr in other.states.values():
            for st in tr.values():
                st[:] = [self_state if x==other_state else x for x in st]
        if other.get_transitions(other_state) != None:
            self.add_transitions(self_state, other.get_transitions(other_state))
            del other.states[other_state]
        self.states.update(other.states)

    def rename_states(self, num):
        for st in list(self.get_source_states()):
            self.states[st+num] = self.states.pop(st)
        for sym in self.states.values():
            for n_st in sym.values():
                n_st[:] = [x+num for x in n_st]

    def print(self):
        print(self.states)
    

class NFA():
    def __init__(self, start_state, accept_state, symbol):
        self.start_state = start_state
        self.accept_state = accept_state
        self.transitions = TransitionsNfa(start_state, symbol, accept_state)
        self.alphabet = {symbol}
        self.states = {start_state, accept_state}

    def next_states(self, states, sym):
        next_st = []
        for st in states:
            next_st +=self.transitions.get_next_state(st, sym)
        return next_st
    
    def concatenation(self, dg):
        self.transitions.states_unification(dg.transitions, self.accept_state, dg.start_state)
        self.accept_state = dg.accept_state
        self.union_sets(dg)
        self.states.discard(dg.start_state)
        return self
    
    def alternation(self, dg):
        self.transitions.states_unification(dg.transitions, self.start_state, dg.start_state)
        self.transitions.states_unification(self.transitions, self.accept_state, dg.accept_state)
        self.union_sets(dg)
        self.states.discard(dg.start_state)
        self.states.discard(dg.accept_state)
        return self
    
    def tseitin(self, dg, num):
        self.transitions.states_unification(dg.transitions, self.start_state, dg.accept_state)
        self.transitions.states_unification(self.transitions, self.accept_state, dg.start_state)
        self.union_sets(dg)
        self.states.discard(dg.accept_state)
        self.states.discard(dg.start_state)
        num = self.add_eps_start(num)
        num = self.add_eps_accept(num)
        return num
    
    def tseitin_left(self, num): # _#P = P*
        self.transitions.states_unification(self.transitions, self.start_state, self.accept_state)
        self.states.discard(self.accept_state)
        self.accept_state = self.start_state
        num = self.add_eps_start(num)
        num = self.add_eps_accept(num)
        return num
    
    def tseitin_right(self, num): # P#_ = PP*
        dg = deepcopy(self)
        dg.transitions.states_unification(dg.transitions, dg.start_state, dg.accept_state)
        dg.states.discard(dg.accept_state)
        dg.accept_state = dg.start_state
        num = self.rename_states(num)
        self.transitions.states_unification(dg.transitions, self.accept_state, dg.start_state)
        self.states.update(dg.states)
        self.states.discard(dg.accept_state)
        num = self.add_eps_accept(num)
        return num
    
    def add_eps_start(self, num):
        self.transitions.add_transition(num, 'eps', self.start_state)
        self.start_state = num
        self.states.update({num})
        return num + 1
    
    def add_eps_accept(self, num):
        self.transitions.add_transition(self.accept_state, 'eps', num)
        self.accept_state = num
        self.states.update({num})
        return num + 1
    
    def rename_states(self, num):
        self.start_state +=num
        self.accept_state +=num
        self.transitions.rename_states(num)
        self.states = set([x+num for x in self.states])
        return max(self.states) + 1
    
    def union_sets(self, other):
        self.alphabet.update(other.alphabet)
        self.states.update(other.states)

    def print(self):
        print("start = ", self.start_state, ", accept = ", self.accept_state)
        print("alphabet = ", self.alphabet)
        print("states = ", self.states)
        self.transitions.print()

    def render(self, dir):
        g = graphviz.Digraph()
        source_states = self.transitions.get_source_states()
        g.attr('node', shape='circle', label = '', width='0.3')
        g.node('', _attributes={'fillcolor' : 'black', 'style' : 'filled'})
        g.edge('', str(self.start_state))
        for st in source_states:
            symbols = self.transitions.get_transitions_sym(st)
            for sym in symbols:
                next_st = self.transitions.get_next_state(st, sym)
                for n_st in next_st:
                    g.edge(str(st), str(n_st), label =" "+sym)
        g.node(str(self.accept_state), _attributes={'shape': 'doublecircle', 'fillcolor' : 'black', 'style' : 'filled'})
        
        g.attr('graph', ranksep='0.2', nodesep='0.3')
        g.render(dir, view=True)


class TransitionsDfa():
    def __init__(self):
        self.states = {}

    def get_next_state(self, state, sym):
        if self.get_transitions(state) != None:
            return self.get_transitions(state).get(sym)
        return None
    
    def get_transitions(self, state):
        return self.states.get(state)
    
    def add_transition(self, source_state, symbol, target_state):
        if self.get_transitions(source_state) == None:
            self.states[source_state] = {symbol:target_state}
        else:
            self.states[source_state][symbol] = target_state
                
    def get_source_states(self):
        return self.states.keys()
    
    def get_transitions_sym(self, state):
        if self.get_transitions(state)!=None:
            return list(self.states[state].keys())
        return []
    
    def del_transition(self, source_state, symbol):
        if self.get_next_state(source_state, symbol)!=None:
            del self.states[source_state][symbol]
            if self.states[source_state] != None:
                return
            del self.states[source_state]

    def add_states(self, other): 
        self.states.update(other.states)

    def print(self):
        print(self.states)
    

class DFA():
    def __init__(self, start_state, accept_states, alphabet, transitions, states):
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.transitions = transitions
        self.alphabet = set(alphabet)
        self.states = set(states)

    def next(self, state, sym):
        return self.transitions.get_next_state(state, sym)
    
    def render(self, dir):
        g = graphviz.Digraph()
        source_states = self.transitions.get_source_states()
        g.attr('node', shape='circle', label = '', width='0.3')
        g.node('', _attributes={'fillcolor' : 'black', 'style' : 'filled'})
        g.edge('', str(self.start_state))
        for st in source_states:
            symbols = self.transitions.get_transitions_sym(st)
            for sym in symbols:
                next_st = self.transitions.get_next_state(st, sym)
                g.edge(str(st), str(next_st), label = " "+sym)
        for ac_st in self.accept_states:
            g.node(str(ac_st), _attributes={'shape': 'doublecircle', 'fillcolor' : 'black', 'style' : 'filled'})

        g.attr('graph', ranksep='0.2', nodesep='0.3')
        g.render(dir, view=True)
      
