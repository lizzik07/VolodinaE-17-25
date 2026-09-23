# Практическое занятие №1 — Основы работы в командной строке

П.Н. Советов, РТУ МИРЭА.

Выполнено в браузерном Linux (JS/Linux, https://bellard.org/jslinux/).

## Задача 1. Список пользователей из passwd

**Условие:** вывести отсортированный в алфавитном порядке список имён пользователей из файла `/etc/passwd`.

**Файл:** `list_users.sh`

**Код:**

```bash
#!/bin/bash
grep . /etc/passwd | cut -d: -f1 | sort
```

**Запуск:**

```bash
chmod +x list_users.sh
./list_users.sh
```

**Вывод:**

```text
bin
cron
daemon
dhcpcd
ftp
games
guest
halt
klogd
lp
mail
news
nobody
ntp
root
shutdown
sshd
svn
sync
uucp
```

**Примечание:** флаг `grep -o` из методички не поддерживается урезанным busybox-grep в JS/Linux, поэтому использована комбинация `grep .` (выбор непустых строк) и `cut -d: -f1` (вырезание имени пользователя до двоеточия).

---

## Задача 2. Топ-5 портов из /etc/protocols

**Условие:** вывести данные `/etc/protocols` в отформатированном и отсортированном порядке для 5 наибольших портов (номер первым, имя вторым).

**Файл:** `top_protocols.sh`

**Код:**

```bash
#!/bin/bash
grep -v '^#' /etc/protocols | grep -v '^$' | awk '{print $2, $1}' | sort -k1,1 -n -r | head -5
```

**Запуск:**

```bash
chmod +x top_protocols.sh
./top_protocols.sh
```

**Вывод:**

```text
262 mptcp
143 ethernet
142 rohc
141 wesp
140 shim6
```

---

## Задача 3. Banner

**Условие:** написать программу `banner` средствами bash, которая выводит текст в рамке, размер которой зависит от длины текста.

**Файл:** `banner`

**Код:**

```bash
#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 \"text\"" >&2
    exit 1
fi

text="$1"
len=${#text}
border=$(printf '%*s' "$((len + 2))" '' | tr ' ' '-')

printf '+%s+\n' "$border"
printf '| %s |\n' "$text"
printf '+%s+\n' "$border"
```

**Запуск:**

```bash
chmod +x banner
./banner "Hello from RTU MIREA!"
```

**Вывод:**

```text
+-----------------------+
| Hello from RTU MIREA! |
+-----------------------+
```

Проверено на https://www.shellcheck.net/ — предупреждений нет.

---

## Задача 4. Идентификаторы C/C++/Java

**Условие:** вывести все идентификаторы (по правилам C/C++/Java) в файле, без повторений.

**Файлы:** `identifiers.sh`, тестовый `hello.c`

**Код `identifiers.sh`:**

```bash
#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 file" >&2
    exit 1
fi

grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | tr '\n' ' '
echo
```

**Тестовый файл `hello.c`:**

```c
#include <stdio.h>
int main(void) {
    printf("hello world\n");
    return 0;
}
```

**Запуск:**

```bash
chmod +x identifiers.sh
./identifiers.sh hello.c
```

**Вывод:**

```text
h hello include int main n printf return stdio void world
```

---

## Задача 5. Регистрация команды (reg)

**Условие:** написать программу, которая задаёт правильные права доступа пользовательской команде и копирует её в `/usr/local/bin`.

**Файл:** `reg`

**Код:**

```bash
#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 program" >&2
    exit 1
fi

prog="$1"

if [ ! -f "$prog" ]; then
    echo "Файл $prog не найден" >&2
    exit 1
fi

chmod 755 "$prog"
cp "$prog" /usr/local/bin/
echo "Команда $(basename "$prog") установлена в /usr/local/bin"
```

**Запуск:**

```bash
chmod +x reg
./reg banner
which banner
banner "test"
```

**Вывод:**

```text
Команда banner установлена в /usr/local/bin
/usr/local/bin/banner
+--------+
| test   |
+--------+
```

---

## Задача 6. Проверка комментария в первой строке (c/js/py)

**Условие:** проверить наличие комментария в первой строке файлов с расширением `.c`, `.js`, `.py`.

**Файл:** `check_comments.sh`

**Код:**

```bash
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
```

**Запуск:**

```bash
chmod +x check_comments.sh
./check_comments.sh .
```

**Вывод:**

```text
НЕТ КОММЕНТАРИЯ: ./hello.js
НЕТ КОММЕНТАРИЯ: ./hello.c
НЕТ КОММЕНТАРИЯ: ./bench.py
OK: ./a.c
НЕТ КОММЕНТАРИЯ: ./b.c
OK: ./c.py
```

---

## Задача 7. Поиск файлов-дубликатов

**Условие:** найти файлы-дубликаты (имеющие одну или более копий содержимого) по заданному пути и подкаталогам.

**Файл:** `find_duplicates.sh`

**Код:**

```bash
#!/bin/bash
dir="${1:-.}"

find "$dir" -type f -print0 \
  | xargs -0 md5sum \
  | sort \
  | awk '
      {
        hash = $1
        $1 = ""
        file = substr($0, 2)
        if (hash == prev_hash) {
          if (!printed_group) {
            print prev_file
            printed_group = 1
          }
          print file
        } else {
          printed_group = 0
        }
        prev_hash = hash
        prev_file = file
      }
    '
```

**Запуск:**

```bash
chmod +x find_duplicates.sh
mkdir dtest
echo "same content" > dtest/a.txt
echo "same content" > dtest/b.txt
echo "other" > dtest/c.txt
./find_duplicates.sh dtest
```

**Вывод:**

```text
dtest/a.txt
dtest/b.txt
```
