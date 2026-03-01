---
title: Публикация документации
description: Публикуйте документацию как красивый публичный сайт с подсветкой синтаксиса, поддержкой SEO и опциональным доступом только для команды.
weight: 5
---

# Публикация документации

DocPlatform может предоставлять документацию как публичный веб-сайт с боковой навигацией, подсветкой синтаксиса и SEO-метаданными. Отдельный генератор статических сайтов не требуется.

## Как работает публикация

Опубликованная документация доступна по адресу `/p/{workspace-slug}/{page-path}`:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Страницы рендерятся из Markdown в HTML по запросу с использованием goldmark (совместим с CommonMark) и подсветкой синтаксиса Chroma для блоков кода.

### Жизненный цикл статуса страницы

Страницы имеют поле `status`, управляющее их видимостью:

| Статус | В редакторе | На опубликованном сайте | В поиске |
|---|---|---|---|
| `draft` (по умолчанию) | Виден | Скрыт | Виден только участникам |
| `published` | Виден | Виден | Виден согласно правилам доступа |
| `archived` | Виден (затемнен) | Скрыт | Скрыт |

Установите статус в frontmatter:

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # shorthand — equivalent to status: published
---
```

Сокращение `publish: true` и `status: published` эквивалентны. Используйте то, что удобнее.

## Включение публикации

### Для отдельной страницы

Установите `published: true` в frontmatter страницы:

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

Или переключите тумблер **Published** в форме frontmatter веб-редактора.

### На уровне workspace

Установите значение по умолчанию на уровне workspace, чтобы новые страницы публиковались автоматически:

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Возможности опубликованного сайта

### Навигация

Опубликованный сайт генерирует боковую навигацию из иерархии страниц. Порядок соответствует боковой панели в веб-редакторе.

Для настройки порядка навигации отредактируйте секцию `navigation` в конфигурации workspace:

```yaml
# .docplatform/config.yaml
navigation:
  - title: "Getting Started"
    path: "getting-started/index.md"
    children:
      - title: "Installation"
        path: "getting-started/installation.md"
      - title: "Quickstart"
        path: "getting-started/quickstart.md"
```

### Подсветка синтаксиса

Блоки кода подсвечиваются с помощью **Chroma** (goldmark-highlighting, тема Dracula). Поддерживается более 200 языков.

Укажите язык после открывающих тройных обратных кавычек:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform автоматически генерирует SEO-метаданные из frontmatter страницы:

| Тег | Источник |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Генерируется из пути страницы |
| `sitemap.xml` | Автоматически из всех опубликованных страниц |
| `robots.txt` | Генерируется автоматически |

### Контроль доступа

По умолчанию опубликованная документация **публична** — вход не требуется. Любой, у кого есть URL, может просматривать ее.

Чтобы ограничить весь опубликованный сайт участниками workspace, установите `PUBLISH_REQUIRE_AUTH`:

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

При включении:

- Посетители, не вошедшие в систему, перенаправляются на `/#/login?next=<url>`
- После входа они возвращаются на запрошенную страницу
- Любой участник workspace (любая роль) может просматривать — даже Viewers
- Пользователи, не являющиеся участниками, при входе перенаправляются на страницу отказа

Перезапустите сервер для применения изменений. Повторная сборка не требуется.

> **Контроль доступа на уровне страницы** (ограничение отдельных страниц определенными ролями) запланирован на будущие версии. В v0.5 контроль доступа работает по принципу все-или-ничего на уровне сайта через `PUBLISH_REQUIRE_AUTH`.

## Встроенные компоненты

Опубликованная документация поддерживает 7 пользовательских компонентов, которые отображаются как интерактивные элементы:

### Callout

```markdown
:::callout{type="info"}
This is an informational callout.
:::

:::callout{type="warning"}
Be careful with this operation.
:::

:::callout{type="danger"}
This action is irreversible.
:::

:::callout{type="tip"}
Pro tip: use keyboard shortcuts for faster editing.
:::
```

**Типы:** `info`, `warning`, `danger`, `tip`, `note`

### Tabs

```markdown
:::tabs
::tab{label="npm"}
npm install docplatform
::
::tab{label="yarn"}
yarn add docplatform
::
::tab{label="pnpm"}
pnpm add docplatform
::
:::
```

### Accordion

```markdown
:::accordion{title="How does sync work?"}
DocPlatform uses a hybrid git engine that combines go-git for small repositories
with native git CLI for large ones. Changes are synced via polling or webhooks.
:::
```

### Cards

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="User Guide" link="/guides/editor"}
Learn the web editor, git sync, and publishing features.
::
:::
```

### Steps

```markdown
:::steps
::step{title="Install"}
Download the binary or pull the Docker image.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start"}
Run `docplatform serve` and open the browser.
::
:::
```

### API Block

```markdown
:::api{method="GET" path="/api/v1/pages/{id}"}
Retrieve a single page by ID.

**Parameters:**
- `id` (path, required) — Page ULID

**Response:** `200 OK`
```json
{
  "id": "01HJKL...",
  "title": "Getting Started",
  "content": "..."
}
```
:::
```

## Пользовательский домен

Для размещения опубликованной документации на собственном домене:

1. Установите переменную окружения `BASE_DOMAIN`:

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Настройте DNS для указания домена на сервер DocPlatform
3. Настройте reverse proxy (nginx, Caddy или облачный балансировщик нагрузки) с TLS-терминацией

Пример конфигурации Caddy:

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy автоматически получает и обновляет TLS-сертификаты через Let's Encrypt.

## Кэширование

Опубликованные страницы кэшируются для повышения производительности:

| Заголовок | Значение | Описание |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Браузеры и CDN кэшируют на 5 минут |
| `ETag` | Хеш контента | Включает условные запросы (304 Not Modified) |

Ключ кэша основан на хеше контента страницы. При изменении контента ETag изменяется автоматически, и кэшированные версии инвалидируются.

### Перезапись URL ресурсов

В веб-редакторе ресурсы используют относительные пути (`assets/screenshot.png`). В опубликованной документации они автоматически переписываются на абсолютные пути (`/p/{slug}/assets/screenshot.png`), чтобы изображения и файлы корректно загружались на любой глубине URL.

## Предпросмотр перед публикацией

Перед тем как сделать страницу публичной, просмотрите ее по URL публикации. Страницы с `published: false` по-прежнему доступны аутентифицированным участникам workspace по пути `/p/` — они просто исключены из публичной навигации и sitemap.
