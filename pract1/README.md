# Практическое занятие №1 — Основы работы в командной строке

П.Н. Советов, РТУ МИРЭА.

Выполнено в браузерном Linux (JS/Linux, https://bellard.org/jslinux/).

## Задача 1. Список пользователей

**Файл:** `list_users.sh`

```bash
#!/bin/bash
grep . /etc/passwd | cut -d: -f1 | sort
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

---

## Задача 2. Топ-5 портов

**Файл:** `top_protocols.sh`

```bash
#!/bin/bash
grep -v '^#' /etc/protocols | grep -v '^$' | awk '{print $2, $1}' | sort -k1,1 -n -r | head -5
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

**Файл:** `banner`

```bash
#!/bin/bash
b=$(printf '%*s' $((${#1} + 2)) '' | tr ' ' '-')
echo "+$b+"
echo "| $1 |"
echo "+$b+"
```

**Вывод при `./banner "Hello from RTU MIREA!"`:**

```text
+-----------------------+
| Hello from RTU MIREA! |
+-----------------------+
```

---

## Задача 4. Идентификаторы C/C++/Java

**Файл:** `identifiers.sh`

```bash
#!/bin/bash
grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | tr '\n' ' '
echo
```

**Вывод при `./identifiers.sh hello.c`:**

```text
h hello include int main n printf return stdio void world
```

---

## Задача 5. Регистрация команды (reg)

**Файл:** `reg`

```bash
#!/bin/bash
chmod 755 "$1"
cp "$1" /usr/local/bin/
```

**Запуск:** `./reg banner`

**Вывод:**

```text
(команда banner установлена в /usr/local/bin)
```

---

## Задача 6. Проверка комментария в первой строке

**Файл:** `check_comments.sh`

```bash
#!/bin/bash
for f in *.c *.js *.py; do
    head -n1 "$f" | grep -qE '^\s*(//|#|/\*)' \
        && echo "OK: $f" \
        || echo "НЕТ: $f"
done
```

**Вывод при `./check_comments.sh`:**

```text
OK: a.c
НЕТ: b.c
OK: c.py
```

---

## Задача 7. Поиск файлов-дубликатов

**Файл:** `find_duplicates.sh`

```bash
#!/bin/bash
find "${1:-.}" -type f -exec md5sum {} + | sort | uniq -w32 -D
```

**Вывод при `./find_duplicates.sh dtest`:**

```text
dtest/a.txt
dtest/b.txt
```

---

## Задача 8. Архивация файлов по расширению

**Файл:** `archive_by_ext.sh`

```bash
#!/bin/bash
tar -cf "archive_${1}.tar" *."${1}"
```

**Запуск:** `./archive_by_ext.sh txt`

**Вывод:**

```text
(создан архив archive_txt.tar)
```

---

## Задача 9. Замена 4 пробелов на табуляцию

**Файл:** `spaces_to_tabs.sh`

```bash
#!/bin/bash
sed 's/    /\t/g' "$1" > "$2"
```

**Запуск:** `./spaces_to_tabs.sh in.txt out.txt`

**Вывод при `cat -A out.txt`:**

```text
hello^Iworld$
^Iindented line$
```

---

## Задача 10. Поиск пустых файлов

**Файл:** `empty_files.sh`

```bash
#!/bin/bash
find "${1:-.}" -maxdepth 1 -type f -empty
```

**Вывод при `./empty_files.sh testdir`:**

```text
testdir/empty1.txt
testdir/empty2.txt
```
