# Граф зависимостей npm: вариант №6

Практическая работа по сборнику №2, ИКБО-17-25.
Этап 1: настраиваемый CLI, проверки ошибок и вывод конфигурации.

Python 3.9+, стандартная библиотека; сборка не требуется.

```sh
./run.sh --package A --depth 3
python3 -m unittest discover -s tests -v
```

Настройки и функции описаны в docstring модулей src/config.py и src/main.py.

Этап 2: src/repository.py получает npm JSON напрямую через urllib;
src/semver.py самостоятельно выбирает версии по диапазонам зависимостей.

```sh
./run.sh --package is-odd --version 3.0.1
```
