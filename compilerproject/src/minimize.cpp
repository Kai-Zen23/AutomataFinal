#include "../include/minimize.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <vector>


void minimizeDFA(DFA &dfa) {
  if (dfa.states.empty())
    return;

  // 1. Partition: {Final, Non-Final}
  std::vector<int> finalStates, nonFinalStates;
  for (auto s : dfa.states) {
    if (s->isFinal)
      finalStates.push_back(s->id);
    else
      nonFinalStates.push_back(s->id);
  }

  std::vector<std::vector<int>> P;
  if (!finalStates.empty())
    P.push_back(finalStates);
  if (!nonFinalStates.empty())
    P.push_back(nonFinalStates);

  std::vector<std::vector<int>> W = P;

  // 2. Hopcroft
  while (!W.empty()) {
    std::vector<int> A = W.back();
    W.pop_back();

    std::set<char> alphabet;
    for (auto s : dfa.states)
      for (auto const &[sym, _] : s->transitions)
        alphabet.insert(sym);

    for (char c : alphabet) {
      std::set<int> A_set(A.begin(), A.end());
      std::vector<int> X;
      for (auto s : dfa.states) {
        if (s->transitions.count(c) && A_set.count(s->transitions[c])) {
          X.push_back(s->id);
        }
      }
      if (X.empty())
        continue;

      int p_size = P.size();
      for (int i = 0; i < p_size; ++i) {
        std::vector<int> Y = P[i];
        std::vector<int> intersection, diff;
        std::set<int> X_set(X.begin(), X.end());
        for (int y : Y)
          (X_set.count(y) ? intersection : diff).push_back(y);

        if (!intersection.empty() && !diff.empty()) {
          P[i] = intersection;
          P.push_back(diff);

          bool inW = false;
          for (int k = 0; k < W.size(); ++k) {
            if (W[k].size() == Y.size()) { // Optimized check
              std::set<int> w_k(W[k].begin(), W[k].end());
              std::set<int> y_set(Y.begin(), Y.end());
              if (w_k == y_set) {
                W[k] = intersection;
                W.push_back(diff);
                inW = true;
                break;
              }
            }
          }
          if (!inW)
            W.push_back(intersection.size() <= diff.size() ? intersection
                                                           : diff);
        }
      }
    }
  }

  // 3. Rebuild
  std::map<int, int> stateMap;
  for (int i = 0; i < P.size(); ++i)
    for (int old : P[i])
      stateMap[old] = i;

  std::vector<DFAState *> newStates;
  for (int i = 0; i < P.size(); ++i) {
    if (P[i].empty())
      continue;
    DFAState *ns = new DFAState();
    ns->id = i;
    ns->isFinal = false;

    int oldRep = P[i][0];
    DFAState *oldState = nullptr;
    for (auto s : dfa.states)
      if (s->id == oldRep)
        oldState = s;

    for (int old : P[i])
      for (auto s : dfa.states)
        if (s->id == old && s->isFinal)
          ns->isFinal = true;

    if (oldState)
      for (auto const &[sym, nextOld] : oldState->transitions)
        ns->transitions[sym] = stateMap[nextOld];

    newStates.push_back(ns);
  }

  int newStartId = stateMap[dfa.startState->id];
  for (auto ns : newStates)
    if (ns->id == newStartId)
      dfa.startState = ns;
  dfa.states = newStates;
}
