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
            tokens.push_back({rule.first, val});
            // Standardized Output for Visualizer
            cout << "SCANNER: Found " << rule.first << " '" << val << "'"
                 << endl;
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
      n1->accept->addTransition("", n2->start);
      stack.push(new NFA(n1->start, n2->accept));
    } else if (c == '|') { // Union
      if (stack.size() < 2)
        return nullptr;
      NFA *n2 = stack.top();
      stack.pop();
      NFA *n1 = stack.top();
      stack.pop();
      State *start = NFA::newState();
      State *end = NFA::newState();
      start->addTransition("", n1->start);
      start->addTransition("", n2->start);
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
    } else if (c == '+') { // One or More (IMPLEMENTED now to handle typical
                           // inputs gracefully)
      if (stack.empty())
        return nullptr;
      NFA *n1 = stack.top();
      stack.pop();
      State *start = NFA::newState();
      State *end = NFA::newState();
      start->addTransition("", n1->start);
      n1->accept->addTransition("", n1->start);
      n1->accept->addTransition("", end);
      stack.push(new NFA(start, end));
    }
  }

  if (!stack.empty()) {
    NFA *res = stack.top();
    res->accept->isFinal = true;
    res->renumberStates(); // <--- NEW CALL
    res->indexStates();    // Populate internal list of all states
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

    for (const auto &t : tokens) {
      if (t.type == "NUMBER" || t.type == "LITERAL") {
        log("SHIFT", "Read operand " + t.value);
      } else if (t.type == "LPAREN") {
        stack.push_back("(");
        log("PUSH", "Push '('");
      } else if (t.type == "RPAREN") {
        while (!stack.empty() && stack.back() != "(") {
          string op = stack.back();
          stack.pop_back();
          log("POP/REDUCE", "Apply T -> T " + op + " F");
        }
        if (!stack.empty()) {
          stack.pop_back();
          log("POP", "Match '('");
        } else {
          log("REJECT", "Unmatched ')' - Stack empty or no matching '('");
          return;
        }
      } else if (t.type == "PLUS" || t.type == "MINUS" ||
                 t.type == "MULTIPLY" || t.type == "DIVIDE") {
        string opVal = t.value;
        while (!stack.empty() && stack.back() != "(" &&
               precedence(stack.back()) >= precedence(opVal)) {
          string p = stack.back();
          stack.pop_back();
          log("POP/REDUCE", "Apply T -> T " + p + " F");
        }
        stack.push_back(opVal);
        log("PUSH", "Push operator " + opVal);
      }
    }

    while (!stack.empty()) {
      string op = stack.back();
      stack.pop_back();
      if (op == "(") {
        log("REJECT", "Unmatched '(' at end of input");
        return;
      }
      log("POP/REDUCE", "Apply E -> E " + op + " T");
    }
    log("ACCEPT", "Input Accepted");
  }
  /**
   * Outputs the static structure of the PDA (State Machine View) for
   * visualization. Since this is a Shift-Reduce parser, we visualize the
   * abstract states.
   */
  void printPDAStructure() {
    cout << "PDA_FINAL: Operand" << endl;
    // Edges format: PDA_EDGE: From --(Label)--> To
    cout << "PDA_EDGE: Start --(number/id)--> Operand" << endl;
    cout << "PDA_EDGE: Start --(Push '(')--> Start" << endl;
    cout << "PDA_EDGE: Operand --(operator)--> Operator" << endl;
    cout << "PDA_EDGE: Operand --(Pop ')')--> Operand" << endl;
    cout << "PDA_EDGE: Operator --(number/id)--> Operand" << endl;
    cout << "PDA_EDGE: Operator --(Push '(')--> Start" << endl;
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
  if (argc < 2)
    return 1;

  string input = argv[1];
  string pattern = (argc > 2) ? argv[2] : "(a|b)*"; // Default or passed arg

  // 1. Generate Automata from Pattern
  cout << "=== AUTOMATA GEN START ===" << endl;
  NFA *nfa = regexToNFA(pattern);
  if (nfa) {
    nfa->printEdges();
    // Generate DFA using real Subset Construction
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