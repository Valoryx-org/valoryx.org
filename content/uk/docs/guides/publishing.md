---
title: Публікація документації
description: Опублікуйте документацію як гарний публічний сайт із підсвічуванням синтаксису, підтримкою SEO та опціональним доступом лише для команди.
weight: 5
---

# Публікація документації

DocPlatform може подавати вашу документацію як публічний вебсайт — із бічною навігацією, підсвічуванням синтаксису та SEO метаданими. Окремий генератор статичних сайтів не потрібен.

## Як працює публікація

Опублікована документація подається за адресою `/p/{workspace-slug}/{page-path}`:

```
http://localhost:3000/p/my-docs/              → docs/index.md
http://localhost:3000/p/my-docs/quickstart    → docs/quickstart.md
http://localhost:3000/p/my-docs/api/auth      → docs/api/auth.md
```

Сторінки рендеряться з Markdown в HTML при запиті за допомогою goldmark (сумісний із CommonMark) з підсвічуванням синтаксису Chroma для блоків коду.

### Життєвий цикл статусу сторінки

Сторінки мають поле `status`, що контролює їх видимість:

| Статус | У редакторі | На опублікованому сайті | У пошуку |
|---|---|---|---|
| `draft` (за замовчуванням) | Видимий | Прихований | Видимий лише для учасників |
| `published` | Видимий | Видимий | Видимий відповідно до правил доступу |
| `archived` | Видимий (затемнений) | Прихований | Прихований |

Встановіть статус у frontmatter:

```yaml
---
title: My Page
status: published    # draft, published, or archived
publish: true        # shorthand — equivalent to status: published
---
```

Скорочення `publish: true` та `status: published` еквівалентні. Використовуйте те, що вам більше подобається.

## Увімкнення публікації

### Для окремої сторінки

Встановіть `published: true` у frontmatter сторінки:

```yaml
---
title: API Authentication
description: How to authenticate with the API.
published: true
---
```

Або перемкніть перемикач **Published** у формі frontmatter веб-редактора.

### За замовчуванням на рівні робочого простору

Встановіть значення за замовчуванням на рівні робочого простору, щоб нові сторінки публікувалися автоматично:

```yaml
# .docplatform/config.yaml
publishing:
  default_published: true
  require_explicit_unpublish: false
```

## Функції опублікованого сайту

### Навігація

Опублікований сайт генерує бічну навігацію з вашої ієрархії сторінок. Порядок відповідає бічній панелі у веб-редакторі.

Щоб налаштувати порядок навігації, змініть секцію `navigation` у конфігурації робочого простору:

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

### Підсвічування синтаксису

Блоки коду підсвічуються за допомогою **Chroma** (goldmark-highlighting, тема Dracula). Підтримується понад 200 мов.

Вкажіть мову після відкриваючих потрійних зворотних лапок:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

### SEO

DocPlatform автоматично генерує SEO метадані з frontmatter сторінки:

| Тег | Джерело |
|---|---|
| `<title>` | Frontmatter `title` |
| `<meta name="description">` | Frontmatter `description` |
| `<meta property="og:title">` | Frontmatter `title` |
| `<meta property="og:description">` | Frontmatter `description` |
| `<link rel="canonical">` | Генерується зі шляху сторінки |
| `sitemap.xml` | Автоматично генерується з усіх опублікованих сторінок |
| `robots.txt` | Автоматично генерується |

### Контроль доступу

За замовчуванням опублікована документація є **публічною** — вхід не потрібен. Будь-хто з URL може переглядати її.

Щоб обмежити весь опублікований сайт лише для учасників робочого простору, встановіть `PUBLISH_REQUIRE_AUTH`:

```bash
# .env
PUBLISH_REQUIRE_AUTH=true
```

Коли увімкнено:

- Відвідувачі, що не увійшли, перенаправляються на `/#/login?next=<url>`
- Після входу вони повертаються на запитану сторінку
- Будь-який учасник робочого простору (будь-яка роль) може переглядати — навіть Viewer
- Неучасники, що входять, все одно перенаправляються

Перезапустіть сервер, щоб ця зміна набула чинності. Перебудова не потрібна.

> **Контроль доступу на рівні сторінки** (обмеження окремих сторінок для конкретних ролей) заплановано для майбутнього релізу. У v0.5 контроль доступу працює за принципом все-або-нічого на рівні сайту через `PUBLISH_REQUIRE_AUTH`.

## Вбудовані компоненти

Опублікована документація підтримує 7 користувацьких компонентів, які відображаються як багаті інтерактивні елементи:

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

**Типи:** `info`, `warning`, `danger`, `tip`, `note`

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

## Власний домен

Для подачі опублікованої документації на власному домені:

1. Встановіть змінну середовища `BASE_DOMAIN`:

```bash
export BASE_DOMAIN=docs.yourcompany.com
```

2. Налаштуйте DNS, щоб ваш домен вказував на сервер DocPlatform
3. Налаштуйте зворотний проксі (nginx, Caddy або хмарний балансувальник навантаження) із TLS термінацією

Приклад конфігурації Caddy:

```
docs.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy автоматично отримує та оновлює TLS сертифікати через Let's Encrypt.

## Кешування

Опубліковані сторінки кешуються для продуктивності:

| Заголовок | Значення | Опис |
|---|---|---|
| `Cache-Control` | `public, max-age=300` | Браузери та CDN кешують на 5 хвилин |
| `ETag` | Хеш контенту | Дозволяє умовні запити (304 Not Modified) |

Ключ кешу базується на хеші контенту сторінки. Коли контент змінюється, ETag автоматично змінюється та кешовані версії інвалідуються.

### Перезапис URL ресурсів

У веб-редакторі ресурси використовують відносні шляхи (`assets/screenshot.png`). В опублікованій документації вони автоматично переписуються на абсолютні шляхи (`/p/{slug}/assets/screenshot.png`), щоб зображення та файли завантажувалися правильно на будь-якій глибині URL.

## Попередній перегляд перед публікацією

Перед тим як зробити сторінку публічною, перегляньте її за опублікованою URL. Сторінки з `published: false` все ще доступні автентифікованим учасникам робочого простору за шляхом `/p/` — вони просто виключені з публічної навігації та sitemap.
