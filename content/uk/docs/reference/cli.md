---
title: Довідник CLI
description: Повний довідник усіх команд CLI DocPlatform — serve, init, rebuild, doctor та version.
weight: 2
---

# Довідник CLI

DocPlatform надає 5 команд CLI для управління сервером, ініціалізації робочих просторів, діагностики та обслуговування.

## Глобальні опції

Ці опції застосовуються до всіх команд:

| Прапорець | Опис |
|---|---|
| `--help`, `-h` | Показати довідку для будь-якої команди |
| `--version`, `-v` | Показати інформацію про версію |

## `docplatform serve`

Запуск HTTP сервера.

```bash
docplatform serve [flags]
```

### Прапорці

| Прапорець | За замовчуванням | Опис |
|---|---|---|
| `--port` | `3000` | HTTP порт прослуховування (перевизначає змінну середовища `PORT`) |
| `--host` | `0.0.0.0` | HTTP адреса прослуховування (перевизначає змінну середовища `HOST`) |
| `--data-dir` | `.docplatform` | Шлях до директорії даних (перевизначає змінну середовища `DATA_DIR`) |

### Поведінка

- Завантажує змінні середовища з файлу `.env` (якщо існує)
- Ініціалізує базу даних SQLite з режимом WAL
- Виконує очікуючі міграції бази даних
- Завантажує політики прав Casbin у пам'ять
- Створює або відкриває пошуковий індекс Bleve
- Запускає git sync engine для всіх налаштованих робочих просторів
- Запускає планувальник резервного копіювання (якщо увімкнено)
- Подає веб-редактор та API на налаштованому порту

### Послідовність запуску

Коли запускається `docplatform serve`, відбувається наступне в порядку:

1. Завантаження конфігурації (змінні середовища + файл `.env` + значення за замовчуванням)
2. Відкриття бази даних SQLite (режим WAL) та виконання очікуючих міграцій
3. Створення організації за замовчуванням, якщо це перший запуск
4. Ініціалізація сервісів: Content Ledger, Git Engine (пул з 4 воркерів), Search Engine, Permission Service, Auth Service, WebSocket Hub
5. Запуск фонових goroutine: WebSocket hub, git sync polling, планувальник резервного копіювання, телеметрія (якщо увімкнена)
6. Початок прослуховування на налаштованому host:port

Запити на читання обслуговуються негайно. Якщо робочі простори мають наявний контент, реконсиляція виконується у фоновому режимі без блокування.

### Сигнали

| Сигнал | Ефект |
|---|---|
| `SIGTERM` | Коректне завершення — припинити прийом запитів, завершити поточні операції, скинути базу даних |
| `SIGINT` | Те саме, що SIGTERM (Ctrl+C) |

**Послідовність завершення** (дедлайн 15 секунд):

1. Скасування контексту додатка (сигналізує всім goroutine зупинитися)
2. Зупинка WebSocket hub (закриття всіх клієнтських з'єднань)
3. Зупинка git sync manager (завершення поточних операцій синхронізації)
4. Закриття пошукового рушія (скидання індексу Bleve на диск)
5. Очікування git worker pool (завершення поточних git операцій)
6. Зупинка HTTP сервера (10-секундний таймаут для поточних запитів)

Якщо завершення перевищує 15 секунд, процес завершується примусово.

### Приклад

```bash
# Start on default port
docplatform serve

# Start on custom port
docplatform serve --port 8080

# Start with explicit data directory
docplatform serve --data-dir /var/lib/docplatform
```

### Вивід

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

Ініціалізація нового робочого простору.

```bash
docplatform init [flags]
```

### Прапорці

| Прапорець | Обов'язковий | За замовчуванням | Опис |
|---|---|---|---|
| `--workspace-name` | Так | — | Відображувана назва робочого простору |
| `--slug` | Так | — | URL-безпечний ідентифікатор (використовується в URL опублікованої документації) |
| `--git-url` | Ні | — | URL віддаленого git репозиторію (SSH або HTTPS) |
| `--branch` | Ні | `main` | Git гілка для синхронізації |
| `--data-dir` | Ні | `.docplatform` | Шлях до директорії даних |

### Поведінка

1. Створює структуру директорії даних (`{DATA_DIR}/`)
2. Ініціалізує базу даних SQLite (якщо ще не існує)
3. Генерує ключ підпису RS256 JWT (якщо ще не існує)
4. Створює директорію робочого простору (`{DATA_DIR}/workspaces/{ulid}/`)
5. Якщо вказано `--git-url`, клонує репозиторій
6. Створює конфігураційний файл робочого простору
7. Індексує наявні `.md` файли

### Приклад

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

### Вивід

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

Перебудова бази даних та пошукового індексу з файлової системи. Використовуйте, коли база даних не синхронізована з реальними файлами на диску.

```bash
docplatform rebuild [flags]
```

### Прапорці

| Прапорець | Обов'язковий | За замовчуванням | Опис |
|---|---|---|---|
| `--workspace-id` | Ні | усі | ULID конкретного робочого простору для перебудови. Без цього прапорця перебудовуються всі робочі простори. |
| `--search` | Ні | `false` | Також видалити та перебудувати пошуковий індекс Bleve |
| `--data-dir` | Ні | `.docplatform` | Шлях до директорії даних |

### Поведінка

1. Створює резервну копію поточної бази даних
2. Видаляє таблицю `pages`
3. Сканує файлову систему на предмет усіх `.md` файлів у директоріях `docs/` робочих просторів
4. Аналізує frontmatter та контент кожного файлу
5. Вставляє записи сторінок у базу даних
6. Перебудовує пошуковий індекс Bleve
7. Звітує про результати реконсиляції

### Коли використовувати

- Після ручного додавання, переміщення або видалення `.md` файлів поза DocPlatform
- Після аварії, що могла залишити базу даних неузгодженою
- Після відновлення файлів із резервної копії git
- Коли `docplatform doctor` повідомляє про невідповідності FS/DB

### Приклад

```bash
# Rebuild all workspaces
docplatform rebuild

# Rebuild a specific workspace
docplatform rebuild --workspace-id 01KJJ10NTF31Z1QJTG4ZRQZ2Z2
```

### Вивід

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

**Відновлення «привидів»:** Коли знаходяться осиротілі записи бази даних (немає відповідного файлу), DocPlatform намагається зіставити їх з неіндексованими файлами за хешем контенту. Це відновлює сторінки, що були переміщені або перейменовані поза DocPlatform.

---

## `docplatform doctor`

Виконання 9 діагностичних перевірок стану платформи.

```bash
docplatform doctor [flags]
```

### Прапорці

| Прапорець | Обов'язковий | За замовчуванням | Опис |
|---|---|---|---|
| `--bundle` | Ні | `false` | Створити ZIP файл із діагностичним виводом для підтримки |
| `--data-dir` | Ні | `.docplatform` | Шлях до директорії даних |

### Перевірки

| # | Перевірка | Опис |
|---|---|---|
| 1 | **З'єднання з базою даних** | Файл SQLite існує, доступний для читання, режим WAL увімкнено |
| 2 | **Версія схеми** | Міграції актуальні |
| 3 | **Узгодженість FS/DB** | Кожен файл у `docs/` має запис у базі даних, і навпаки |
| 4 | **Осиротілі файли** | Файли на диску без запису в базі даних |
| 5 | **Осиротілі записи** | Записи бази даних без файлу на диску |
| 6 | **Стан пошукового індексу** | Кількість документів в індексі Bleve збігається з кількістю сторінок |
| 7 | **Биті внутрішні посилання** | Markdown посилання на неіснуючі сторінки |
| 8 | **Валідність frontmatter** | Усі сторінки мають коректний YAML frontmatter із назвою |
| 9 | **Підключення до git remote** | Якщо git налаштовано, чи доступний віддалений сервер? |

### Коди виходу

| Код | Значення |
|---|---|
| `0` | Усі перевірки пройдено (стан нормальний) |
| `1` | Одна або більше перевірок не пройдені або мають попередження |

Використовуйте код виходу в скриптах та моніторингу:

```bash
docplatform doctor || echo "Health check failed"
```

### Приклад

```bash
docplatform doctor
```

### Вивід

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

Bundle зберігається за адресою `{DATA_DIR}/diagnostics/docplatform-diagnostics-{timestamp}.zip` та містить:

- `report.json` — структуровані результати діагностики
- Інформація про схему (визначення таблиць, без даних рядків)
- Список файлів (шляхи та розміри, без контенту)
- Інформація про систему (ОС, архітектура, версія Go)
- Останні 1 000 рядків логів помилок
- Версія сервера та конфігурація (з прихованими секретами)

Bundle **ніколи** не містить контент сторінок, паролі, токени або приватні ключі.

---

## `docplatform version`

Виведення версії, хешу коміту та дати збірки.

```bash
docplatform version
```

### Вивід

```
docplatform v0.5.2 (commit: abc1234, built: 2026-03-08T10:00:00Z)
```

Інформація про версію вбудовується під час збірки через прапорці лінкера. Корисно для перевірки розгорнутого релізу та запитів до підтримки.
