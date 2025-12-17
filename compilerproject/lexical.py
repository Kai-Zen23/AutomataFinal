
import collections

# -----------------------------------------------------------------------------
# AUTOMATA STRUCTURES (Lexical)
# -----------------------------------------------------------------------------

class State:
    def __init__(self, name=None, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = collections.defaultdict(list)

    def add_transition(self, symbol, state):
        self.transitions[symbol].append(state)

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

    def get_steps(self):
        # BFS to record transitions for visualization
        visited = set()
        queue = [self.start]
        visited.add(self.start)
        steps = []
        
        while queue:
            current = queue.pop(0)
            for symbol, next_states in current.transitions.items():
                for ns in next_states:
                    steps.append({
                        "from": current.name,
                        "to": ns.name,
                        "label": "ε" if symbol == '' else symbol
                    })
                    if ns not in visited:
                        visited.add(ns)
                        queue.append(ns)
        return steps

class DFA:
    def __init__(self, states, start, accept_states):
        self.states = states
        self.start = start
        self.accept_states = accept_states
        self.transitions = {} # (state, symbol) -> state

    def get_steps(self):
        steps = []
        # We need to flatten the (state, symbol) -> next_state map
        for (state, symbol), next_state in self.transitions.items():
             steps.append({
                "from": str(state),
                "to": str(next_state),
                "label": symbol
            })
        return steps

# -----------------------------------------------------------------------------
# ALGORITHMS (Regex -> NFA -> DFA)
# -----------------------------------------------------------------------------

# Regex Postfix Parser for Shunting-yard algorithm
def to_postfix(regex):
    output = []
    stack = []
    # Simplified handling: add explicit concatenation '.'
    formatted_regex = ""
    for i in range(len(regex)):
        c = regex[i]
        formatted_regex += c
        if i + 1 < len(regex):
            next_c = regex[i+1]
            if c != '(' and c != '|' and next_c != '|' and next_c != '*' and next_c != ')' and next_c != '+':
                 formatted_regex += '.'
    
    precedence = {'*': 3, '+': 3, '.': 2, '|': 1}
    
    for char in formatted_regex:
        if char.isalnum() or char == '_':
            output.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop() # Pop '('
        else:
            while stack and stack[-1] != '(' and precedence.get(stack[-1], 0) >= precedence.get(char, 0):
                output.append(stack.pop())
            stack.append(char)
            
    while stack:
        output.append(stack.pop())
    return output

# Thompson's Construction
def regex_to_nfa(regex):
    postfix = to_postfix(regex)
    stack = []
    state_counter = 0

    def new_state():
        nonlocal state_counter
        s = State(str(state_counter))
        state_counter += 1
        return s

    for char in postfix:
        if char.isalnum() or char == '_':
            start = new_state()
            end = new_state()
            start.add_transition(char, end)
            stack.append(NFA(start, end))
        elif char == '.':
            n2 = stack.pop()
            n1 = stack.pop()
            n1.accept.add_transition('', n2.start)
            stack.append(NFA(n1.start, n2.accept))
        elif char == '|':
            n2 = stack.pop()
            n1 = stack.pop()
            start = new_state()
            end = new_state()
            start.add_transition('', n1.start)
            start.add_transition('', n2.start)
            n1.accept.add_transition('', end)
            n2.accept.add_transition('', end)
            stack.append(NFA(start, end))
        elif char == '*':
            n1 = stack.pop()
            start = new_state()
            end = new_state()
            start.add_transition('', n1.start)
            start.add_transition('', end)
            n1.accept.add_transition('', n1.start)
            n1.accept.add_transition('', end)
            stack.append(NFA(start, end))
        elif char == '+': # a+ = aa*
             n1 = stack.pop()
             # We clone logic or simpler: construct new structure
             # For simplicity, treat a+ as a followed by a* logic but standard construction:
             # Just * logic but without the empty start->end path
             start = new_state()
             end = new_state()
             start.add_transition('', n1.start)
             n1.accept.add_transition('', n1.start)
             n1.accept.add_transition('', end)
             stack.append(NFA(start, end))

    if stack:
        nfa = stack.pop()
        nfa.accept.is_final = True
        return nfa
    return None

# Subset Construction
def nfa_to_dfa(nfa):
    # Inputs (approximate for demo)
    inputs = set()
    # Collect inputs
    queue = [nfa.start]
    visited = {nfa.start}
    while queue:
        curr = queue.pop(0)
        for sym in curr.transitions:
            if sym != '': inputs.add(sym)
            for n in curr.transitions[sym]:
                if n not in visited:
                    visited.add(n)
                    queue.append(n)
    
    # Epsilon Closure
    def get_epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        while stack:
            s = stack.pop()
            if '' in s.transitions:
                for next_s in s.transitions['']:
                    if next_s not in closure:
                        closure.add(next_s)
                        stack.append(next_s)
        return closure

    start_closure = get_epsilon_closure([nfa.start])
    
    # DFA States mapping: frozenset(nfa_states) -> DFA State ID
    dfa_states = {}
    unmarked_states = [start_closure]
    dfa_states[frozenset(start_closure)] = 0
    state_counter = 1
    
    dfa = DFA(states={}, start=0, accept_states=set())
    
    while unmarked_states:
        current_closure = unmarked_states.pop(0)
        current_id = dfa_states[frozenset(current_closure)]
        
        # Check if accepting
        for s in current_closure:
            if s.is_final:
                dfa.accept_states.add(current_id)
                break
        
        for char in sorted(inputs):
            # Move
            next_states = set()
            for s in current_closure:
                if char in s.transitions:
                    for ns in s.transitions[char]:
                        next_states.add(ns)
            
            # Epsilon closure of result
            next_closure = get_epsilon_closure(next_states)
            
            if not next_closure:
                continue
                
            frozen_next = frozenset(next_closure)
            if frozen_next not in dfa_states:
                dfa_states[frozen_next] = state_counter
                state_counter += 1
                unmarked_states.append(next_closure)
            
            dfa.transitions[(current_id, char)] = dfa_states[frozen_next]
            
    return dfa
