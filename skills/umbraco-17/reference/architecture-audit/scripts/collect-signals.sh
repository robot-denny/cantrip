#!/usr/bin/env bash
# collect-signals.sh — deterministic structural signals for the architecture audit
# Read-only. No side effects beyond stdout.
# Usage: collect-signals.sh <target-dir>

set -u

TARGET="${1:-.}"

if [ ! -d "$TARGET" ]; then
  echo "ERROR: target directory not found: $TARGET" >&2
  exit 1
fi

cd "$TARGET" || exit 1

echo "=== architecture-audit signals: $(pwd) ==="
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# --- Project layout ---
echo "## Project layout"
echo
echo "Top-level .csproj files:"
find . -maxdepth 4 -name "*.csproj" \
  -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/node_modules/*" 2>/dev/null \
  | sort
echo

echo "Top-level solution files:"
find . -maxdepth 2 -name "*.sln" 2>/dev/null | sort
echo

# --- Source code counts ---
echo "## Source code counts"
CS_FILES=$(find . -name "*.cs" \
  -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/TEMP/*" \
  -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
CS_OUT_VIEWS=$(find . -name "*.cs" \
  -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/TEMP/*" \
  -not -path "*/node_modules/*" -not -path "*/Views/*" 2>/dev/null | wc -l | tr -d ' ')
CSHTML_FILES=$(find . -name "*.cshtml" \
  -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | wc -l | tr -d ' ')
TS_FILES=$(find . \( -name "*.ts" -o -name "*.tsx" \) \
  -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
JS_FILES=$(find . \( -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" -not -path "*/dist/*" -not -path "*/wwwroot/lib/*" 2>/dev/null | wc -l | tr -d ' ')

echo "C# files (total):                  $CS_FILES"
echo "C# files (outside Views/):         $CS_OUT_VIEWS"
echo "Razor (.cshtml) files:             $CSHTML_FILES"
echo "TypeScript files:                  $TS_FILES"
echo "JavaScript files (excl. lib):      $JS_FILES"
echo

# --- DI / composition signals ---
echo "## DI / composition"
COMPOSER_COUNT=$(grep -rln "IComposer\|: ComposeAfter" . --include="*.cs" 2>/dev/null \
  | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
NOTIF_HANDLER_COUNT=$(grep -rln "INotificationHandler\|INotificationAsyncHandler" . --include="*.cs" 2>/dev/null \
  | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
echo "Composer files:                    $COMPOSER_COUNT"
echo "Notification handler files:        $NOTIF_HANDLER_COUNT"
echo

# --- Async hygiene ---
echo "## Async hygiene"
BLOCK_ASYNC=$(grep -rEn "\.Result\b|\.Wait\(\)" . --include="*.cs" 2>/dev/null \
  | grep -v "/bin/" | grep -v "/obj/" | grep -v "/TEMP/" | wc -l | tr -d ' ')
echo "Possible sync-over-async (.Result / .Wait):  $BLOCK_ASYNC"
echo

# --- Logging signals ---
echo "## Logging"
SERILOG=$(grep -rln "Serilog\|UseSerilog" . --include="*.cs" --include="*.csproj" 2>/dev/null | wc -l | tr -d ' ')
ILOGGER=$(grep -rln "ILogger<" . --include="*.cs" 2>/dev/null | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
CONSOLE_WRITELN=$(grep -rln "Console\.WriteLine" . --include="*.cs" 2>/dev/null | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
echo "Serilog references:                $SERILOG"
echo "ILogger<T> references:             $ILOGGER"
echo "Console.WriteLine occurrences:     $CONSOLE_WRITELN"
echo

# --- Resilience signals ---
echo "## Resilience"
POLLY=$(grep -rln "Polly\.\|AddPolicyHandler\|RetryAsync\|CircuitBreaker" . --include="*.cs" --include="*.csproj" 2>/dev/null | wc -l | tr -d ' ')
HEALTH=$(grep -rln "AddHealthChecks\|MapHealthChecks" . --include="*.cs" 2>/dev/null | wc -l | tr -d ' ')
OTEL=$(grep -rln "OpenTelemetry\|ApplicationInsights" . --include="*.cs" --include="*.csproj" 2>/dev/null | wc -l | tr -d ' ')
SWALLOWED=$(grep -rEn "catch\s*\(\s*Exception[^)]*\)\s*\{[\s]*\}" . --include="*.cs" 2>/dev/null \
  | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
echo "Polly / retry references:          $POLLY"
echo "Health check registrations:        $HEALTH"
echo "OpenTelemetry/AppInsights refs:    $OTEL"
echo "Swallowed exceptions (heuristic):  $SWALLOWED"
echo

# --- CI/CD presence ---
echo "## CI/CD"
for d in .github/workflows .gitlab-ci.yml azure-pipelines.yml bitbucket-pipelines.yml .circleci .drone.yml; do
  if [ -e "$d" ]; then
    echo "present: $d"
  fi
done
[ -d ".githooks" ] && echo "present: .githooks/"
[ -d ".husky" ] && echo "present: .husky/"
[ -f ".pre-commit-config.yaml" ] && echo "present: .pre-commit-config.yaml"
[ -f ".editorconfig" ] && echo "present: .editorconfig"
echo

# --- Tests ---
echo "## Tests"
TEST_PROJ=$(find . -name "*.Tests.csproj" -o -name "*Test*.csproj" \
  -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
TEST_DIR=$(find . -maxdepth 3 -type d \( -name "tests" -o -name "test" -o -name "Tests" \) \
  -not -path "*/node_modules/*" 2>/dev/null | head -5)
PLAYWRIGHT=$(find . -name "playwright.config.*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
XUNIT=$(grep -rln "xunit\|XUnit" . --include="*.csproj" 2>/dev/null | wc -l | tr -d ' ')
NUNIT=$(grep -rln "NUnit" . --include="*.csproj" 2>/dev/null | wc -l | tr -d ' ')
echo "Test project files (.csproj):      $TEST_PROJ"
echo "xUnit refs:                        $XUNIT"
echo "NUnit refs:                        $NUNIT"
echo "Playwright config present:         $PLAYWRIGHT"
echo "Test directories:"
echo "$TEST_DIR" | sed 's/^/  /'
echo

# --- Umbraco-specific ---
echo "## Umbraco-specific"
UDA_COUNT=$(find . -name "*.uda" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null | wc -l | tr -d ' ')
DELIVERY_API=$(grep -rln "DeliveryApi" . --include="*.cs" --include="*.json" 2>/dev/null \
  | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
CACHED_PARTIAL=$(grep -rln "CachedPartialAsync\|CachedPartial" . --include="*.cshtml" 2>/dev/null | wc -l | tr -d ' ')
EXAMINE_IN_VIEW=$(grep -rln "ExamineManager\|IExamineManager" . --include="*.cshtml" 2>/dev/null | wc -l | tr -d ' ')
echo ".uda schema artifact count:        $UDA_COUNT"
echo "DeliveryApi references:            $DELIVERY_API"
echo "Cached partial usage:              $CACHED_PARTIAL"
echo "Examine queries in Razor (smell):  $EXAMINE_IN_VIEW"
echo

# --- Documentation signals (pattern-detected, not filename-coupled) ---
echo "## Documentation"
for f in CLAUDE.md AGENTS.md AGENT.md CONVENTIONS.md README.md CONTRIBUTING.md GLOSSARY.md CONTEXT.md DOMAIN.md ARCHITECTURE.md DECISIONS.md .github/copilot-instructions.md; do
  [ -f "$f" ] && echo "present: $f"
done
for d in .claude/commands .claude/agents .claude/skills .cursor .continue .aider docs docs/adr adr decisions _specs specs docs/specs _plans plans docs/plans _features features docs/features _prds prds RFCS RFCs; do
  [ -d "$d" ] && echo "present: $d/"
done

XMLDOC_COUNT=$(grep -rln "/// <summary>" . --include="*.cs" 2>/dev/null | grep -v "/bin/" | grep -v "/obj/" | wc -l | tr -d ' ')
echo "Files with XML doc comments:       $XMLDOC_COUNT"
echo

# --- Frontend / headless signals ---
echo "## Frontend / build"
PACKAGE_JSON=$(find . -maxdepth 4 -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | head -10)
VITE=$(find . -maxdepth 4 -name "vite.config.*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
WEBPACK=$(find . -maxdepth 4 -name "webpack.config.*" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
echo "package.json locations:"
echo "$PACKAGE_JSON" | sed 's/^/  /'
echo "Vite configs:                      $VITE"
echo "Webpack configs:                   $WEBPACK"
echo

# --- Secrets scan (presence only — never print values) ---
echo "## Secrets scan"
SECRET_HITS=$(grep -rlEn "(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,})" . \
  --include="*.cs" --include="*.json" --include="*.config" --include="*.yaml" --include="*.yml" \
  2>/dev/null | grep -v "/bin/" | grep -v "/obj/" | grep -v "/node_modules/" | wc -l | tr -d ' ')
if [ "$SECRET_HITS" -gt 0 ]; then
  echo "WARNING: ${SECRET_HITS} file(s) contain patterns that look like secrets."
  echo "Investigate manually. Do NOT print the secret values in the audit report."
else
  echo "No obvious secret patterns detected."
fi
echo

# --- Git signals (lifecycle inputs) ---
echo "## Git signals"
if [ -d ".git" ]; then
  FIRST_COMMIT=$(git log --reverse --format=%cI 2>/dev/null | head -1)
  LAST_COMMIT=$(git log -1 --format=%cI 2>/dev/null)
  COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
  CONTRIB_COUNT=$(git shortlog -sn --all 2>/dev/null | wc -l | tr -d ' ')
  echo "First commit:                      $FIRST_COMMIT"
  echo "Most recent commit:                $LAST_COMMIT"
  echo "Total commits:                     $COMMIT_COUNT"
  echo "Distinct contributors:             $CONTRIB_COUNT"
else
  echo "Not a git repository — lifecycle heuristics will be coarser."
fi
echo

echo "=== end signals ==="
