#ifndef NFA_H
#define NFA_H

#include "parser_regex.h"
#include <map>
#include <set>
#include <string>
#include <vector>


// Forward declaration
struct State;

// NFA State
struct State {
  int id;
  bool isFinal;
  // Map symbol to list of next states. Empty string key = epsilon.
  std::map<char, std::vector<State *>> transitions;
  std::vector<State *> epsilonTransitions;

  State(int i) : id(i), isFinal(false) {}
  void addTransition(char sym, State *next);
  void addEpsilon(State *next);
};

// NFA Fragment (Thompson's Construction building block)
struct NFAFragment {
  State *start;
  State *accept;

  // Helper to join fragments
  NFAFragment(State *s, State *a) : start(s), accept(a) {}
};

class NFA {
public:
  NFA();
  ~NFA();

  State *start;
  State *accept;
  std::vector<State *> allStates;

  // Build NFA from AST
  void construct(ASTNode *root);

  // Helpers
  static State *newState();
  static void resetStateCounter();

private:
  NFAFragment visit(ASTNode *node);
  static int stateIds;
  // Track allocated states for cleanup (simple vector of pointers)
};

#endif
