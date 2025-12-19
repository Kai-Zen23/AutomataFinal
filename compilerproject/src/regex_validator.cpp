#include "../include/regex_validator.h"
#include "../include/lexer_regex.h"
#include "../include/parser_regex.h"

ValidationResult RegexValidator::validate(const std::string &pattern) {
  Lexer lexer(pattern);
  auto tokens = lexer.tokenize();

  if (lexer.hasError()) {
    return {false, lexer.getError(), lexer.getErrorPos()};
  }

  Parser parser(tokens);
  auto ast = parser.parse();

  if (parser.hasError()) {
    return {false, parser.getError(), parser.getErrorPos()};
  }

  return {true, "Valid", -1};
}
