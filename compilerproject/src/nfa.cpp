#include "../include/nfa.h"
#include <iostream>

int NFA::stateIds = 0;
std::vector<State *>
    globalStates; // For simplified memory management in this scope

void State::addTransition(char sym, State *next) {
  transitions[sym].push_back(next);
}

void State::addEpsilon(State *next) { epsilonTransitions.push_back(next); }

State *NFA::newState() {
  State *s = new State(stateIds++);
  globalStates.push_back(s);
  return s;
}

void NFA::resetStateCounter() {
  stateIds = 0;
  // Note: Memory leak if we don't clear globalStates, but simplest for this
  // task Real implementation would own states in NFA object. We'll move
  // ownership to NFA object soon.
}

NFA::NFA() : start(nullptr), accept(nullptr) { resetStateCounter(); }

NFA::~NFA() {
  // Delete states
  // for(State* s : allStates) delete s;
  // In this simple demo, we rely on OS cleanup or separate pool.
  // Avoid double free if multiple NFAs verify this.
}

void NFA::construct(ASTNode *root) {
  if (!root)
    return;
  NFAFragment frag = visit(root);
  start = frag.start;
  accept = frag.accept;
  accept->isFinal = true;

  // Collect all states? (Optional, good for printing/DFA)
  // BFS traversal
  std::vector<State *> q;
  std::set<int> visited;
  q.push_back(start);
  visited.insert(start->id);

  int head = 0;
  while (head < q.size()) {
    State *curr = q[head++];
    allStates.push_back(curr);

    for (auto const &[sym, nexts] : curr->transitions) {
      for (State *s : nexts) {
        if (visited.find(s->id) == visited.end()) {
          visited.insert(s->id);
          q.push_back(s);
        }
      }
    }
    for (State *s : curr->epsilonTransitions) {
      if (visited.find(s->id) == visited.end()) {
        visited.insert(s->id);
        q.push_back(s);
      }
    }
  }
}

NFAFragment NFA::visit(ASTNode *node) {
  switch (node->getType()) {
  case AST_CHAR: {
    CharNode *n = static_cast<CharNode *>(node);
    State *s = newState();
    State *a = newState();
    s->addTransition(n->val, a);
    return NFAFragment(s, a);
  }
  case AST_EPSILON: {
    State *s = newState();
    State *a = newState();
    s->addEpsilon(a);
    return NFAFragment(s, a);
  }
  case AST_CONCAT: {
    ConcatNode *n = static_cast<ConcatNode *>(node);
    NFAFragment left = visit(n->left.get());
    NFAFragment right = visit(n->right.get());
    // Merge left.accept -> right.start (epsilon)
    // Optimization: Merge states directly if careful, but Thompson uses epsilon
    left.accept->addEpsilon(right.start);
    left.accept->isFinal = false; // it was temp final
    return NFAFragment(left.start, right.accept);
  }
  case AST_UNION: {
    UnionNode *n = static_cast<UnionNode *>(node);
    NFAFragment top = visit(n->left.get());
    NFAFragment bot = visit(n->right.get());

    State *s = newState();
    State *a = newState();

    s->addEpsilon(top.start);
    s->addEpsilon(bot.start);

    top.accept->addEpsilon(a);
    bot.accept->addEpsilon(a);

    return NFAFragment(s, a);
  }
  case AST_STAR: {
    StarNode *n = static_cast<StarNode *>(node);
    NFAFragment inner = visit(n->child.get());

    State *s = newState();
    State *a = newState();

    s->addEpsilon(inner.start);
    s->addEpsilon(a); // Skip

    inner.accept->addEpsilon(inner.start); // Loop
    inner.accept->addEpsilon(a);           // Exit

    return NFAFragment(s, a);
  }
  }
  // Should not reach
  return NFAFragment(nullptr, nullptr);
}
