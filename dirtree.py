import os
from pathlib import Path
import argparse


def generate_directory_tree(
    root_dir,
    exclude_dirs=None,
    exclude_extensions=None,
    exclude_files=None,
    max_depth=None,
    current_depth=0,
):
    """
    Генерирует дерево директорий проекта и выводит в консоль.

    Args:
        root_dir (str или Path): Корневая директория проекта
        exclude_dirs (list): Список директорий для исключения
        exclude_extensions (list): Список расширений файлов для исключения
        exclude_files (list): Список конкретных файлов для исключения
        max_depth (int): Максимальная глубина рекурсии
        current_depth (int): Текущая глубина (для внутреннего использования)
    """
    if exclude_dirs is None:
        exclude_dirs = [
            ".venv",
            "venv",
            "env",
            ".env",
            "__pycache__",
            ".git",
            "node_modules",
            ".idea",
            ".vscode",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            "*.egg-info",
            "coverage",
            ".coverage",
            "htmlcov",
        ]

    if exclude_extensions is None:
        exclude_extensions = [
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".log",
            ".tmp",
            ".temp",
            ".cache",
            ".swp",
            ".db",
            ".sqlite",
            ".sqlite3",
        ]

    if exclude_files is None:
        exclude_files = [
            ".DS_Store",
            "Thumbs.db",
            ".gitignore",
            ".gitattributes",
            ".env.example",
            ".env.local",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "README.md",
            "LICENSE",
            "MANIFEST.in",
        ]

    root_path = Path(root_dir)

    if not root_path.exists():
        print(f"Директория {root_path} не существует!")
        return

    if not root_path.is_dir():
        print(f"{root_path} не является директорией!")
        return

    indent = "    " * current_depth

    try:
        items = sorted(
            root_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        )

        for i, item in enumerate(items):
            # Пропускаем скрытые файлы/папки (начинающиеся с .)
            if item.name.startswith(".") and item.name not in [".", ".."]:
                continue

            # Проверяем исключенные директории
            if item.is_dir():
                skip_dir = False
                for pattern in exclude_dirs:
                    if "*" in pattern:
                        pattern = pattern.replace("*", ".*")
                        import re

                        if re.match(pattern, item.name):
                            skip_dir = True
                            break
                    elif item.name == pattern:
                        skip_dir = True
                        break

                if skip_dir:
                    continue

            # Проверяем максимальную глубину
            if max_depth is not None and current_depth >= max_depth:
                continue

            # Определяем префикс для текущего элемента
            if i == len(items) - 1:
                prefix = "└── "
                next_indent = "    "
            else:
                prefix = "├── "
                next_indent = "│   "

            # Обрабатываем директории
            if item.is_dir():
                print(f"{indent}{prefix}{item.name}/")
                # Рекурсивно обрабатываем поддиректорию
                generate_directory_tree(
                    item,
                    exclude_dirs,
                    exclude_extensions,
                    exclude_files,
                    max_depth,
                    current_depth + 1,
                )
            # Обрабатываем файлы
            else:
                # Пропускаем исключенные файлы
                if item.name in exclude_files:
                    continue

                # Пропускаем файлы с исключенными расширениями
                skip_file = False
                for ext in exclude_extensions:
                    if item.name.endswith(ext):
                        skip_file = True
                        break

                if not skip_file:
                    print(f"{indent}{prefix}{item.name}")

    except PermissionError:
        print(f"{indent}└── [Доступ запрещен]")


def main():
    parser = argparse.ArgumentParser(
        description="Генерация структуры директорий проекта с выводом в консоль",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python script.py                    # Текущая директория
  python script.py /path/to/project   # Указанная директория
  python script.py -d 2               # Ограничить глубину 2 уровнями
  python script.py -e node_modules    # Исключить дополнительную директорию
        """,
    )

    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Корневая директория проекта (по умолчанию: текущая)",
    )
    parser.add_argument(
        "-d", "--depth", type=int, help="Максимальная глубина отображения"
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        help="Дополнительные директории для исключения (можно использовать несколько раз)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Показывать все файлы, включая скрытые и служебные",
    )

    args = parser.parse_args()

    # Настраиваем исключения в зависимости от аргументов
    exclude_dirs = None
    exclude_extensions = None
    exclude_files = None

    if not args.all:
        # Базовые исключения
        exclude_dirs = [
            ".venv",
            "venv",
            "env",
            ".env",
            "__pycache__",
            ".git",
            "node_modules",
            ".idea",
            ".vscode",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            "*.egg-info",
            "coverage",
            ".coverage",
            "htmlcov",
        ]

        exclude_extensions = [
            ".pyc",
            ".pyo",
            ".pyd",
            ".so",
            ".dll",
            ".exe",
            ".log",
            ".tmp",
            ".temp",
            ".cache",
            ".swp",
            ".db",
            ".sqlite",
            ".sqlite3",
            ".class",
            ".jar",
            ".war",
            ".ear",
            ".zip",
            ".tar",
            ".gz",
            ".7z",
            ".rar",
            ".whl",
            ".egg",
        ]

        exclude_files = [
            ".DS_Store",
            "Thumbs.db",
            ".gitignore",
            ".gitattributes",
            ".env.example",
            ".env.local",
        ]
    else:
        # В режиме --all только самые необходимые исключения
        exclude_dirs = [".venv", "__pycache__"]
        exclude_extensions = [".pyc", ".pyo", ".pyd"]
        exclude_files = []

    # Добавляем пользовательские исключения
    if args.exclude:
        exclude_dirs.extend(args.exclude)

    print(f"\n📁 Структура проекта: {os.path.abspath(args.root_dir)}")
    print("=" * 60)

    generate_directory_tree(
        root_dir=args.root_dir,
        exclude_dirs=exclude_dirs,
        exclude_extensions=exclude_extensions,
        exclude_files=exclude_files,
        max_depth=args.depth,
    )

    print("=" * 60)
    print(
        f"📊 Глубина: {'без ограничений' if not args.depth else args.depth} уровня(ей)"
    )
    print(f"⚙️  Исключены: .venv, __pycache__, .pyc файлы и другие служебные файлы\n")


if __name__ == "__main__":
    main()
