#include "../include/lexer_regex.h"

Lexer::Lexer(const std::string &pat) : pattern(pat), pos(0), errorPos(-1) {}

char Lexer::peek() {
  if (pos >= pattern.length())
    return 0;
  return pattern[pos];
}

char Lexer::advance() {
  if (pos >= pattern.length())
    return 0;
  return pattern[pos++];
}

void Lexer::addToken(std::vector<Token> &tokens, TokenType type, char val) {
  tokens.push_back({type, val, pos - 1});
}

std::vector<Token> Lexer::tokenize() {
  std::vector<Token> tokens;
  pos = 0; // Reset
  errorPos = -1;
  errorMsg = "";

  while (pos < pattern.length()) {
    char c = advance();

    switch (c) {
    case '*':
      addToken(tokens, TOKEN_STAR);
      break;
    case '+':
      addToken(tokens, TOKEN_PLUS);
      break;
    case '?':
      addToken(tokens, TOKEN_QUEST);
      break;
    case '|':
      addToken(tokens, TOKEN_OR);
      break;
    case '(':
      addToken(tokens, TOKEN_LPAREN);
      break;
    case ')':
      addToken(tokens, TOKEN_RPAREN);
      break;
    case '[':
      addToken(tokens, TOKEN_LBRACKET);
      break;
    case ']':
      addToken(tokens, TOKEN_RBRACKET);
      break;
    // case '-': addToken(tokens, TOKEN_DASH); break; // Dash inside brackets is
    // special
    case '\\': {
      if (pos >= pattern.length()) {
        errorMsg = "Dangling escape character at end of pattern";
        errorPos = pos - 1;
        return tokens;
      }
      char next = advance();
      addToken(tokens, TOKEN_CHAR, next); // Escaped char is treated as literal
      break;
    }
    default:
      addToken(tokens, TOKEN_CHAR, c);
      break;
    }
  }
  tokens.push_back({TOKEN_END, 0, pos});
  return tokens;
}
