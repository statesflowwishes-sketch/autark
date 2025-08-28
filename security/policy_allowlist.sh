#!/usr/bin/env bash
# Beispiel: Prüft ob Kommando im erlaubten Muster
CMD="$*"
ALLOW_PATTERNS=(
  "^git (status|add|commit|diff|restore|checkout)"
  "^pytest( |$)"
  "^npm (install|run build)"
  "^pip install"
  "^ls( |$)"
  "^cat "
)
for p in "${ALLOW_PATTERNS[@]}"; do
  if [[ "$CMD" =~ $p ]]; then
    exit 0
  fi
done
echo "Command blocked by policy: $CMD" >&2
exit 1