---
title: Справочник CLI
description: Полный справочник всех команд CLI DocPlatform — serve, init, rebuild, doctor и version.
weight: 2
---

# Справочник CLI

DocPlatform предоставляет 5 команд CLI для управления сервером, инициализации workspace, диагностики и обслуживания.

## Глобальные параметры

Эти параметры применяются ко всем командам:

| Флаг | Описание |
|---|---|
| `--help`, `-h` | Показать справку для любой команды |
| `--version`, `-v` | Вывести информацию о версии |

## `docplatform serve`

Запуск HTTP-сервера.

```bash
docplatform serve [flags]
```

### Флаги

| Флаг | По умолчанию | Описание |
|---|---|---|
| `--port` | `3000` | Порт HTTP-сервера (переопределяет переменную окружения `PORT`) |
| `--host` | `0.0.0.0` | Адрес HTTP-сервера (переопределяет переменную окружения `HOST`) |
| `--data-dir` | `.docplatform` | Путь к директории данных (переопределяет переменную окружения `DATA_DIR`) |

### Поведение

- Загружает переменные окружения из файла `.env` (если присутствует)
- Инициализирует базу данных SQLite в режиме WAL
- Выполняет ожидающие миграции базы данных
- Загружает политики прав Casbin в память
- Создает или открывает поисковый индекс Bleve
- Запускает git sync engine для всех настроенных workspaces
- Запускает планировщик резервного копирования (если включен)
- Обслуживает веб-редактор и API на настроенном порту

### Последовательность запуска

При запуске `docplatform serve` происходит следующее по порядку:

1. Загрузка конфигурации (переменные окружения + файл `.env` + значения по умолчанию)
2. Открытие базы данных SQLite (режим WAL) и выполнение ожидающих миграций
3. Инициализация организации по умолчанию при первом запуске
4. Инициализация сервисов: Content Ledger, Git Engine (пул из 4 воркеров), Search Engine, Permission Service, Auth Service, WebSocket Hub
5. Запуск фоновых goroutine: WebSocket hub, git sync polling, планировщик резервного копирования, телеметрия (если включена)
6. Начало прослушивания на настроенном host:port

Запросы на чтение обслуживаются немедленно. Если workspaces содержат существующий контент, реконсиляция выполняется в фоне без блокировки.

### Сигналы

| Сигнал | Эффект |
|---|---|
| `SIGTERM` | Корректное завершение — прекращение приема запросов, завершение текущих операций, запись базы данных |
| `SIGINT` | То же, что SIGTERM (Ctrl+C) |

**Последовательность завершения** (дедлайн 15 секунд):

1. Отмена контекста приложения (сигнал всем goroutine о завершении)
2. Остановка WebSocket hub (закрытие всех клиентских соединений)
3. Остановка менеджера синхронизации git (завершение текущих операций)
4. Закрытие поискового движка (запись индекса Bleve на диск)
5. Опустошение пула git-воркеров (ожидание текущих git-операций)
6. Завершение HTTP-сервера (тайм-аут 10 секунд для текущих запросов)

Если завершение превышает 15 секунд, процесс завершается принудительно.

### Пример

```bash
# Start on default port
docplatform serve

# Start on custom port
docplatform serve --port 8080

# Start with explicit data directory
docplatform serve --data-dir /var/lib/docplatform
```

### Вывод

```
INFO  Server starting            port=3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db wal=true
INFO  Migrations applied         count=1
INFO  Search index ready         documents=42
INFO  Workspace loaded           name="Docs" slug=docs git_remote=git@github.com:...
INFO  Backup scheduler started   retention_days=7
INFO  Listening on               http://0.0.0.0:3000
```

---

## `docplatform init`

Инициализация нового workspace.

```bash
docplatform init [flags]
```

### Флаги

| Флаг | Обязательно | По умолчанию | Описание |
|---|---|---|---|
| `--workspace-name` | Да | — | Отображаемое имя workspace |
| `--slug` | Да | — | URL-безопасный идентификатор (используется в URL опубликованной документации) |
| `--git-url` | Нет | — | URL удаленного git-репозитория (SSH или HTTPS) |
| `--branch` | Нет | `main` | Ветка git для синхронизации |
| `--data-dir` | Нет | `.docplatform` | Путь к директории данных |

### Поведение

1. Создание структуры директории данных (`{DATA_DIR}/`)
2. Инициализация базы данных SQLite (если еще не существует)
3. Генерация ключа подписи JWT RS256 (если еще не существует)
4. Создание директории workspace (`{DATA_DIR}/workspaces/{ulid}/`)
5. Если указан `--git-url`, клонирование репозитория
6. Создание файла конфигурации workspace
7. Индексация существующих файлов `.md`

### Пример

```bash
# Local workspace (no git)
docplatform init \
  --workspace-name "Internal Wiki" \
  --slug wiki

# With git
docplatform init \
  --workspace-name "API Docs" \
  --slug api-docs \
  --git-url git@github.com:your-org/api-docs.git \
  --branch main
```

### Вывод

```
INFO  Data directory created     path=.docplatform
INFO  Database initialized       path=.docplatform/data.db
INFO  JWT key generated          path=.docplatform/jwt-key.pem
INFO  Workspace created          id=01KJJ10NTF... name="API Docs" slug=api-docs
INFO  Repository cloned          url=git@github.com:your-org/api-docs.git branch=main
INFO  Pages indexed              count=15
INFO  Ready. Run 'docplatform serve' to start.
```

---

## `docplatform rebuild`

Перестроение базы данных и поискового индекса из файловой системы. Используйте, когда база данных рассинхронизировалась с фактическими файлами на диске.

```bash
docplatform rebuild [flags]
```

### Флаги

| Флаг | Обязательно | По умолчанию | Описание |
|---|---|---|---|
| `--workspace-id` | Нет | все | ULID конкретного workspace для перестроения. Без этого флага перестраиваются все workspaces. |
| `--search` | Нет | `false` | Также удалить и перестроить поисковый индекс Bleve |
| `--data-dir` | Нет | `.docplatform` | Путь к директории данных |

### Поведение

1. Создание резервной копии текущей базы данных
2. Удаление таблицы `pages`
3. Сканирование файловой системы на наличие всех файлов `.md` в директориях `docs/` workspaces
4. Парсинг frontmatter и контента каждого файла
5. Вставка записей страниц в базу данных
6. Перестроение поискового индекса Bleve
7. Отчет о результатах реконсиляции

### Когда использовать

- После ручного добавления, перемещения или удаления файлов `.md` вне DocPlatform
- После сбоя, который мог оставить базу данных в несогласованном состоянии
- После восстановления файлов из git-бэкапа
- Когда `docplatform doctor` сообщает о несоответствиях FS/DB

### Пример

```bash
# Rebuild all workspaces
docplatform rebuild

# Rebuild a specific workspace
docplatform rebuild --workspace-id 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Вывод

```
INFO  Backup created             path=.docplatform/backups/pre-rebuild-20250115.db
INFO  Rebuilding workspace       id=01KJJ10NTF... name="API Docs"
INFO  Scanning filesystem        path=.docplatform/workspaces/01KJJ.../docs/
INFO  Pages found                count=42
INFO  Database rebuilt            inserted=42 updated=0 orphaned=3
INFO  Search index rebuilt        documents=42
INFO  Ghost recovery             matched=2 unmatched=1
INFO  Rebuild complete
```

**Ghost recovery:** Когда обнаруживаются осиротевшие записи базы данных (нет соответствующего файла), DocPlatform пытается сопоставить их с неиндексированными файлами по хешу контента. Это восстанавливает страницы, которые были перемещены или переименованы вне DocPlatform.

---

## `docplatform doctor`

Запуск 9 диагностических проверок состояния платформы.

```bash
docplatform doctor [flags]
```

### Флаги

| Флаг | Обязательно | По умолчанию | Описание |
|---|---|---|---|
| `--bundle` | Нет | `false` | Создать ZIP-файл с результатами диагностики для поддержки |
| `--data-dir` | Нет | `.docplatform` | Путь к директории данных |

### Проверки

| # | Проверка | Описание |
|---|---|---|
| 1 | **Подключение к базе данных** | Файл SQLite существует, доступен для чтения, режим WAL включен |
| 2 | **Версия схемы** | Миграции актуальны |
| 3 | **Консистентность FS/DB** | Каждый файл в `docs/` имеет запись в базе данных, и наоборот |
| 4 | **Осиротевшие файлы** | Файлы на диске без записи в базе данных |
| 5 | **Осиротевшие записи** | Записи в базе данных без файла на диске |
| 6 | **Состояние поискового индекса** | Количество документов в индексе Bleve совпадает с количеством страниц |
| 7 | **Битые внутренние ссылки** | Markdown-ссылки на несуществующие страницы |
| 8 | **Валидность frontmatter** | Все страницы имеют корректный YAML frontmatter с заголовком |
| 9 | **Связь с git remote** | Если git настроен, доступен ли удаленный репозиторий? |

### Коды завершения

| Код | Значение |
|---|---|
| `0` | Все проверки пройдены (здоров) |
| `1` | Одна или более проверок не пройдены или имеют предупреждения |

Используйте код завершения в скриптах и мониторинге:

```bash
docplatform doctor || echo "Health check failed"
```

### Пример

```bash
docplatform doctor
```

### Вывод

```
DocPlatform Health Check
========================

✓ Database connection          OK (WAL mode, 42 pages, 3 users)
✓ Schema version               OK (v1, up to date)
✓ FS/DB consistency            OK (42 files, 42 records)
✓ Orphaned files               OK (0 found)
✓ Orphaned records             OK (0 found)
✓ Search index health          OK (42 indexed, 42 expected)
⚠ Broken internal links        WARNING (2 broken links found)
  → guides/editor.md:15 → "old-page.md" (file not found)
  → api/endpoints.md:42 → "deprecated.md" (file not found)
✓ Frontmatter validity         OK (42/42 valid)
✓ Git remote connectivity      OK (git@github.com:your-org/docs.git)

Result: 8/9 passed, 1 warning
```

### Режим bundle

```bash
docplatform doctor --bundle
# Creates: docplatform-doctor-20250115.zip
```

Bundle сохраняется в `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` и содержит:

- `report.json` — структурированные результаты диагностики
- Информация о схеме (определения таблиц, без данных строк)
- Список файлов (пути и размеры, без контента)
- Информация о системе (ОС, архитектура, версия Go)
- Последние 1 000 строк журнала ошибок
- Версия сервера и конфигурация (с замаскированными секретами)

Bundle **никогда** не включает контент страниц, пароли, токены или приватные ключи.

---

## `docplatform version`

Вывод версии, хеша коммита и даты сборки.

```bash
docplatform version
```

### Вывод

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

Информация о версии встраивается во время сборки через флаги линковщика. Полезна для проверки развернутого релиза и обращений в поддержку.
