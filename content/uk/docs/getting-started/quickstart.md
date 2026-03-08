---
title: Швидкий старт
description: Запустіть DocPlatform менш ніж за 5 хвилин із повнофункціональним робочим простором документації.
weight: 1
---

# Швидкий старт

Від нуля до працюючої документаційної платформи менш ніж за 5 хвилин. Цей посібник охоплює найшвидший шлях — для детальних варіантів див. посібник [Встановлення](installation.md).

## Крок 1: Встановлення

```bash
# Recommended (auto-detects platform)
curl -fsSL https://valoryx.org/install.sh | sh
```

Або завантажте вручну:

```bash
curl -sLO https://github.com/Valoryx-org/releases/releases/latest/download/docplatform-linux-amd64
chmod +x docplatform-linux-amd64
sudo mv docplatform-linux-amd64 /usr/local/bin/docplatform
```

Або з Docker:

```bash
docker run -d --name docplatform -p 3000:3000 -v docplatform-data:/data ghcr.io/valoryx-org/docplatform:latest
```

Якщо використовуєте Docker, перейдіть до [Кроку 3](#крок-3-зареєструйте-обліковий-запис) — контейнер ініціалізується автоматично.

## Крок 2: Ініціалізація робочого простору

```bash
docplatform init --workspace-name "My Docs" --slug my-docs
```

Це створює:

```
.docplatform/
├── data.db              # SQLite database
├── jwt-key.pem          # Auto-generated RS256 signing key
└── workspaces/
    └── {workspace-id}/
        ├── docs/        # Your documentation lives here
        └── .docplatform/
            └── config.yaml
```

### З git (опціонально)

Підключіться до наявного git репозиторію під час ініціалізації:

```bash
docplatform init \
  --workspace-name "My Docs" \
  --slug my-docs \
  --git-url git@github.com:your-org/docs.git \
  --branch main
```

DocPlatform клонує репозиторій та починає синхронізацію. Усі наявні `.md` файли автоматично індексуються.

## Крок 3: Запуск сервера

```bash
docplatform serve
```

```
INFO  Server starting            port=3000 version=v0.5.2
INFO  Database initialized       path=.docplatform/data.db
INFO  Search index ready         documents=0
INFO  Workspace loaded           name="My Docs" slug=my-docs
INFO  Listening on               http://localhost:3000
```

Відкрийте [http://localhost:3000](http://localhost:3000) у браузері.

## Крок 4: Зареєструйте обліковий запис

Перший зареєстрований користувач автоматично стає **SuperAdmin** із повним доступом до платформи.

1. Натисніть **Create Account**
2. Введіть ім'я, електронну пошту та пароль
3. Ви увійшли в систему та готові писати

> **Примітка безпеки:** Механізм «перший користувач стає адміністратором» діє лише коли жодного користувача не існує. Після першої реєстрації нові облікові записи отримують роль за замовчуванням, налаштовану для робочого простору.

## Крок 5: Створіть першу сторінку

1. Натисніть **New Page** на бічній панелі
2. Дайте їй назву — URL slug генерується автоматично з назви
3. Почніть писати в багатофункціональному редакторі
4. Зміни автоматично зберігаються кожні кілька секунд

Сторінка зберігається як Markdown файл у директорії `docs/` вашого робочого простору. Якщо ви підключили git, вона автоматично фіксується та відправляється.

## Крок 6: Спробуйте

Ось кілька речей, які варто спробувати одразу:

| Дія | Як |
|---|---|
| **Перемкнутися на необроблений Markdown** | Натисніть перемикач `</>` на панелі інструментів редактора |
| **Пошук** | Натисніть `Cmd+K` (або `Ctrl+K`), щоб відкрити миттєвий пошук |
| **Створити підсторінку** | Натисніть `+` поруч з наявною сторінкою на бічній панелі |
| **Переглянути опублікований сайт** | Перейдіть до `http://localhost:3000/p/my-docs/` |
| **Запустити діагностику** | Виконайте `docplatform doctor` у терміналі |

## Що далі

| Мета | Посібник |
|---|---|
| Підключити git репозиторій | [Інтеграція з Git](../guides/git-integration.md) |
| Запросити команду | [Команди та співпраця](../guides/collaboration.md) |
| Опублікувати документацію публічно | [Публікація](../guides/publishing.md) |
| Розгорнути у виробництво | [Розгортання](../deployment/binary.md) |
| Налаштувати провайдерів автентифікації | [Автентифікація](../configuration/authentication.md) |
