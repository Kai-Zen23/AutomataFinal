#ifndef DFA_H
#define DFA_H

#include "nfa.h"
#include <map>
#include <set>
#include <string>
#include <vector>


struct DFAState {
  int id;
  bool isFinal;
  std::map<char, int> transitions; // char -> next_id
  std::set<State *>
      nfaStates; // The set of NFA states this DFA state represents
};

class DFA {
public:
  DFA(NFA *nfa); // Construct from NFA

  std::vector<DFAState *> states;
  DFAState *startState;

  bool simulate(const std::string &input);
  int getStateCount() const { return states.size(); }

  // For minimization
  void minimize();

private:
  NFA *nfa;
  std::set<State *> epsilonClosure(std::set<State *> states);
  std::set<State *> move(std::set<State *> states, char sym);
};

#endif
