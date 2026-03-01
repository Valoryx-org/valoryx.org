---
title: Markdown та компоненти
description: Пишіть документацію з CommonMark Markdown, YAML frontmatter та 7 вбудованими інтерактивними компонентами.
weight: 2
---

# Markdown та компоненти

DocPlatform використовує Markdown, сумісний із CommonMark, з YAML frontmatter та 7 користувацькими компонентами для багатої інтерактивної документації.

## Основи Markdown

DocPlatform підтримує повну специфікацію CommonMark плюс поширені розширення.

### Заголовки

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Заголовки автоматично генерують anchor ID для глибоких посилань: `## My Section` → `#my-section`.

### Форматування тексту

```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
`Inline code`
[Link text](https://example.com)
![Image alt text](./assets/screenshot.png)
```

### Списки

```markdown
- Unordered item
- Another item
  - Nested item

1. Ordered item
2. Another item

- [ ] Task item (unchecked)
- [x] Task item (checked)
```

### Цитати

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Блоки коду

Огороджені блоки коду з підсвічуванням синтаксису для конкретної мови (200+ мов через Shiki):

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Таблиці

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Таблиці підтримують вирівнювання ліворуч, по центру та праворуч:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Горизонтальні лінії

```markdown
---
```

### Посилання між сторінками

Посилайтеся на інші сторінки у вашому робочому просторі за допомогою відносних шляхів:

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform перевіряє внутрішні посилання. Команда `doctor` повідомляє про будь-які биті посилання.

## Frontmatter

Кожна сторінка починається з блоку YAML frontmatter, обмеженого `---`:

```yaml
---
title: Page Title
description: A brief summary for search results and SEO.
tags: [guide, getting-started]
published: true
access: public
allowed_roles: []
---
```

### Поля frontmatter

| Поле | Тип | Обов'язкове | За замовчуванням | Опис |
|---|---|---|---|---|
| `title` | string | Так | — | Назва сторінки, що відображається в навігації та заголовках |
| `description` | string | Ні | — | Короткий опис для результатів пошуку, SEO мета-тегів |
| `tags` | string[] | Ні | `[]` | Категорії для фільтрації та пошуку |
| `published` | boolean | Ні | `false` | Включення в опублікований документаційний сайт |
| `access` | string | Ні | `public` | Видимість: `public`, `workspace`, `restricted` |
| `allowed_roles` | string[] | Ні | `[]` | Ролі з правом перегляду (коли `access: restricted`) |

## Користувацькі компоненти

DocPlatform включає 7 вбудованих компонентів, які відображаються як багаті інтерактивні елементи як у попередньому перегляді веб-редактора, так і в опублікованій документації.

Компоненти використовують синтаксис директив:

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Виділяйте важливу інформацію стилізованими блоками.

```markdown
:::callout{type="info"}
DocPlatform automatically indexes all content for search.
:::

:::callout{type="warning"}
Changing the workspace slug will break existing published URLs.
:::

:::callout{type="danger"}
Running `rebuild` drops the pages table and re-indexes from the filesystem.
This is irreversible.
:::

:::callout{type="tip"}
Press Cmd+K to open search from anywhere in the editor.
:::

:::callout{type="note"}
This feature is available in Community Edition.
:::
```

**Доступні типи:** `info`, `warning`, `danger`, `tip`, `note`

### Блок коду (розширений)

Стандартні огороджені блоки коду автоматично доповнюються:

- **Підсвічування синтаксису** — 200+ мов через Shiki
- **Кнопка копіювання** — копіювання в буфер обміну одним кліком
- **Мітка мови** — відображається у верхньому правому куті
- **Номери рядків** — опціонально, вмикаються через `showLineNumbers`

````markdown
```typescript {showLineNumbers}
interface Page {
  id: string;
  title: string;
  content: string;
  published: boolean;
}
```
````

### Tabs

Групуйте пов'язаний контент у перемикальні панелі вкладок.

```markdown
:::tabs
::tab{label="macOS"}
```bash
brew install docplatform
```
::
::tab{label="Linux"}
```bash
curl -fsSL https://valoryx.org/install.sh | sh
```
::
::tab{label="Docker"}
```bash
docker pull ghcr.io/valoryx-org/docplatform:latest
```
::
:::
```

Вибір вкладки зберігається під час навігації між сторінками — якщо користувач обрав "Docker", усі групи вкладок на наступних сторінках за замовчуванням показують "Docker", коли така мітка існує.

### Accordion

Згортувані секції для додаткового контенту.

```markdown
:::accordion{title="What happens during initialization?"}
The `init` command creates a `.docplatform` directory, initializes the SQLite
database, generates an RS256 signing key, and optionally clones a git repository.
:::

:::accordion{title="Can I use an existing database?"}
No. DocPlatform manages its own SQLite database and does not support connecting
to external database servers in Community Edition.
:::
```

### Cards

Сітка карток із посиланнями для навігаційних сторінок або оглядів функцій.

```markdown
:::cards
::card{title="Getting Started" link="/getting-started"}
Install and configure DocPlatform in under 10 minutes.
::
::card{title="Git Integration" link="/guides/git-integration"}
Bidirectional sync between the web editor and your git repository.
::
::card{title="Publishing" link="/guides/publishing"}
Publish beautiful documentation sites with dark mode and SEO.
::
::card{title="Search" link="/guides/search"}
Instant full-text search with permission filtering.
::
:::
```

### Steps

Нумеровані покрокові інструкції з візуальними індикаторами прогресу.

```markdown
:::steps
::step{title="Download"}
Get the latest binary from GitHub Releases.
::
::step{title="Initialize"}
Run `docplatform init` to create your workspace.
::
::step{title="Start the server"}
Run `docplatform serve` and open http://localhost:3000.
::
::step{title="Register"}
Create your admin account — the first user becomes SuperAdmin.
::
:::
```

### API Block

Документуйте API ендпоінти з бейджами методів, параметрами та прикладами відповідей.

```markdown
:::api{method="POST" path="/api/v1/auth/login"}
Authenticate a user and receive JWT tokens.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` — Invalid credentials
- `429 Too Many Requests` — Rate limit exceeded
:::
```

## Використання компонентів у редакторі

### Режим форматованого тексту

У багатофункціональному редакторі компоненти відображаються як інтерактивні блоки. Вставляйте їх за допомогою:

- **Слеш-команди** — введіть `/`, потім назву компонента (наприклад, `/callout`, `/tabs`)
- **Панель інструментів** — натисніть кнопку **+** → оберіть компонент
- **Клавіатура** — немає виділених ярликів (використовуйте слеш-команди)

### Режим необробленого Markdown

У режимі необробленого тексту записуйте синтаксис директив безпосередньо. Редактор забезпечує підсвічування синтаксису для блоків компонентів.

## Розширення Markdown

Окрім CommonMark, DocPlatform підтримує:

| Розширення | Синтаксис | Опис |
|---|---|---|
| **Списки завдань** | `- [ ] item` | Інтерактивні прапорці |
| **Закреслення** | `~~text~~` | Закреслений текст |
| **Таблиці** | Таблиці GFM | З підтримкою вирівнювання |
| **Автопосилання** | `https://...` | URL автоматично стають посиланнями |
| **Виноски** | `[^1]` | Виноски у стилі посилань |
| **Anchor заголовків** | Автоматична генерація | Глибокі посилання на розділи |
