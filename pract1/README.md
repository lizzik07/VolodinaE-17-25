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
