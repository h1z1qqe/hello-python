# hello-python — CI/CD на Python CLI с публикацией бинарников в GitHub Releases

[![Python CI/CD](https://github.com/h1z1qqe/hello-python/actions/workflows/ci.yml/badge.svg)](https://github.com/h1z1qqe/hello-python/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/h1z1qqe/hello-python?label=release)](https://github.com/h1z1qqe/hello-python/releases)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyInstaller](https://img.shields.io/badge/PyInstaller-6.11.0-9B4FBA)](https://pyinstaller.org/)
[![Lint: ruff](https://img.shields.io/badge/lint-ruff-261230)](https://github.com/astral-sh/ruff)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC)](https://docs.pytest.org/)

**Отчёт по лабораторной работе.** Проект демонстрирует полный цикл CI/CD для CLI-приложения на Python: автоматическая сборка в самодостаточные исполняемые файлы для Linux, macOS и Windows через PyInstaller и публикация их в GitHub Releases при push тега `v*`.

---

## Содержание

1. [Цель работы](#1-цель-работы)
2. [Теоретическая часть](#2-теоретическая-часть)
3. [Инструменты и технологии](#3-инструменты-и-технологии)
4. [Структура проекта](#4-структура-проекта)
5. [Ход выполнения работы](#5-ход-выполнения-работы)
6. [Устройство CI/CD-пайплайна](#6-устройство-cicd-пайплайна)
7. [Результаты работы](#7-результаты-работы)
8. [Выводы](#8-выводы)
9. [Приложение: быстрый старт](#9-приложение-быстрый-старт)

## 1. Цель работы

Цель — научиться автоматически собирать CLI-приложение на Python в самодостаточные исполняемые файлы под Linux, macOS и Windows и публиковать их в GitHub Releases при push тега `v*`. Пользователь такого приложения скачивает один файл и запускает его без установки Python, интерпретатор и зависимости уже упакованы внутрь.

Для достижения цели решались следующие задачи:

- создать проект Python CLI с модульной структурой, тестами (pytest) и конфигурацией `pyproject.toml`;
- настроить workflow GitHub Actions с матричной сборкой — три ОС собираются параллельно на трёх runner'ах;
- освоить публикацию артефактов в Releases через `softprops/action-gh-release`;
- освоить семантическое версионирование и полный цикл обновления релиза: `v0.1.0` → `v0.2.0`.

## 2. Теоретическая часть

### 2.1 PyInstaller

**PyInstaller** — инструмент, который превращает Python-скрипт в самодостаточный исполняемый файл: внутрь упаковывается интерпретатор Python, все зависимости и код приложения. Пользователь скачивает один файл и запускает его без установленного Python и без виртуальных окружений. Режим `--onefile` собирает всё в один бинарник, который при запуске распаковывает себя во временный каталог. Размер такого файла — порядка 10–15 МБ, поскольку внутрь входит целиком интерпретатор.

### 2.2 GitHub Releases

**GitHub Releases** — раздел репозитория, где публикуются версии проекта: git-теги, описания изменений и прикреплённые файлы для скачивания. Релиз в этой работе создаётся автоматически action'ом `softprops/action-gh-release` при push тега вида `v0.1.0`; опция `generate_release_notes: true` формирует список изменений из коммитов. Важное свойство релизов — **неизменяемость**: нельзя перезаписать файлы внутри уже опубликованной версии, для нового кода выпускается новая версия.

### 2.3 Почему нет cross-compilation: Go/Rust vs Python

Компиляторы Go и Rust умеют cross-compilation — один runner собирает бинарники сразу под все платформы. Python так не умеет: PyInstaller встраивает платформо-зависимый интерпретатор и нативные библиотеки (`.so` / `.dylib` / `.dll`), поэтому сборка должна выполняться на той же ОС, под которую готовится бинарник. Отсюда в CI используется матрица из трёх runner'ов.

| Характеристика | Go / Rust | Python + PyInstaller |
|---|---|---|
| Cross-compilation с одного runner'а | да | нет |
| Интерпретатор в артефакте | не нужен (нативный код) | встраивается целиком |
| Сборка под 3 ОС | 1 job | 3 параллельных job'а |
| Результат | один бинарник | три платформо-зависимых бинарника |

### 2.4 Матричные сборки GitHub Actions

`strategy.matrix` описывает список вариантов, для каждого GitHub Actions создаёт отдельный параллельный job. В этой работе матрица собирает приложение на `ubuntu-latest` (Linux x64), `macos-14` (Apple Silicon, arm64) и `windows-latest` (Windows x64). Все три сборки идут одновременно, что сокращает общее время пайплайна.

### 2.5 Семантическое версионирование

Версии имеют формат `MAJOR.MINOR.PATCH`:

| Что изменили | Какую версию | Пример |
|---|---|---|
| Исправили баг | patch | `0.1.0` → `0.1.1` |
| Добавили функцию | minor | `0.1.0` → `0.2.0` |
| Сломали совместимость | major | `0.1.0` → `1.0.0` |

В работе выполняется обновление `0.1.0` → `0.2.0` — добавление новой функциональности, то есть minor.

### 2.6 CI и CI/CD

**CI (Continuous Integration)** — при каждом push в `main` и каждом pull request автоматически запускаются линтер (`ruff`) и тесты (`pytest`): это job `test`. **CI/CD** добавляет этап доставки: при push тега `v*` job `release` собирает бинарники и публикует их в Releases. Условие `if: startsWith(github.ref, 'refs/tags/v')` разделяет этапы — релизный job запускается только по тегу, а не по обычному push.

## 3. Инструменты и технологии

| Инструмент | Версия | Назначение |
|---|---|---|
| Python | 3.12 | Язык разработки, среда выполнения |
| pytest | 8.3.3 | Модульные тесты |
| ruff | 0.7.1 | Линтер и форматтер |
| PyInstaller | 6.11.0 | Сборка бинарников в режиме `--onefile` |
| Docker | `python:3.12-slim`, `debian:stable-slim` | Локальные проверки и запуск бинарника в чистом окружении |
| GitHub Actions | `actions/checkout@v7`, `actions/setup-python@v5` | CI/CD-пайплайн, матричные сборки |
| softprops/action-gh-release | v2 | Автоматическая публикация релизов |

## 4. Структура проекта

```text
hello-python/
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD-пайплайн GitHub Actions
├── hello/
│   ├── __init__.py         # версия пакета (__version__)
│   └── greeting.py         # функции greet() и sum_range()
├── tests/
│   └── test_greeting.py    # модульные тесты pytest
├── .gitignore              # исключения git (venv, dist, кэши)
├── main.py                 # точка входа CLI (функция main())
├── pyproject.toml          # метаданные проекта, версия, конфигурация pytest
└── requirements.txt        # зависимости: pytest, pyinstaller
```

## 5. Ход выполнения работы

Лабораторная выполнялась в **GitHub Codespaces** (Linux-окружение), все команды — bash. Структура проекта создана одной bash-командой (`mkdir` + `cat` с heredoc-блоками) согласно заданию: создаются каталоги `.github/workflows`, `hello`, `tests` и записываются все файлы проекта.

### 5.1 Проверка структуры проекта

```shell
cd ~/hello-python
find . -type f | sort
```

Ожидаемый вывод:

```text
./.github/workflows/ci.yml
./.gitignore
./hello/__init__.py
./hello/greeting.py
./main.py
./pyproject.toml
./requirements.txt
./tests/test_greeting.py
```

### 5.2 Тесты в Docker (Python на хосте не нужен)

Тесты запускаются в контейнере `python:3.12-slim` с монтированием каталога проекта:

```shell
cd ~/hello-python
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$(pwd)":/app \
  -v ~/.pip-docker-cache:/tmp/.cache/pip \
  -w /app \
  python:3.12-slim \
  sh -c "pip install --cache-dir=/tmp/.cache/pip -r requirements.txt && python -m pytest -v"
```

Ожидаемый вывод — оба теста прошли:

```text
tests/test_greeting.py::test_greet PASSED
tests/test_greeting.py::test_sum_range PASSED
========================= 2 passed in 0.12s =========================
```

Примечание для Codespaces: Docker доступен в окружении из коробки (проверяется командой `docker --version`). Если Docker недоступен, тесты можно запустить напрямую через виртуальное окружение:

```shell
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python -m pytest -v
```

### 5.3 Локальная сборка бинарника через PyInstaller

```shell
cd ~/hello-python
docker run --rm \
  -u "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$(pwd)":/app \
  -v ~/.pip-docker-cache:/tmp/.cache/pip \
  -w /app \
  python:3.12 \
  sh -c "pip install --cache-dir=/tmp/.cache/pip -r requirements.txt && \
         python -m PyInstaller --onefile --name hello-python main.py && \
         ls -la dist/"
```

После сборки в каталоге `dist/` появляется файл `hello-python` размером около 12 МБ — в нём упакованы интерпретатор, зависимости и код.

### 5.4 Запуск бинарника в чистом контейнере

Проверяем, что бинарник самодостаточен: запускаем его в контейнере `debian:stable-slim`, в котором Python отсутствует.

```shell
docker run --rm \
  -v "$(pwd)/dist":/dist \
  debian:stable-slim \
  /dist/hello-python
```

Ожидаемый вывод:

```text
hello-python version 0.1.0
Hello from Python! 🐍📦
OS: linux
Arch: x86_64
Hello, GitHub!
Sum 1..10 = 55
```

Бинарник, собранный в Linux-контейнере, не запустится на Windows или macOS — PyInstaller не умеет cross-compilation, под каждую ОС нужна своя сборка. Именно поэтому в CI используется матрица с тремя runner'ами.

### 5.5 Создание репозитория на GitHub и первый push

На GitHub создан **пустой** публичный репозиторий `hello-python` — без README.md, .gitignore и лицензии, иначе push будет отклонён. Затем проект отправлен в репозиторий:

```shell
cd ~/hello-python
git init
git add .
git commit -m "Initial commit: Python CLI with PyInstaller and CI/CD to Releases"
git branch -M main
git remote add origin "https://github.com/h1z1qqe/hello-python.git"
git remote -v
git push -u origin main
```

### 5.6 Первый запуск CI (без релиза)

После push в `main` во вкладке **Actions** запустился workflow **Python CI/CD** (выполняется примерно 2–3 минуты). Job `test` прошёл все проверки: `ruff check`, `ruff format --check`, `pytest`. Job `release` был пропущен — push был в ветку, а не тег. Это штатное поведение: релиз создаётся только при push тега `v*`.

### 5.7 Публикация релиза v0.1.0

Когда код в `main` стабилен и CI зелёный, создаётся тег:

```shell
git tag v0.1.0
git push origin v0.1.0
```

Что произошло после push тега:

- `test` — снова прогнал линтер и тесты;
- `release` — собрал бинарники параллельно на трёх ОС (ubuntu-latest, macos-14, windows-latest);
- создался **GitHub Release v0.1.0** с тремя прикреплёнными файлами.

Проверка: `https://github.com/h1z1qqe/hello-python/releases` — релиз v0.1.0 с файлами `hello-python-linux-x64`, `hello-python-macos-arm64`, `hello-python-windows-x64.exe`.

### 5.8 Скачивание и запуск бинарника

```shell
cd ~
wget "https://github.com/h1z1qqe/hello-python/releases/download/v0.1.0/hello-python-linux-x64" -O hello-python
chmod +x hello-python
./hello-python
```

Вывод совпадает с ожидаемым — бинарник работает без установленного Python:

```text
hello-python version 0.1.0
Hello from Python! 🐍📦
OS: linux
Arch: x86_64
Hello, GitHub!
Sum 1..10 = 55
```

### 5.9 Обновление релиза: v0.1.0 → v0.2.0

По семантическому версионированию добавление новой функциональности — это minor: `0.1.0` → `0.2.0`. Выполнен полный цикл обновления:

1. **Изменён код**: в `hello/greeting.py` добавлена функция `factorial()`, в `main.py` — вывод `Factorial 5 = 120`, в `tests/test_greeting.py` — тест `test_factorial`. **Версия обновлена в двух файлах** — `pyproject.toml` (`version = "0.2.0"`) и `hello/__init__.py` (`__version__ = "0.2.0"`). Оба файла должны совпадать, иначе в бинарнике останется старая версия.
2. **Проверка форматирования и тестов перед push** — CI запускает `ruff format --check`, неотформатированный код уронит workflow. Локально: ruff — `All checks passed!`, pytest — `3 passed` (включая новый `test_factorial`).
3. **Коммит и push в main** — job `test` проходит, job `release` пропускается (это push ветки, не тега):

```shell
git add .
git commit -m "feat: bump version to 0.2.0"
git push origin main
```

4. **Новый тег** — только после зелёного CI:

```shell
git tag v0.2.0
git push origin v0.2.0
```

5. **Проверка результата:** `https://github.com/h1z1qqe/hello-python/releases` — два релиза: `v0.1.0` (старый, не тронут) и `v0.2.0` (новый). Скачан обновлённый бинарник и проверен запуск — версия `0.2.0`.

Если тег создан ошибочно: удалить локально `git tag -d v0.2.0`, на GitHub — `git push origin :refs/tags/v0.2.0`, затем удалить релиз на странице Releases, исправить код и повторить. Релизы в GitHub **неизменяемы** — нельзя перезаписать файлы внутри уже опубликованной версии.

## 6. Устройство CI/CD-пайплайна

Workflow `.github/workflows/ci.yml` (**Python CI/CD**) запускается на: push в `main`, push тегов `v*` и на pull request:

```yaml
on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
```

### 6.1 Job test (этап CI)

| Параметр | Значение |
|---|---|
| Runner | `ubuntu-latest` |
| Шаги | checkout → setup-python 3.12 (кэш pip) → установка зависимостей → `ruff check .` → `ruff format --check .` → `pytest -v` |
| Когда запускается | каждый push в `main` и каждый pull request |

### 6.2 Job release (этап CD)

| Параметр | Значение |
|---|---|
| Условие запуска | `needs: test` и `if: startsWith(github.ref, 'refs/tags/v')` |
| Runner | матрица из трёх ОС |
| Права | `permissions: contents: write` — требуется для создания релиза |
| Сборка | `python -m PyInstaller --onefile --name hello-python main.py` |
| Публикация | `softprops/action-gh-release@v2`, `generate_release_notes: true` |

Матрица артефактов:

| Runner | ОС / архитектура | Артефакт |
|---|---|---|
| ubuntu-latest | Linux x64 | `hello-python-linux-x64` |
| macos-14 | macOS Apple Silicon (arm64) | `hello-python-macos-arm64` |
| windows-latest | Windows x64 | `hello-python-windows-x64.exe` |

Ключевой фрагмент матрицы:

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        artifact: hello-python-linux-x64
      - os: macos-14
        artifact: hello-python-macos-arm64
      - os: windows-latest
        artifact: hello-python-windows-x64.exe
```

Для Windows используется отдельный шаг переименования с условием `if: runner.os == 'Windows'`, потому что PyInstaller на Windows создаёт файл с расширением `.exe`.

## 7. Результаты работы

- Репозиторий: <https://github.com/h1z1qqe/hello-python>
- Actions: <https://github.com/h1z1qqe/hello-python/actions>
- Releases: <https://github.com/h1z1qqe/hello-python/releases>

| Релиз | Тип версии | Файлы | Состояние |
|---|---|---|---|
| v0.1.0 | начальная версия | `hello-python-linux-x64`, `hello-python-macos-arm64`, `hello-python-windows-x64.exe` | опубликован, не изменялся |
| v0.2.0 | minor — новая функциональность | `hello-python-linux-x64`, `hello-python-macos-arm64`, `hello-python-windows-x64.exe` | опубликован |

Все проверки job `test` проходят (ruff + pytest), релизные job'ы собирают бинарники на трёх ОС параллельно и публикуют их в Release автоматически.

## 8. Выводы

В ходе лабораторной работы настроен полный цикл CI/CD для Python CLI-приложения: от локальной разработки до автоматической публикации готовых бинарников под три операционные системы.

1. **PyInstaller** упаковывает интерпретатор, зависимости и код в один самодостаточный файл (`--onefile`). Самодостаточность проверена запуском бинарника в чистом контейнере Debian, где Python отсутствует.
2. **В Python нет cross-compilation** (в отличие от Go/Rust): PyInstaller встраивает платформо-зависимый интерпретатор, поэтому сборка под каждую ОС выполняется на своём runner'е — для трёх платформ нужна матрица из трёх параллельных job'ов.
3. **GitHub Actions**: матричные сборки (`strategy.matrix`) запускают три job'а одновременно; job'у релиза требуется право `contents: write`; публикация выполняется action'ом `softprops/action-gh-release` с автогенерацией release notes.
4. **Семантическое версионирование**: обновление `v0.1.0` → `v0.2.0` (minor). Версия обновляется синхронно в двух файлах (`pyproject.toml` и `hello/__init__.py`); релизы неизменяемы — старая версия остаётся доступной пользователям.
5. **Разница CI и CI/CD**: CI (ruff + pytest на каждый push и PR) контролирует качество кода; CD добавляет автоматическую доставку — сборку и публикацию артефактов по тегу. Этапы разделены условием `if: startsWith(github.ref, 'refs/tags/v')`.

Что освоено:

- Python: `pyproject.toml`, виртуальные окружения (venv), pip, запуск модулей (`python -m`);
- pytest: структура и запуск модульных тестов;
- ruff: быстрый линтер и форматтер для Python;
- матричные сборки GitHub Actions: 3 ОС параллельно;
- PyInstaller: режим `--onefile`, упаковка интерпретатора и зависимостей;
- GitHub Releases: публикация бинарников через `softprops/action-gh-release`;
- семантическое версионирование и полный цикл обновления релиза: версия → формат → тесты → тег → новый Release.

## 9. Приложение: быстрый старт

Скачать и запустить готовый бинарник (Linux):

```shell
wget "https://github.com/h1z1qqe/hello-python/releases/download/v0.2.0/hello-python-linux-x64" -O hello-python
chmod +x hello-python
./hello-python
```

Запуск из исходников:

```shell
git clone https://github.com/h1z1qqe/hello-python.git
cd hello-python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Запуск тестов:

```shell
python -m pytest -v
```
