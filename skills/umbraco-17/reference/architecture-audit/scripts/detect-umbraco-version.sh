#!/usr/bin/env bash
# detect-umbraco-version.sh — detect Umbraco major version from a target repo.
# Read-only.
# Usage: detect-umbraco-version.sh <target-dir>
# Output: a single line — the major version (e.g. "17"), or "none" if Umbraco is not present.

set -u

TARGET="${1:-.}"

if [ ! -d "$TARGET" ]; then
  echo "ERROR: target directory not found: $TARGET" >&2
  exit 1
fi

cd "$TARGET" || exit 1

# Look at every .csproj for an Umbraco.Cms PackageReference
VERSION=$(grep -hEo '<PackageReference[^>]+Include="Umbraco\.Cms"[^>]+Version="[0-9]+\.[0-9]+\.[0-9]+' \
  $(find . -maxdepth 4 -name "*.csproj" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null) 2>/dev/null \
  | grep -oE 'Version="[0-9]+' | head -1 | grep -oE '[0-9]+')

if [ -z "$VERSION" ]; then
  # Fallback: any Umbraco.* package gives us at least a major
  VERSION=$(grep -hEo '<PackageReference[^>]+Include="Umbraco\.[A-Za-z.]+"[^>]+Version="[0-9]+' \
    $(find . -maxdepth 4 -name "*.csproj" -not -path "*/bin/*" -not -path "*/obj/*" 2>/dev/null) 2>/dev/null \
    | grep -oE 'Version="[0-9]+' | head -1 | grep -oE '[0-9]+')
fi

if [ -z "$VERSION" ]; then
  # Last fallback: presence of a .umbraco file at root signals Umbraco Cloud project,
  # but doesn't reveal the major. Report "umbraco-cloud-no-version" so the caller can ask.
  if [ -f ".umbraco" ]; then
    echo "umbraco-cloud-no-version"
    exit 0
  fi
  echo "none"
  exit 0
fi

echo "$VERSION"
