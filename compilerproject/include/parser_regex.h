#ifndef PARSER_REGEX_H
#define PARSER_REGEX_H

#include "lexer_regex.h"
#include <memory>
#include <string>
#include <vector>

enum ASTType { AST_CHAR, AST_CONCAT, AST_UNION, AST_STAR, AST_EPSILON };

// Abstract Base Class / Interface for AST Nodes
class ASTNode {
public:
  virtual ~ASTNode() = default;
  virtual void print(int indent = 0) const = 0;
  virtual ASTType getType() const = 0;
};

class CharNode : public ASTNode {
public:
  char val;
  CharNode(char c) : val(c) {}
  void print(int indent = 0) const override;
  ASTType getType() const override { return AST_CHAR; }
};

class EpsilonNode : public ASTNode {
public:
  void print(int indent = 0) const override;
  ASTType getType() const override { return AST_EPSILON; }
};

class ConcatNode : public ASTNode {
public:
  std::unique_ptr<ASTNode> left;
  std::unique_ptr<ASTNode> right;
  ConcatNode(std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r)
      : left(std::move(l)), right(std::move(r)) {}
  void print(int indent = 0) const override;
  ASTType getType() const override { return AST_CONCAT; }
};

class UnionNode : public ASTNode {
public:
  std::unique_ptr<ASTNode> left;
  std::unique_ptr<ASTNode> right;
  UnionNode(std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r)
      : left(std::move(l)), right(std::move(r)) {}
  void print(int indent = 0) const override;
  ASTType getType() const override { return AST_UNION; }
};

class StarNode : public ASTNode {
public:
  std::unique_ptr<ASTNode> child;
  StarNode(std::unique_ptr<ASTNode> c) : child(std::move(c)) {}
  void print(int indent = 0) const override;
  ASTType getType() const override { return AST_STAR; }
};

class Parser {
public:
  Parser(const std::vector<Token> &tokens);
  std::unique_ptr<ASTNode> parse();
  std::string getError() const { return errorMsg; }
  int getErrorPos() const { return errorPos; }
  bool hasError() const { return errorPos != -1; }

private:
  const std::vector<Token> &tokens;
  int current;
  std::string errorMsg;
  int errorPos;

  Token peek() const;
  Token advance();
  bool match(TokenType type);
  bool check(TokenType type) const;
  bool isAtEnd() const;

  // Grammar Productions
  std::unique_ptr<ASTNode> parseExpression(); // Union
  std::unique_ptr<ASTNode> parseTerm();       // Concat
  std::unique_ptr<ASTNode> parseFactor();     // Star/Plus/Quest
  std::unique_ptr<ASTNode> parseAtom();       // Char or (Expr)

  void setError(const std::string &msg, int pos);
};

#endif
