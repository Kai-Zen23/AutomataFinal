#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <regex>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <vector>

using namespace std;

// ============================================================================
// 1. LEXICAL ANALYSIS (SCANNER)
// ============================================================================

struct Token {
  string type;
  string value;
};

class Lexer {
public:
  /**
   * Scans the input string and converts it into a stream of tokens based on
   * predefined regex rules.
   *
   * @param input The source code string to be analyzed.
   * @return A vector of Token objects representing the identified lexemes.
   */
  vector<Token> tokenize(const string &input) {
    vector<Token> tokens;
    // Define regex rules for various token types
    vector<pair<string, regex>> rules = {
        {"NUMBER", regex(R"(^[0-9]+(\.[0-9]+)?)")},
        {"INDENTIFIER", regex(R"(^[a-zA-Z_][a-zA-Z0-9_]*)")},
        {"LPAREN", regex(R"(^\()")},
        {"RPAREN", regex(R"(^\))")},
        {"LBRACE", regex(R"(^\{)")},
        {"RBRACE", regex(R"(^\})")},
        {"LBRACKET", regex(R"(^\[)")},
        {"RBRACKET", regex(R"(^\])")},
        {"ALTERNATION", regex(R"(^\|)")},
        {"PLUS", regex(R"(^\+)")},
        {"MINUS", regex(R"(^-)")},
        {"MULTIPLY", regex(R"(^\*)")},
        {"DIVIDE", regex(R"(^/)")},
        {"ASSIGN", regex(R"(^=)")},
        {"COMMA", regex(R"(^,)")},
        {"WS", regex(R"(^\s+)")}};

    size_t pos = 0;
    while (pos < input.length()) {
      string substr = input.substr(pos);
      bool matched = false;
      for (const auto &rule : rules) {
        smatch match;
        // Attempt to match the current substring against the regex rule
        if (regex_search(substr, match, rule.second)) {
          string val = match.str();
          if (rule.first != "WS") { // Skip whitespace
            // Special Case: Split Identifiers into chars for PDA Visualization
            // 'push 1 by 1'
            if (rule.first == "INDENTIFIER" && val.length() > 1) {
              for (char c : val) {
                string s(1, c);
                tokens.push_back({rule.first, s});
                cout << "SCANNER: Found " << rule.first << " '" << s << "'"
                     << endl;
              }
            } else {
              tokens.push_back({rule.first, val});
              cout << "SCANNER: Found " << rule.first << " '" << val << "'"
                   << endl;
            }
          }
          pos += val.length();
          matched = true;
          break;
        }
      }
      if (!matched) {
        cout << "SCANNER: ERROR - Unknown symbol '" << substr[0] << "'" << endl;
        pos++;
      }
    }
    return tokens;
  }
};

// ============================================================================
// 2. AUTOMATA (NFA/DFA) - From Regex
// ============================================================================

struct State {
  int id;
  bool isFinal;
  map<string, vector<State *>> transitions;

  State(int i) : id(i), isFinal(false) {}

  /**
   * Adds a transition from this state to another state on a given symbol.
   *
   * @param symbol The input symbol triggering the transition (empty string for
   * epsilon).
   * @param next The destination state.
   */
  void addTransition(string symbol, State *next) {
    transitions[symbol].push_back(next);
  }
};

class NFA {
public:
  State *start;
  State *accept;
  vector<State *> allStates;
  static int stateCounter;

  NFA(State *s, State *a) : start(s), accept(a) {}

  /**
   * Creates a new unique NFA state.
   *
   * @return A pointer to the newly created State object.
   */
  static State *newState() {
    State *s = new State(stateCounter++);
    return s;
  }

  /**
   * Traverses the NFA using BFS and prints all transitions to standard output.
   * This output is parsed by the GUI to visualize the NFA structure.
   */
  void printEdges() {
    // BFS to print all edges
    set<int> visited;
    queue<State *> q;
    q.push(start);
    visited.insert(start->id);

    while (!q.empty()) {
      State *curr = q.front();
      q.pop();

      if (curr->isFinal) {
        cout << "NFA_FINAL: " << curr->id << endl;
      }

      for (auto const &[sym, targets] : curr->transitions) {
        string label = (sym == "" ? "EPS" : sym);
        for (State *next : targets) {
          // Output "NFA_EDGE" marker for the Python GUI to parse and draw the
          // graph.
          cout << "NFA_EDGE: " << curr->id << " --(" << label << ")--> "
               << next->id << endl;
          if (visited.find(next->id) == visited.end()) {
            visited.insert(next->id);
            q.push(next);
          }
        }
      }
    }
  }

  /**
   * Helper to collect all unique states reachable from start
   */
  void collectStates(State *root, set<State *> &visited) {
    if (visited.count(root))
      return;
    visited.insert(root);
    allStates.push_back(root);

    for (auto const &[sym, targets] : root->transitions) {
      for (State *next : targets) {
        collectStates(next, visited);
      }
    }
  }

  /**
   * Populates allStates vector for the DFA generator
   */
  void indexStates() {
    set<State *> visited;
    allStates.clear();
    collectStates(start, visited);
  }

  /**
   * Renumbers states so that the start state is 0 and others follow BFS order.
   * This ensures a clean, predictable diagram and output list.
   */
  void renumberStates() {
    map<State *, int> newIds;
    queue<State *> q;
    int currentId = 0;

    // Start with the start node
    q.push(start);
    newIds[start] = currentId++;

    while (!q.empty()) {
      State *curr = q.front();
      q.pop();

      // Assign ID if not already done (though for BFS we usually assign on
      // push) Actually, for better ordering, we assign when we first see them.

      // Sort transitions to ensure deterministic numbering for parallel edges
      // processing if needed, but map iteration is sorted by key (symbol).

      for (auto const &[sym, targets] : curr->transitions) {
        for (State *next : targets) {
          if (newIds.find(next) == newIds.end()) {
            newIds[next] = currentId++;
            q.push(next);
          }
        }
      }
    }

    // Apply new IDs
    // We also need to iterate over ALL states in case some are unreachable
    // (though Thompson's construction usually produces connected graphs,
    // disconnected parts might exist if we did optimizations, but here safe to
    // just renumber reachable).
    for (auto const &[state, id] : newIds) {
      state->id = id;
    }
  }
};
int NFA::stateCounter = 0;

/**
 * Converts an infix regular expression to postfix notation using the
 * Shunting-yard algorithm. It also inserts explicit concatenation operators
 * ('.') where implicit concatenation occurs.
 *
 * @param regexStr The input regular expression (infix).
 * @return The postfix representation of the regex.
 */
string toPostfix(string regexStr) {
  string output = "";
  stack<char> opStack;
  // Pre-formatting: insert explicit concatenation '.'
  string formatted = "";
  for (size_t i = 0; i < regexStr.length(); i++) {
    char c = regexStr[i];
    formatted += c;
    if (i + 1 < regexStr.length()) {
      char next = regexStr[i + 1];
      if (c != '(' && c != '|' && next != '|' && next != '*' && next != ')' &&
          next != '+') {
        formatted += '.';
      }
    }
  }

  map<char, int> prec = {{'*', 3}, {'+', 3}, {'.', 2}, {'|', 1}};

  for (char c : formatted) {
    if (isalnum(c) || c == '_') {
      output += c;
    } else if (c == '(') {
      opStack.push(c);
    } else if (c == ')') {
      while (!opStack.empty() && opStack.top() != '(') {
        output += opStack.top();
        opStack.pop();
      }
      if (!opStack.empty())
        opStack.pop();
    } else {
      while (!opStack.empty() && opStack.top() != '(' &&
             prec[opStack.top()] >= prec[c]) {
        output += opStack.top();
        opStack.pop();
      }
      opStack.push(c);
    }
  }
  while (!opStack.empty()) {
    output += opStack.top();
    opStack.pop();
  }
  return output;
}

/**
 * Constructs an NFA from a regex string using Thompson's Construction
 * algorithm.
 *
 * @param regexStr The regular expression string.
 * @return A pointer to the resulting NFA object, or nullptr if construction
 * failed.
 */
NFA *regexToNFA(string regexStr) {
  string postfix = toPostfix(regexStr);
  stack<NFA *> stack;
  NFA::stateCounter = 0; // Reset

  for (char c : postfix) {
    if (isalnum(c) || c == '_') {
      State *start = NFA::newState();
      State *end = NFA::newState();
      string sym(1, c);
      start->addTransition(sym, end);
      stack.push(new NFA(start, end));
    } else if (c == '.') { // Concat
      if (stack.size() < 2)
        return nullptr;
      NFA *n2 = stack.top();
      stack.pop();
      NFA *n1 = stack.top();
      stack.pop();

      // Optimization: Merge n1->accept with n2->start
      // Redirect edges from n2->start to n1->accept
      for (auto const &[sym, targets] : n2->start->transitions) {
        for (State *t : targets) {
          n1->accept->addTransition(sym, t);
        }
      }
      // If n2->start was acting as a final state (rare in this constr.),
      // propagate finality But typically we just use n2->accept as the new
      // accept. n2->start is effectively removed from the graph flow.

      stack.push(new NFA(n1->start, n2->accept));
      // Optionally delete n2->start if proper memory management were in place

    } else if (c == '|') { // Union
      if (stack.size() < 2)
        return nullptr;
      NFA *n2 = stack.top();
      stack.pop();
      NFA *n1 = stack.top();
      stack.pop();

      State *start = NFA::newState();
      State *end = NFA::newState();

      // Optimization: Start state copies transitions of sub-NFAs instead of
      // epsilon branching This avoids "start --eps--> n1.start" chain. Valid
      // because n1.start/n2.start are fresh entry points from stack.
      for (auto const &[sym, targets] : n1->start->transitions) {
        for (State *t : targets)
          start->addTransition(sym, t);
      }
      for (auto const &[sym, targets] : n2->start->transitions) {
        for (State *t : targets)
          start->addTransition(sym, t);
      }

      n1->accept->addTransition("", end);
      n2->accept->addTransition("", end);
      stack.push(new NFA(start, end));

    } else if (c == '*') { // Kleene Star
      if (stack.empty())
        return nullptr;
      NFA *n1 = stack.top();
      stack.pop();
      State *start = NFA::newState();
      State *end = NFA::newState();
      start->addTransition("", n1->start);
      start->addTransition("", end);
      n1->accept->addTransition("", n1->start);
      n1->accept->addTransition("", end);
      stack.push(new NFA(start, end));

    } else if (c == '+') { // One or More
      if (stack.empty())
        return nullptr;
      NFA *n1 = stack.top();
      stack.pop();
      // Optimization: A+ is just A with a loop back from accept to start
      // No new states needed.
      n1->accept->addTransition("", n1->start);
      stack.push(new NFA(n1->start, n1->accept));
    }
  }

  if (!stack.empty()) {
    NFA *res = stack.top();
    res->accept->isFinal = true;
    res->renumberStates();
    res->indexStates();
    return res;
  }
  return nullptr;
}

// --- DFA SUBSET CONSTRUCTION HELPERS ---

/**
 * Computes epsilon closure for a set of NFA states.
 * @param states Input set of states.
 * @return Set of states reachable via epsilon transitions.
 */
set<State *> epsilonClosure(const set<State *> &states) {
  set<State *> closure = states;
  stack<State *> worklist;
  for (State *s : states)
    worklist.push(s);

  while (!worklist.empty()) {
    State *s = worklist.top();
    worklist.pop();

    // Find epsilon transitions ("")
    if (s->transitions.count("")) {
      for (State *next : s->transitions.at("")) {
        if (closure.find(next) == closure.end()) {
          closure.insert(next);
          worklist.push(next);
        }
      }
    }
  }
  return closure;
}

/**
 * Computes the set of states reachable from 'states' on symbol 'symbol'.
 * @param states Input set of NFA states.
 * @param symbol The transition symbol.
 * @return Set of next states.
 */
set<State *> move(const set<State *> &states, string symbol) {
  set<State *> result;
  for (State *s : states) {
    if (s->transitions.count(symbol)) {
      for (State *next : s->transitions.at(symbol)) {
        result.insert(next);
      }
    }
  }
  return result;
}

/**
 * Generates a DFA from the given NFA using Subset Construction.
 * Replaces the previous mock implementation with the standard algorithm.
 *
 * @param nfa The NFA to convert.
 */
void generateDFA(NFA *nfa) {
  // 1. Identify Alphabet (skip epsilon)
  set<string> alphabet;
  for (State *s : nfa->allStates) {
    for (auto const &[sym, targets] : s->transitions) {
      if (!sym.empty())
        alphabet.insert(sym);
    }
  }

  // 2. Initial State = epsilonClosure({nfa->start})
  set<State *> startSet = {nfa->start};
  set<State *> dfaStart = epsilonClosure(startSet);

  // DFA States Management
  // We use vector<set<State*>> to store D-states, index is ID.
  vector<set<State *>> dStates;
  dStates.push_back(dfaStart);

  // To quick check if a set exists (map set -> int ID)
  map<set<State *>, int> dStateToId;
  dStateToId[dfaStart] = 0;

  queue<int> q; // Queue of DFA state IDs to process
  q.push(0);

  // Store Transitions: dfaTransitions[fromID][symbol] = toID
  map<int, map<string, int>> dfaTransitions;

  // Store Final States IDs
  set<int> finalStates;
  // Check if start state is final
  bool startIsFinal = false;
  for (State *s : dfaStart)
    if (s->isFinal)
      startIsFinal = true;
  if (startIsFinal)
    finalStates.insert(0);

  // 3. Main Loop
  while (!q.empty()) {
    int uID = q.front();
    q.pop();

    set<State *> u = dStates[uID];

    for (const string &symbol : alphabet) {
      set<State *> moved = move(u, symbol);
      set<State *> v = epsilonClosure(moved);

      if (v.empty())
        continue; // Dead state, usually ignore in simple viz, or implicit trap

      if (dStateToId.find(v) == dStateToId.end()) {
        // New DFA State found
        int vID = dStates.size();
        dStates.push_back(v);
        dStateToId[v] = vID;
        q.push(vID);

        // Check if accepting
        for (State *s : v) {
          if (s->isFinal) {
            finalStates.insert(vID);
            break;
          }
        }
      }

      // Record Transition
      dfaTransitions[uID][symbol] = dStateToId[v];
    }
  }

  // 4. Output Results for Visualizer

  // Print Final States
  for (int id : finalStates) {
    cout << "DFA_FINAL: " << id << endl;
  }

  // Print Edges
  for (auto const &[uID, trans] : dfaTransitions) {
    for (auto const &[sym, vID] : trans) {
      // Output "DFA_EDGE" marker for the Python GUI.
      cout << "DFA_EDGE: " << uID << " --(" << sym << ")--> " << vID << endl;
    }
  }
}

// ============================================================================
// 3. SYNTACTIC ANALYSIS (PDA / PARSER)
// ============================================================================

class Parser {
  vector<string> stack;
  int stepCount = 0;

public:
  /**
   * Logs a step of the PDA execution to standard output for the GUI visualizer.
   *
   * @param action The action performed (e.g., SHIFT, REDUCE).
   * @param desc A description of the action.
   */
  void log(string action, string desc) {
    cout << "PDA_STEP: " << ++stepCount << " | " << action << " | [";
    for (size_t i = 0; i < stack.size(); i++) {
      cout << stack[i] << (i < stack.size() - 1 ? ", " : "");
    }
    cout << "] | " << desc << endl;
  }

  /**
   * Determines the precedence of an operator.
   *
   * @param op The operator string.
   * @return An integer representing precedence level (higher is stronger).
   */
  int precedence(string op) {
    if (op == "*" || op == "/")
      return 2;
    if (op == "+" || op == "-")
      return 1;
    return 0;
  }

  /**
   * Parses the stream of tokens using a Pushdown Automaton (Shift-Reduce
   * style). Validates the input against the grammar rules.
   *
   * @param tokens The vector of tokens to parse.
   */
  void parse(const vector<Token> &tokens) {
    stepCount = 0;
    stack.clear();
    log("START", "Initialize PDA");

    for (size_t i = 0; i < tokens.size(); ++i) {
      const auto &t = tokens[i];

      if (t.type == "NUMBER" || t.type == "LITERAL" ||
          t.type == "INDENTIFIER") {
        // Regex Literal / Identifier: Push to stack (Implicit Concat)
        stack.push_back(t.value);
        log("SHIFT", "Read " + t.value);

      } else if (t.type == "LPAREN") {
        stack.push_back("(");
        log("PUSH", "Group Start '('");

      } else if (t.type == "RPAREN") {
        // Reduce internal group
        bool found = false;
        // Pop until matching '('
        // For visualization: we just pop everything and say "Reduced Group"
        // In a real Regex PDA, we'd form a Sub-NFA. Here we just visualize
        // structure.
        while (!stack.empty()) {
          string top = stack.back();
          stack.pop_back();
          if (top == "(") {
            found = true;
            log("REDUCE", "Rule: F -> ( E )");
            break;
          }
          log("POP", "Consuming " + top);
        }
        if (!found) {
          log("REJECT", "Unmatched ')'");
          return;
        }

      } else if (t.type == "MULTIPLY" || t.type == "PLUS") {
        // Kleene Star or Plus (Postfix)
        // Acts on the element on top of stack
        if (stack.empty() || stack.back() == "(" || stack.back() == "|") {
          log("REJECT", "Operator " + t.value + " needs operand");
          return;
        }
        string top = stack.back();
        stack.pop_back();
        log("REDUCE", "Rule: F -> " + top + t.value);
        // Push back abstract result? Or just keep going?
        // For "Push 1 by 1", we want the result on stack?
        // stack.push_back(top + t.value);
        // Let's push back a marker
        stack.push_back(top + t.value);

      } else if (t.type == "ALTERNATION") {
        // Union Operator '|'
        // Low precedence. Should reduce existing concats?
        // For strict visualization, just push it.
        stack.push_back("|");
        log("SHIFT", "Union Operator '|'");

      } else if (t.type == "COMMA") {
        // Skip commas
        log("SKIP", "Comma");
      }
    }

    while (!stack.empty()) {
      // Just clear stack
      string op = stack.back();
      stack.pop_back();
      // If we see '(', it's unmatched
      if (op == "(") {
        log("REJECT", "Unmatched '('");
        return;
      }
      // Provide generic reduction log for visualization
      log("REDUCE", "Rule: S -> S . " + op);
    }
    log("ACCEPT", "Input Accepted");
  }

  void printPDAStructure() {
    cout << "PDA_FINAL: State" << endl;
    cout << "PDA_EDGE: Start --(char)--> State" << endl;
    cout << "PDA_EDGE: Start --( '(' )--> Start" << endl;
    cout << "PDA_EDGE: State --(char)--> State" << endl;
    cout << "PDA_EDGE: State --('*')--> State" << endl;
    cout << "PDA_EDGE: State --('|')--> Start" << endl;
    cout << "PDA_EDGE: State --( ')' )--> State" << endl;
  }
};

// ============================================================================
// MAIN DRIVER
// ============================================================================

/**
 * Main entry point of the compiler engine.
 * [UPDATED] Uses C++17 standard features.
 *
 * Usage: compiler_engine <input_code> [regex_pattern]
 *
 * 1. Generates NFA/DFA from the provided regex pattern.
 * 2. Scans the input code to produce tokens.
 * 3. Parses the tokens using the PDA logic.
 *
 * @param argc Argument count.
 * @param argv Argument vector.
 * @return 0 on success, 1 on error.
 */
int main(int argc, char *argv[]) {
  // Demo Mode: If no args are provided, we could default or error.
  // The GUI always provides args.
  if (argc < 2)
    return 1;

  // 1. Generate Automata from Pattern (Standard Mode)
  // ... (Removed valid check to support conditional logic below)

  if (argc >= 4 && string(argv[1]) == "TEST_MODE") {
    string pattern = argv[2];
    NFA *nfa = regexToNFA(pattern);
    if (!nfa) {
      cout << "ERROR: Invalid Regex" << endl;
      return 1;
    }
    // Run simulations
    for (int i = 3; i < argc; i++) {
      string testStr = argv[i];

      // Simulation
      set<State *> current = epsilonClosure({nfa->start});
      for (char c : testStr) {
        string sym(1, c);
        set<State *> next = move(current, sym);
        current = epsilonClosure(next);
      }

      bool accepted = false;
      for (State *s : current) {
        if (s->isFinal) {
          accepted = true;
          break;
        }
      }

      cout << "RESULT: " << testStr << " -> "
           << (accepted ? "Accepted" : "Rejected") << endl;
    }
    return 0;
  }

  string input = argv[1];
  string pattern = (argc > 2) ? argv[2] : "(a|b)*";

  cout << "=== AUTOMATA GEN START ===" << endl;
  NFA *nfa = regexToNFA(pattern);
  if (nfa) {
    nfa->printEdges();
    generateDFA(nfa);
  }

  // 2. Scan Input
  cout << "=== SCANNER START ===" << endl;
  Lexer lexer;
  vector<Token> tokens = lexer.tokenize(input);

  // 3. Parse Input (PDA)
  cout << "=== PARSER START ===" << endl;
  Parser parser;
  parser.printPDAStructure();
  parser.parse(tokens);

  return 0;
}