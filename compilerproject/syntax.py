
# -----------------------------------------------------------------------------
# PARSER STRUCTURES (Syntactic)
# -----------------------------------------------------------------------------

# PDA simulating a Calculator Grammar
# E -> E + T | T
# T -> T * F | F
# F -> ( E ) | num | id
#
# Simplified for visualization: We'll use a stack trace of a shift-reduce parser simulation
# or a simple precedence climbing trace.
class CalculatorPDA:
    def __init__(self):
        self.steps = []
        self.stack = []
        self.state = "q0"

    def log(self, action, desc):
        self.steps.append({
            "action": action,
            "stack": list(self.stack), # copy
            "state": self.state,
            "description": desc
        })

    def parse(self, tokens):
        # tokens: list of (type, value)
        # Using a simple operator precedence or shunting yard trace for the "PDA equivalent" 
        # since actual PDA tables are huge.
        
        self.steps = []
        self.stack = []
        self.state = "q0"
        
        # Precedence map including new regex operators
        prec = {
            'ALTERNATION': 0, '|': 0,
            'PLUS': 1, 'MINUS': 1, '+': 1, '-': 1,
            'STAR': 2, 'DIVIDE': 2, '*': 2, '/': 2,
            'DOT': 2, # Explicit concat
        }
        
        self.log("START", "Initialize PDA")
        
        for type, val in tokens:
            # 1. Operands (Numbers, Literals/Identifiers)
            if type in ('NUMBER', 'IDENTIFIER', 'LITERAL'):
                self.log("SHIFT", f"Read operand '{val}'")
            
            # 2. Operators (Math + Regex Alternation/Kleene)
            elif type in ('OPERATOR', 'PLUS', 'MINUS', 'STAR', 'DIVIDE', 'ALTERNATION', 'DOT'):
                # Handle generic operators
                while (self.stack and 
                       self.stack[-1] not in ('(', 'LPAREN', 'LBRACE') and 
                       prec.get(self.stack[-1], 0) >= prec.get(type, prec.get(val, 0))): # Use type or val for lookup
                    
                    op = self.stack.pop()
                    self.log("POP", f"Pop operator '{op}'")
                    self.log("REDUCE", f"Apply rule T -> T {op} F")
                
                # Push the current operator (store value or type? Store value for visual)
                self.stack.append(val if val else type) 
                self.state = "q1"
                self.log("PUSH", f"Push operator '{val}'")

            # 3. Left Parenthesis
            elif type in ('LPAREN', 'LBRACE') or val == '(':
                self.stack.append('(') # Normalize to '('
                self.log("PUSH", f"Push '('")
                
            # 4. Right Parenthesis
            elif type in ('RPAREN', 'RBRACE') or val == ')':
                while self.stack and self.stack[-1] != '(':
                    op = self.stack.pop()
                    self.log("POP", f"Pop operator '{op}'")
                    self.log("REDUCE", f"Apply rule T -> T {op} F")
                
                if self.stack and self.stack[-1] == '(':
                    self.stack.pop() # Pop (
                    self.log("POP", f"Pop matching '('")
                    self.log("REDUCE", "Reduce ( E ) to F")
                else:
                    self.log("ERROR", "Unmatched closing parenthesis")
                    self.steps[-1]["action"] = "REJECT" # Mark as reject
                    return self.steps
                    
            # 5. Ignored structural tokens (Comma, Brackets handled loosely or ignored)
            elif type in ('COMMA', 'LBRACKET', 'RBRACKET', 'WS'):
                 self.log("SKIP", f"Skipping token '{val}' (Not used in Calc PDA)")
            
            else:
                 # Fallback for old tokens or unknown
                 if val in '()':
                     pass # handled above
                 else:
                     self.log("SHIFT", f"Read unknown '{val}'")
        
        while self.stack:
            if self.stack[-1] == '(':
                self.log("ERROR", "Unbalanced parenthesis")
                return self.steps
            op = self.stack.pop()
            self.log("POP", f"Pop remaining operator '{op}'")
            self.log("REDUCE", f"Apply rule E -> E {op} T")
            
        self.state = "qAccept"
        self.log("ACCEPT", "Input accepted")
        return self.steps
