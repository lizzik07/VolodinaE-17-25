#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 extension" >&2
    exit 1
fi

ext="$1"
archive="archive_${ext}.tar"

files=$(find . -maxdepth 1 -type f -name "*.${ext}")

if [ -z "$files" ]; then
    echo "Файлы с расширением .$ext не найдены" >&2
    exit 1
fi

find . -maxdepth 1 -type f -name "*.${ext}" -print0 | xargs -0 tar -cvf "$archive"
echo "Создан архив: $archive"
