#!/usr/bin/env bash
#
# Fixture runner. One runner, many suites.
#
# A suite is a directory under tests/ holding a `subject` file plus one directory per case:
#
#     tests/<suite>/subject        one line: repo-relative path to the executable under test
#     tests/<suite>/<case>/        a minimal fixture tree plus an `expect` file
#
# The `expect` file declares what the subject should do when run inside that case dir:
#
#     exit: 0                     required, exactly once
#     args: --flag value          zero or one; a single line, word-split, no globbing
#     contains: some substring     zero or more; output must contain each
#     not_contains: substring      zero or more; output must contain none
#     same_stdout_as: other-case   zero or more; stdout must byte-match that case's stdout
#
# `contains`/`not_contains` see stdout and stderr merged, because a check's findings may go
# to either and a fixture should not have to care which. `same_stdout_as` cannot use that
# stream — a byte comparison of merged output would fail on any stderr noise or interleaving
# difference that has nothing to do with the claim. So it re-runs both cases with stderr
# discarded. Two runs is the price of not changing what `contains` sees.
#
# Fixtures are deliberately minimal fake trees rather than real installs — the subject is
# being tested, not the thing that produced the tree.
#
# Usage:  tests/run.sh                       every suite
#         tests/run.sh <suite>               one suite, every case
#         tests/run.sh <suite> <case> ...    named cases in one suite
# Exit:   0 if every case passes, 1 if any case fails, 2 on a usage or setup error

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

TESTS_DIR="tests"

WORK=$(mktemp -d) || exit 2
trap 'rm -rf "$WORK"' EXIT

PASS=0
FAIL=0
FAILED_NAMES=()

# Every directory under tests/ that carries a subject file.
list_suites() {
  find "$TESTS_DIR" -mindepth 2 -maxdepth 2 -type f -name subject | sort | while IFS= read -r f; do
    basename "$(dirname "$f")"
  done
}

# First value of a single-line directive, or empty.
directive() {  # directive <expect-file> <name>
  sed -n "s/^$2:[[:space:]]*//p" "$1" | head -1
}

# How many times a single-line directive appears. A second one is an authoring mistake:
# `head -1` above would take the first and discard the rest silently, so the case would
# run against arguments nobody reading the file would predict.
directive_count() {  # directive_count <expect-file> <name>
  grep -c "^$2:" "$1" 2>/dev/null || true
}

# Read a case's `args:` line into the named array without glob expansion.
read_args() {  # read_args <expect-file> <array-name>
  local line
  line=$(directive "$1" args)
  # shellcheck disable=SC2229
  IFS=' ' read -r -a "$2" <<<"$line"
}

# Run one case capturing stdout alone, for same_stdout_as.
capture_stdout() {  # capture_stdout <suite-dir> <case> <subject-abs> <outfile>
  local dir="$1/$2" a=()
  read_args "$dir/expect" a
  ( cd "$dir" && "$3" ${a[@]+"${a[@]}"} ) >"$4" 2>/dev/null
}

# A case's stdout-only capture, computed at most once per run.
#
# Without the cache, cost scales with the number of same_stdout_as *references* rather
# than with the number of cases: a canonical case referenced by four variants was run
# five times to produce byte-identical output, and a case naming two references
# re-captured its own stdout twice. Measured at 15 subject invocations where 10 suffice.
# $WORK is the cache surface because bash 3.2 has no associative arrays.
stdout_of() {  # stdout_of <suite-dir> <case> <subject-abs> -> prints cache path
  # Keyed by suite as well as case: one $WORK serves the whole run, and two suites may
  # legitimately hold a case of the same name against different subjects.
  local key="$WORK/stdout.${1//\//_}.$2"
  [[ -f "$key" ]] || capture_stdout "$1" "$2" "$3" "$key"
  printf '%s\n' "$key"
}

# --- pick the suites and cases to run ----------------------------------------

suites=()
case_args=()

if [[ $# -eq 0 ]]; then
  while IFS= read -r s; do suites+=("$s"); done < <(list_suites)
  if [[ ${#suites[@]} -eq 0 ]]; then
    printf 'no suites found under %s/ — a suite needs a `subject` file\n' "$TESTS_DIR" >&2
    exit 2
  fi
else
  if [[ ! -f "$TESTS_DIR/$1/subject" ]]; then
    printf 'no such suite: %s\n' "$1" >&2
    printf 'suites under %s/ are:\n' "$TESTS_DIR" >&2
    list_suites | sed 's/^/  /' >&2
    exit 2
  fi
  suites=("$1"); shift
  case_args=("$@")
fi

# --- run them ----------------------------------------------------------------

for suite in "${suites[@]}"; do
  suite_dir="$TESTS_DIR/$suite"

  subject_rel=$(sed -n '1p' "$suite_dir/subject" | tr -d '\r')
  subject_rel="${subject_rel#"${subject_rel%%[![:space:]]*}"}"
  subject_rel="${subject_rel%"${subject_rel##*[![:space:]]}"}"

  # Resolve before any cd — a case runs with its own directory as cwd.
  SUBJECT="$PWD/$subject_rel"
  subject_ok=1
  if [[ -z $subject_rel || ! -x $SUBJECT ]]; then
    subject_ok=0
  fi

  cases=()
  if [[ ${#case_args[@]} -gt 0 ]]; then
    cases=("${case_args[@]}")
  else
    while IFS= read -r d; do cases+=("$(basename "$d")"); done \
      < <(find "$suite_dir" -mindepth 1 -maxdepth 1 -type d | sort)
  fi

  n=${#cases[@]}; [[ $n -eq 1 ]] && plural="case" || plural="cases"
  printf '\n%s — %d %s, subject %s\n' \
    "$suite" "$n" "$plural" "${subject_rel:-<empty>}"

  # Guarded: a suite may legitimately have a subject and no cases yet -- that is the
  # state every new suite passes through. Unguarded on bash 3.2, `set -u` kills the
  # interpreter here, and since suites run in sorted order it takes every later suite's
  # results with it, reporting a raw "unbound variable" instead of "0 cases".
  for name in "${cases[@]+"${cases[@]}"}"; do
    dir="$suite_dir/$name"
    expect="$dir/expect"

    if [[ ! -f $expect ]]; then
      printf '\033[31mFAIL\033[0m  %-28s no expect file\n' "$name"
      FAIL=$((FAIL + 1)); FAILED_NAMES+=("$suite/$name"); continue
    fi

    problems=()

    if [[ $subject_ok -eq 0 ]]; then
      problems+=("subject missing or not executable: ${subject_rel:-<empty>}")
    else
      want_exit=$(directive "$expect" exit)
      args=(); read_args "$expect" args

      # `exit` and `args` are single-line directives. A duplicate is silently dropped by
      # `head -1`, so the case would run against arguments the file does not appear to
      # declare -- refuse instead of guessing which line was meant.
      for single in exit args; do
        count=$(directive_count "$expect" "$single")
        [[ "$count" -gt 1 ]] && \
          problems+=("$single: declared $count times, expected at most one")
      done

      # Run the subject inside the fixture, capturing output and status together.
      actual=$( cd "$dir" && "$SUBJECT" ${args[@]+"${args[@]}"} 2>&1 )
      got_exit=$?

      [[ "$got_exit" != "$want_exit" ]] && problems+=("exit $got_exit, wanted $want_exit")

      while IFS= read -r sub; do
        [[ -z "$sub" ]] && continue
        grep -qiF -- "$sub" <<<"$actual" || problems+=("output missing: $sub")
      done < <(sed -n 's/^contains:[[:space:]]*//p' "$expect")

      while IFS= read -r sub; do
        [[ -z "$sub" ]] && continue
        grep -qiF -- "$sub" <<<"$actual" && problems+=("output should not contain: $sub")
      done < <(sed -n 's/^not_contains:[[:space:]]*//p' "$expect")

      while IFS= read -r ref; do
        [[ -z "$ref" ]] && continue
        if [[ ! -f "$suite_dir/$ref/expect" ]]; then
          problems+=("same_stdout_as: no case '$ref' in suite $suite")
          continue
        fi
        mine=$(stdout_of "$suite_dir" "$name" "$SUBJECT")
        theirs=$(stdout_of "$suite_dir" "$ref" "$SUBJECT")
        if ! cmp -s "$mine" "$theirs"; then
          problems+=("stdout differs from case $ref:")
          total=$(diff "$theirs" "$mine" | wc -l | tr -d ' ')
          while IFS= read -r line; do
            problems+=("  $line")
          done < <(diff "$theirs" "$mine" | head -6)
          # Say when there is more, so a reader can tell a whole diff from a clipped one.
          [[ "$total" -gt 6 ]] && \
            problems+=("  ... $((total - 6)) more diff lines; run the two cases to see them")
        fi
      done < <(sed -n 's/^same_stdout_as:[[:space:]]*//p' "$expect")
    fi

    if [[ ${#problems[@]} -eq 0 ]]; then
      printf '\033[32mok\033[0m    %s\n' "$name"
      PASS=$((PASS + 1))
    else
      printf '\033[31mFAIL\033[0m  %s\n' "$name"
      for p in "${problems[@]}"; do printf '        %s\n' "$p"; done
      FAIL=$((FAIL + 1)); FAILED_NAMES+=("$suite/$name")
    fi
  done
done

printf '\n'
if [[ $FAIL -eq 0 ]]; then
  [[ ${#suites[@]} -eq 1 ]] && sp="suite" || sp="suites"
  printf '\033[32m%d/%d cases passed\033[0m across %d %s.\n' \
    "$PASS" "$((PASS + FAIL))" "${#suites[@]}" "$sp"
  exit 0
fi
printf '\033[31m%d/%d cases failed:\033[0m %s\n' "$FAIL" "$((PASS + FAIL))" "${FAILED_NAMES[*]}"
exit 1
