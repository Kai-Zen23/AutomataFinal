#include "../include/dfa.h"
#include <algorithm>
#include <iostream>
#include <queue>


// Helper to compare sets of states (for map key)
// We just use std::set which is comparable.

DFA::DFA(NFA *n) : nfa(n), startState(nullptr) {
  if (!n || !n->start)
    return;

  // Subset Construction
  std::map<std::set<int>, int>
      seenStates; // Map NFA State ID Set -> DFA State ID
  std::queue<std::set<State *>> worklist;
  int nextId = 0;

  std::set<State *> startSet = epsilonClosure({nfa->start});
  std::set<int> startIds;
  for (auto s : startSet)
    startIds.insert(s->id);

  DFAState *dStart = new DFAState();
  dStart->id = nextId++;
  dStart->nfaStates = startSet;
  dStart->isFinal = false;
  for (auto s : startSet)
    if (s->isFinal)
      dStart->isFinal = true;

  states.push_back(dStart);
  startState = dStart;
  seenStates[startIds] = dStart->id;
  worklist.push(startSet);

  while (!worklist.empty()) {
    std::set<State *> current = worklist.front();
    worklist.pop();

    std::set<int> currentIds;
    for (auto s : current)
      currentIds.insert(s->id);
    int currentDfaId = seenStates[currentIds];
    DFAState *currentDfaState = states[currentDfaId];

    // Find alphabet
    std::set<char> alphabet;
    for (auto s : current) {
      for (auto const &[sym, _] : s->transitions) {
        alphabet.insert(sym);
      }
    }

    for (char sym : alphabet) {
      std::set<State *> nextSet = epsilonClosure(move(current, sym));
      if (nextSet.empty())
        continue; // Dead state implicit? Or explicit?

      std::set<int> nextIds;
      for (auto s : nextSet)
        nextIds.insert(s->id);

      if (seenStates.find(nextIds) == seenStates.end()) {
        DFAState *newState = new DFAState();
        newState->id = nextId++;
        newState->nfaStates = nextSet;
        newState->isFinal = false;
        for (auto s : nextSet)
          if (s->isFinal)
            newState->isFinal = true;

        states.push_back(newState);
        seenStates[nextIds] = newState->id;
        worklist.push(nextSet);
      }

      currentDfaState->transitions[sym] = seenStates[nextIds];
    }
  }
}

std::set<State *> DFA::epsilonClosure(std::set<State *> inputStates) {
  std::set<State *> closure = inputStates;
  std::vector<State *> stack(inputStates.begin(), inputStates.end());

  while (!stack.empty()) {
    State *s = stack.back();
    stack.pop_back();

    for (State *next : s->epsilonTransitions) {
      if (closure.find(next) == closure.end()) {
        closure.insert(next);
        stack.push_back(next);
      }
    }
  }
  return closure;
}

std::set<State *> DFA::move(std::set<State *> inputStates, char sym) {
  std::set<State *> result;
  for (State *s : inputStates) {
    if (s->transitions.count(sym)) {
      for (State *next : s->transitions[sym]) {
        result.insert(next);
      }
    }
  }
  return result;
}

bool DFA::simulate(const std::string &input) {
  if (!startState)
    return false;
  DFAState *curr = startState;
  for (char c : input) {
    if (curr->transitions.find(c) == curr->transitions.end()) {
      return false; // Stuck -> Reject
    }
    int nextId = curr->transitions[c];
    // Find pointer (inefficient O(N), but vector index usually matches ID)
    // Caution: minimize() might shuffle Is/Indices.
    // Better: Use map or ensure vector index == ID.
    // Assuming vector index == id for now, but safer to lookup.
    if (nextId < states.size() && states[nextId]->id == nextId) {
      curr = states[nextId];
    } else {
      // Search
      bool found = false;
      for (auto s : states)
        if (s->id == nextId) {
          curr = s;
          found = true;
          break;
        }
      if (!found)
        return false;
    }
  }
  return curr->isFinal;
}

// Hopcroft's will be in minimize.cpp (implemented as extern or method here?)
// For modularity, I'll put it later.
void DFA::minimize() {
  // Placeholder for now
}
