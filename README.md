# Практическое задание 1. Анализатор журналов событий

## Цель и бизнес-требования

CLI-приложение для построчного анализа больших журналов нескольких компонентов службы поддержки. Приложение должно фильтровать события, считать статистику и формировать JSON/CSV-отчёт, не загружая весь журнал в память.

## Формат входа

Одна запись имеет формат `timestamp | level | source | eventCode | message`. Временная метка должна быть ISO 8601 UTC с суффиксом `Z`; допустимые уровни: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`. Поля не должны быть пустыми, разделитель `|` внутри полей не поддерживается. Повреждённые записи пропускаются, а номер строки и причина выводятся в stderr и попадают в отчёт.

## Структура проекта

- `log_analyzer/parser.py` — разбор и проверка записи.
- `log_analyzer/filters.py` — временные, уровневые и source-фильтры.
- `log_analyzer/aggregate.py` — потоковая агрегация.
- `log_analyzer/output.py` — вывод в терминал, JSON и CSV.
- `log_analyzer/cli.py` — аргументы CLI и потоковое чтение.
- `tests/` — автоматические тесты.
- `logs_events_sample.log` — входной пример.
- `reports/tests.html` — HTML-отчёт тестирования.
- `reports/coverage/index.html` — HTML-отчёт покрытия.

## Развёртывание

В WSL/Ubuntu из корневой папки проекта выполните:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
```

## Запуск

Минимальный запуск:

```bash
python3 -m log_analyzer --input logs_events_sample.log
```

Фильтр по уровню и источнику, JSON-отчёт:

```bash
python3 -m log_analyzer --input logs_events_sample.log --level ERROR --source gateway --top 5 --format json --output reports/errors.json
```

Интервал времени (начало включительно, конец исключительно):

```bash
python3 -m log_analyzer --input logs_events_sample.log --from 2026-09-01T00:00:00Z --to 2026-09-03T00:00:00Z --format csv --output reports/period.csv
```

Сочетание нескольких фильтров:

```bash
python3 -m log_analyzer --input logs_events_sample.log --from 2026-09-04T00:00:00Z --to 2026-09-08T00:00:00Z --level ERROR --level WARN --source orders-api --source payment-worker --top 10 --format json --output reports/filtered.json
```

CLI-параметры: `--input`, `--from`, `--to`, `--level` (можно повторять), `--source` (можно повторять), `--top`, `--format json|csv`, `--output`.

## Тестирование и покрытие

Одна команда запускает тесты, создаёт HTML-отчёт тестов и HTML-отчёт покрытия:

```bash
./run_tests.sh
```

- Отчёт тестов: `reports/tests.html`.
- Отчёт покрытия: `reports/coverage/index.html`.
- Метрика: line coverage и branch coverage через `pytest-cov`/Coverage.py.
- Целевое требование задания: не менее 80% покрытия исполняемого кода. Фактический процент указывается по результату запуска команды; его нельзя считать подтверждённым до выполнения тестов в целевой среде.

Тесты проверяют корректные и повреждённые записи, дату и уровень, пустые поля, пустой и отсутствующий файл, границы интервала, комбинированные фильтры, top-N, JSON/CSV и сообщения о номерах строк.

## Ограничения

Приложение обрабатывает входной файл построчно и не хранит список всех событий. В памяти остаются только счётчики и сообщения об ошибочных строках, необходимые для отчёта.
