import argparse
import os
import socket
import sys
from vfs import VFS


def get_prompt():
    """Формирует приглашение вида username@hostname:cwd$."""
    user = os.getenv("USER", "user")
    host = socket.gethostname()
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = cwd.replace(home, "~", 1)
    return f"{user}@{host}:{cwd}$ "


def parse_input(user_input):
    """Простой парсер."""
    return user_input.split()


def execute_command(parts):
    """Выполняет команду, возвращает True, если нужно выйти."""
    if not parts:
        return False

    command = parts[0]
    args = parts[1:]

    if command == "exit":
        print("Завершение работы эмулятора.")
        return True
    elif command == "ls":
        print(f"Вызвана команда ls с аргументами: {args}")
    elif command == "cd":
        print(f"Вызвана команда cd с аргументами: {args}")
    else:
        print(f"Ошибка: неизвестная команда '{command}'")

    return False


def run_script(script_path):
    """Читает и выполняет стартовый скрипт."""
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                print(f"{get_prompt()}{line}")
                parts = parse_input(line)
                should_exit = execute_command(parts)
                if should_exit:
                    break
    except FileNotFoundError:
        print(
            f"Ошибка: файл скрипта '{script_path}' не найден.",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument(
        "--vfs", default="vfs.zip", help="Путь к файлу VFS"
    )
    parser.add_argument(
        "--script", default=None, help="Путь к стартовому скрипту"
    )
    args = parser.parse_args()

    print("--- Отладка параметров ---")
    print(f"VFS path: {args.vfs}")
    print(f"Script path: {args.script}")
    print("--------------------------")

    vfs = VFS()
    if args.vfs:
        print(f"Загрузка VFS из {args.vfs}...")
        vfs.load_from_csv(args.vfs)
        print("VFS успешно загружена в память.")

    if args.script:
        print(f"Выполнение скрипта {args.script}...")
        run_script(args.script)
    else:
        while True:
            try:
                user_input = input(get_prompt())
            except (KeyboardInterrupt, EOFError):
                print("\nВыход...")
                break

            if not user_input.strip():
                continue

            parts = parse_input(user_input)
            if execute_command(parts):
                break


if __name__ == "__main__":
    main()
