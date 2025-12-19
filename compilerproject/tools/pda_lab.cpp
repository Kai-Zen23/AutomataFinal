#include "../include/dfa.h"
#include "../include/nfa.h"
#include "../include/parser_regex.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stack>
#include <string>
#include <tuple>
#include <vector>

using namespace std;

// ==========================================
// 1. General PDA (Nondeterministic, Epsilon-moves)
// ==========================================

struct Transition {
  string fromState;
  char input; // '\0' for epsilon
  char pop;   // '\0' for empty stack check (if needed) or specific char
  string toState;
  string
      push; // String to push (reversed: left char is top? No, usually left char
            // pushed first, right is top) Standard: "XY" -> Push X, then Push
            // Y. Top is Y. User pseudo: "gamma... rightmost ends up on top".
};

struct Config {
  string state;
  size_t inputIndex;
  string stackContent;    // Using string for stack (back is top)
  vector<string> history; // For trace
};

class GeneralPDA {
  string startState;
  char startStack;
  set<string> finalStates;
  multimap<tuple<string, char, char>, pair<string, string>>
      transitions; // (q, sigma, pop) -> (next_q, push_str)

public:
  GeneralPDA(string q0, char z0) : startState(q0), startStack(z0) {}

  void addFinalState(string q) { finalStates.insert(q); }

  void addTransition(string q, char input, char pop, string nextQ,
                     string pushStr) {
    transitions.insert({{q, input, pop}, {nextQ, pushStr}});
  }

  bool accept(string input, string mode = "final_state") {
    queue<Config> worklist;

    string initialStack(1, startStack);
    vector<string> initHist;
    initHist.push_back("Step 0: Start | Stack: " + initialStack);

    worklist.push({startState, 0, initialStack, initHist});

    set<tuple<string, int, string>> visited; // Cycle detection

    while (!worklist.empty()) {
      Config curr = worklist.front();
      worklist.pop();

      // Cycle check
      if (visited.count({curr.state, curr.inputIndex, curr.stackContent}))
        continue;
      visited.insert({curr.state, curr.inputIndex, curr.stackContent});

      // Check Acceptance
      if (mode == "final_state") {
        if (curr.inputIndex == input.length() &&
            finalStates.count(curr.state)) {
          printTrace(curr.history, "ACCEPTED by Final State");
          return true;
        }
      } else if (mode == "empty_stack") {
        if (curr.inputIndex == input.length() && curr.stackContent.empty()) {
          printTrace(curr.history, "ACCEPTED by Empty Stack");
          return true;
        }
      }

      // Get Top (if any)
      char top = '\0';
      if (!curr.stackContent.empty())
        top = curr.stackContent.back();

      // Collect possible moves
      // We need to look for matching transitions.
      // Keys: (state, input?, pop?)
      // Transition can consume Input or Epsilon.
      // Transition can consume Pop or Epsilon (ignore top).

      // For simplicity based on user pseudo code:
      // "apply_stack_rewrite(S, top, gamma)" implies we MUST pop 'top'.
      // Matches user spec: delta(q, a, top).

      // 1. Epsilon Input Moves
      tryMoves(curr, '\0', top, input, worklist);

      // 2. Real Input Moves
      if (curr.inputIndex < input.length()) {
        tryMoves(curr, input[curr.inputIndex], top, input, worklist);
      }
    }

    cout << "REJECTED" << endl;
    return false;
  }

private:
  void tryMoves(const Config &curr, char inputChar, char stackTop,
                const string &fullInput, queue<Config> &worklist) {
    // Debug
    // cout << "DEBUG: Try state=" << curr.state << " in=" << (inputChar ?
    // inputChar : '_') << " top=" << stackTop << endl;

    auto range = transitions.equal_range({curr.state, inputChar, stackTop});
    // if (range.first == range.second) cout << "DEBUG: No trans found" << endl;
    for (auto it = range.first; it != range.second; ++it) {
      string nextQ = it->second.first;
      string toPush = it->second.second;

      // cout << "DEBUG: Found trans -> " << nextQ << " push=" << toPush <<
      // endl;

      Config nextConf = curr;
      nextConf.state = nextQ;
      if (inputChar != '\0')
        nextConf.inputIndex++;

      // Pop
      if (!nextConf.stackContent.empty())
        nextConf.stackContent.pop_back();

      // Push (User spec: left-to-right, last ends on top)
      for (char c : toPush) {
        if (c != '\0')
          nextConf.stackContent.push_back(c);
      }

      // Trace
      string act = (inputChar == '\0') ? "EPS" : string(1, inputChar);
      string desc =
          "Transition to " + nextQ + ", Stack: " + nextConf.stackContent;
      nextConf.history.push_back("Action: " + act + " | " + desc);

      // Add to worklist
      worklist.push(nextConf);
    }
  }

  // Fixed: moved logic back to accept to access queue or pass queue
  // Actually, let's just make the inner loop explicit in accept().
  void printTrace(const vector<string> &hist, string result) {
    cout << "Trace for Result: " << result << endl;
    for (const auto &s : hist)
      cout << s << endl;
    cout << "----------------------------------" << endl;
  }
};

// ==========================================
// 2. Specialized DPDA for { a^n b^n | n >= 1 }
// ==========================================

bool runDPDA_anbn(string w) {
  cout << "Running DPDA (a^n b^n) on '" << w << "'" << endl;

  vector<char> stack;
  stack.push_back('$'); // Bottom marker

  enum State { Q_PUSH, Q_POP };
  State state = Q_PUSH;

  int i = 0;
  while (i < w.length()) {
    char a = w[i];

    cout << "Step: " << i << ", State: " << (state == Q_PUSH ? "PUSH" : "POP")
         << ", Input: " << a << ", StackTop: " << stack.back() << endl;

    if (state == Q_PUSH) {
      if (a == 'a') {
        stack.push_back('A');
        i++;
      } else if (a == 'b') {
        state = Q_POP;
        // Do not increment i, handle 'b' in Q_POP logic next iteration?
        // User code: "do not advance i here; handle this 'b' in q_pop"
        // So we loop again.
      } else {
        cout << "REJECT: Invalid char in PUSH mode" << endl;
        return false;
      }
    } else if (state == Q_POP) {
      if (a == 'b') {
        if (stack.back() == 'A') {
          stack.pop_back();
          i++;
        } else {
          cout << "REJECT: Stack mismatch (expected A)" << endl;
          return false;
        }
      } else {
        cout << "REJECT: 'a' found in POP mode" << endl;
        return false;
      }
    }
  }

  // End of input
  if (state == Q_POP && stack.back() == '$') {
    cout << "ACCEPT: Stack is [$]" << endl;
    return true;
  }

  cout << "REJECT: Final check failed. State=" << state
       << " StackTop=" << stack.back() << endl;
  return false;
}

int main(int argc, char *argv[]) {
  if (argc > 1) {
    // CLI Mode
    string input = argv[1];
    string pattern = (argc > 2) ? argv[2] : "";

    if (!pattern.empty()) {
      // REGEX MODE (NFA Simulation via PDA)

      // 1. Parse Regex
      Lexer lexer(pattern);
      vector<Token> tokens = lexer.tokenize();
      if (lexer.hasError()) {
        cout << "Error: Lexer - " << lexer.getError() << endl;
        return 1;
      }

      Parser parser(tokens);
      std::unique_ptr<ASTNode> root = parser.parse();
      if (parser.hasError() || !root) {
        cout << "Error: Parser - " << parser.getError() << endl;
        return 1;
      }

      // 2. Build NFA
      NFA nfa;
      nfa.construct(root.get());

      // 3. Convert to DFA (Removes Epsilons)
      DFA dfa(&nfa);

      // 4. Convert DFA to GeneralPDA (Stack always '$')
      // Start state = dfa.startState->id
      GeneralPDA pda(to_string(dfa.startState->id), '$');

      // Final states & Transitions
      for (DFAState *s : dfa.states) {
        if (s->isFinal) {
          pda.addFinalState(to_string(s->id));
        }

        // Transitions (Deterministic, No Epsilon)
        for (auto const &[inputChar, nextId] : s->transitions) {
          pda.addTransition(to_string(s->id), inputChar, '$', to_string(nextId),
                            "$");
        }
      }

      pda.accept(input);
      return 0;
    }

    // DEFAULT MODE (Manually defined PDA for a^n b^n)
    GeneralPDA pda("q_push", '$');
    pda.addFinalState("q_acc");
    pda.addTransition("q_push", 'a', '$', "q_push", "$A");
    pda.addTransition("q_push", 'a', 'A', "q_push", "AA");
    pda.addTransition("q_push", 'b', 'A', "q_pop", "");
    pda.addTransition("q_pop", 'b', 'A', "q_pop", "");
    pda.addTransition("q_pop", '\0', '$', "q_acc", "$");

    pda.accept(input);
    return 0;
  }

  // TEST MODE (No Args)
  // 1. Test DPDA
  cout << "=== Testing DPDA { a^n b^n } ===" << endl;
  runDPDA_anbn("aabb");
  cout << endl;
  runDPDA_anbn("aabbb");
  cout << endl;

  // 2. Test General PDA with { a^n b^n } specs
  cout << "=== Testing General PDA { a^n b^n } ===" << endl;

  GeneralPDA pda("q_push", '$');
  pda.addFinalState("q_acc");
  pda.addTransition("q_push", 'a', '$', "q_push", "$A");
  pda.addTransition("q_push", 'a', 'A', "q_push", "AA");
  pda.addTransition("q_push", 'b', 'A', "q_pop", "");
  pda.addTransition("q_pop", 'b', 'A', "q_pop", "");
  pda.addTransition("q_pop", '\0', '$', "q_acc", "$");

  cout << "Testing 'aabb':" << endl;
  pda.accept("aabb");

  cout << "\nTesting 'aabbb':" << endl;
  pda.accept("aabbb");

  return 0;
}
