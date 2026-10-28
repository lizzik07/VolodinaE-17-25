#!/bin/bash
for f in *.c *.js *.py; do
    head -n1 "$f" | grep -qE '^\s*(//|#|/\*)' \
        && echo "OK: $f" \
        || echo "НЕТ: $f"
done
