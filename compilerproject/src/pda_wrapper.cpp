#include "../include/pda_wrapper.h"

PDAWrapper::PDAWrapper(DFA *d) : dfa(d) {}

bool PDAWrapper::simulate(const std::string &input) {
  if (!dfa || !dfa->startState)
    return false;

  // 1. Initialize Stack with Bottom Marker
  std::stack<char> stack;
  const char BOTTOM_MARKER = (char)255;
  stack.push(BOTTOM_MARKER);

  // 2. Start State
  DFAState *current = dfa->startState;

  for (char c : input) {
    // Enforce Stack Constraint
    if (stack.empty() || stack.top() != BOTTOM_MARKER)
      return false;

    // Transition
    if (current->transitions.find(c) == current->transitions.end()) {
      return false; // Reject
    }
    int nextId = current->transitions[c];

    // Find next state
    bool found = false;
    // Optimization: Try direct index
    if (nextId < dfa->states.size() && dfa->states[nextId]->id == nextId) {
      current = dfa->states[nextId];
      found = true;
    } else {
      for (auto s : dfa->states)
        if (s->id == nextId) {
          current = s;
          found = true;
          break;
        }
    }
    if (!found)
      return false;
  }

  // Accept if Final State AND Stack has Bottom Marker
  return current->isFinal && !stack.empty() && stack.top() == BOTTOM_MARKER;
}
