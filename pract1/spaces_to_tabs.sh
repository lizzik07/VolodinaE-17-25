#!/bin/bash
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: $0 input output" >&2
    exit 1
fi

input="$1"
output="$2"
tab=$(printf '\t')

sed "s/    /${tab}/g" "$input" > "$output"
