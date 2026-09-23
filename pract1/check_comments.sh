#!/bin/bash
dir="${1:-.}"

find "$dir" -type f \( -name "*.c" -o -name "*.js" -o -name "*.py" \) | while read -r f; do
    first_line=$(head -n 1 "$f")
    case "$f" in
        *.py)
            if [[ "$first_line" == \#* ]]; then
                echo "OK: $f"
            else
                echo "НЕТ КОММЕНТАРИЯ: $f"
            fi
            ;;
        *.c|*.js)
            if [[ "$first_line" == //* ]] || [[ "$first_line" == /\** ]]; then
                echo "OK: $f"
            else
                echo "НЕТ КОММЕНТАРИЯ: $f"
            fi
            ;;
    esac
done
