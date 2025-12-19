#include "../include/dfa.h"
#include "../include/lexer_regex.h"
#include "../include/minimize.h"
#include "../include/nfa.h"
#include "../include/parser_regex.h"
#include "../include/pda_wrapper.h"
#include "../include/regex_validator.h"
#include <iostream>
#include <string>
#include <vector>


using namespace std;

int main(int argc, char *argv[]) {
  if (argc < 2) {
    cout << "Usage: regex_engine <MODE> <ARGS...>" << endl;
    return 1;
  }

  string mode = argv[1];

  if (mode == "VALIDATE") {
    if (argc < 3)
      return 1;
    string pattern = argv[2];
    auto res = RegexValidator::validate(pattern);
    if (res.isValid) {
      cout << "VALID" << endl;
    } else {
      cout << "ERROR|" << res.errorMsg << "|" << res.errorPos << endl;
    }
    return 0;
  }

  if (mode == "TEST") {
    string pattern = (argc > 2) ? argv[2] : "";

    Lexer lexer(pattern);
    auto tokens = lexer.tokenize();
    if (lexer.hasError()) {
      cout << "ERROR: Lexer" << endl;
      return 1;
    }

    Parser parser(tokens);
    auto ast = parser.parse();
    if (!ast) {
      cout << "ERROR: Invalid Regex" << endl;
      return 1;
    }

    NFA nfa;
    nfa.construct(ast.get());

    DFA dfa(&nfa);
    minimizeDFA(dfa);

    // PDAWrapper pda(&dfa); // Optional check

    for (int i = 3; i < argc; ++i) {
      string testStr = argv[i];
      bool accepted = dfa.simulate(testStr);
      cout << "RESULT: " << testStr << " -> "
           << (accepted ? "Accepted" : "Rejected") << endl;
    }
    return 0;
  }

  if (mode == "METRICS") {
    string pattern = (argc > 2) ? argv[2] : "";
    Lexer lexer(pattern);
    auto tokens = lexer.tokenize();
    Parser parser(tokens);
    auto ast = parser.parse();
    NFA nfa;
    nfa.construct(ast.get());
    DFA dfa(&nfa);
    int dfaStates = dfa.states.size();
    minimizeDFA(dfa);
    cout << "METRICS: NFA=" << nfa.allStates.size() << " DFA=" << dfaStates
         << " MinDFA=" << dfa.states.size() << endl;
    return 0;
  }

  return 0;
}
