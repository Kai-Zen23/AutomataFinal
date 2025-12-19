#ifndef LEXER_REGEX_H
#define LEXER_REGEX_H

#include <iostream>
#include <string>
#include <vector>


enum TokenType {
  TOKEN_CHAR,
  TOKEN_STAR,     // *
  TOKEN_PLUS,     // +
  TOKEN_QUEST,    // ?
  TOKEN_OR,       // |
  TOKEN_LPAREN,   // (
  TOKEN_RPAREN,   // )
  TOKEN_LBRACKET, // [    (Basic support for character classes if needed)
  TOKEN_RBRACKET, // ]
  TOKEN_DASH,     // -
  TOKEN_END,
  TOKEN_ERROR
};

struct Token {
  TokenType type;
  char value;   // For TOKEN_CHAR
  int position; // Index in the original string for error reporting
};

class Lexer {
public:
  Lexer(const std::string &pattern);
  std::vector<Token> tokenize();
  std::string getError() const { return errorMsg; }
  int getErrorPos() const { return errorPos; }
  bool hasError() const { return errorPos != -1; }

private:
  std::string pattern;
  int pos;
  std::string errorMsg;
  int errorPos;

  char peek();
  char advance();
  void addToken(std::vector<Token> &tokens, TokenType type, char val = 0);
};

#endif
