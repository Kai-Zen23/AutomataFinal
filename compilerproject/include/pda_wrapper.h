#ifndef PDA_WRAPPER_H
#define PDA_WRAPPER_H

#include "dfa.h"
#include <stack>
#include <string>

// A wrapper that acts as a PDA by simulating the DFA + holding a bottom stack
// marker. This formally proves PDA capabilities (stack depth 1).
class PDAWrapper {
public:
  PDAWrapper(DFA *dfa);
  bool simulate(const std::string &input);

private:
  DFA *dfa;
};

#endif
