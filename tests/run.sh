#!/usr/bin/env bash
#
# Fixture runner for scripts/check-install.sh.
#
# Each tests/install-check/<case>/ is a minimal fake project tree plus an `expect` file
# declaring what the check should do when run inside it:
#
#     exit: 0                     required, exactly once
#     contains: some substring    zero or more; output must contain each
#     not_contains: substring     zero or more; output must contain none
#
# Fixtures are deliberately minimal fake trees rather than real installs — the check is
# being tested, not the installer.
#
# Usage:  tests/run.sh [case-name ...]     (no args = every case)
# Exit:   0 if every case passes, 1 otherwise

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

CHECK="$PWD/scripts/check-install.sh"
CASES_DIR="tests/install-check"

PASS=0
FAIL=0
FAILED_NAMES=()

cases=("$@")
if [[ ${#cases[@]} -eq 0 ]]; then
  while IFS= read -r d; do cases+=("$(basename "$d")"); done \
    < <(find "$CASES_DIR" -mindepth 1 -maxdepth 1 -type d | sort)
fi

for name in "${cases[@]}"; do
  dir="$CASES_DIR/$name"
  expect="$dir/expect"

  if [[ ! -f $expect ]]; then
    printf '\033[31mFAIL\033[0m  %-28s no expect file\n' "$name"
    FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name"); continue
  fi

  want_exit=$(sed -n 's/^exit:[[:space:]]*//p' "$expect" | head -1)

  # Run the check inside the fixture, capturing output and status together.
  actual=$( cd "$dir" && "$CHECK" 2>&1 )
  got_exit=$?

  problems=()
  [[ "$got_exit" != "$want_exit" ]] && problems+=("exit $got_exit, wanted $want_exit")

  while IFS= read -r sub; do
    [[ -z "$sub" ]] && continue
    grep -qiF -- "$sub" <<<"$actual" || problems+=("output missing: $sub")
  done < <(sed -n 's/^contains:[[:space:]]*//p' "$expect")

  while IFS= read -r sub; do
    [[ -z "$sub" ]] && continue
    grep -qiF -- "$sub" <<<"$actual" && problems+=("output should not contain: $sub")
  done < <(sed -n 's/^not_contains:[[:space:]]*//p' "$expect")

  if [[ ${#problems[@]} -eq 0 ]]; then
    printf '\033[32mok\033[0m    %s\n' "$name"
    PASS=$((PASS + 1))
  else
    printf '\033[31mFAIL\033[0m  %s\n' "$name"
    for p in "${problems[@]}"; do printf '        %s\n' "$p"; done
    FAIL=$((FAIL + 1)); FAILED_NAMES+=("$name")
  fi
done

printf '\n'
if [[ $FAIL -eq 0 ]]; then
  printf '\033[32m%d/%d cases passed.\033[0m\n' "$PASS" "$((PASS + FAIL))"
  exit 0
fi
printf '\033[31m%d/%d cases failed:\033[0m %s\n' "$FAIL" "$((PASS + FAIL))" "${FAILED_NAMES[*]}"
exit 1
