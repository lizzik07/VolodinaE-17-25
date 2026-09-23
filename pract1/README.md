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
