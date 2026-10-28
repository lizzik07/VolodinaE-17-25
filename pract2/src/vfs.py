import csv
import sys


class VFSNode:
    """Узел виртуальной файловой системы."""

    def __init__(self, name, is_dir=True, content=""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}


class VFS:
    """Класс виртуальной файловой системы."""

    def __init__(self):
        # Корень всегда существует
        self.root = VFSNode("/", is_dir=True)

    def load_from_csv(self, filepath):
        """Загружает структуру из CSV-файла.
        
        Формат CSV: path,type,content
        Пример:
        /dir1,dir,
        /dir1/file.txt,file,Hello World
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) < 2:
                        continue
                    path, node_type = row[0], row[1]
                    content = row[2] if len(row) > 2 else ""
                    self._create_node(path, node_type, content)
        except FileNotFoundError:
            print(
                f"Ошибка VFS: файл '{filepath}' не найден.",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(
                f"Ошибка VFS: неверный формат файла ({e}).",
                file=sys.stderr,
            )
            sys.exit(1)

    def _create_node(self, path, node_type, content):
        """Вспомогательный метод для создания узлов по пути."""
        parts = [p for p in path.split("/") if p]
        current = self.root

        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            is_dir = (node_type == "dir") if is_last else True

            if part not in current.children:
                current.children[part] = VFSNode(
                    part, is_dir, content if is_last else ""
                )

            current = current.children[part]