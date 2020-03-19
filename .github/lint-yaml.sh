#!/bin/sh

# Create a link to this file at .git/hooks/pre-commit to
# force PEP8 validation prior to committing:
#
# $ ln -s -f ../../.github/pre-commit .git/hooks/pre-commit
#
# Ignored violations:
#
#   E402: Module level import not at top of file
#   E741: Do not use variables named 'l', 'o', or 'i'
#   W503: Line break occurred before a binary operator
#   W504: Line break occurred after a binary operator

exec 1>&2

echo "Validating PEP8 compliance..."
echo "------------------------------------------------------------------------------------------------------------"
echo "  - Playbook & Inventory Validation"
find . -name "*.yml" -maxdepth 1 -exec yamllint -d "{extends: relaxed, rules: {line-length: {max: 140}}}" {} \;
echo "------------------------------------------------------------------------------------------------------------"
echo "  - Group Variables"
find group_vars/ -name "*.yml" -maxdepth 1 -exec yamllint -d "{extends: relaxed, rules: {line-length: {max: 140}}}" {} \;
echo "------------------------------------------------------------------------------------------------------------"
