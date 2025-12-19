#ifndef REGEX_VALIDATOR_H
#define REGEX_VALIDATOR_H

#include <string>

struct ValidationResult {
  bool isValid;
  std::string errorMsg;
  int errorPos;
};

class RegexValidator {
public:
  static ValidationResult validate(const std::string &pattern);
};

#endif
