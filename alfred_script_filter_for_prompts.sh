#!/bin/bash

PROMPTS_DIR="$HOME/Local-Projects-2026/Quick-Prompter/Project-Init/prompts"
# Alfred JSON output
echo '{"items": ['
first=true
for file in "$PROMPTS_DIR"/*.md; do
  if [ -f "$file" ]; then
    filename=$(basename "$file" .md)
    # Remove extension and format for display
    
    if [ "$first" = true ]; then
      first=false
    else
      echo ","
    fi
    
    printf '{"title": "%s", "subtitle": "%s", "arg": "%s", "icon": {"type": "fileicon", "path": "%s"}}' \
      "$filename" "$file" "$file" "$file"
  fi
done
echo ']}'