---
title: Markdown и компоненты
description: Создание документации с помощью CommonMark Markdown, YAML frontmatter и 7 встроенных интерактивных компонентов.
weight: 2
---

# Markdown и компоненты

DocPlatform использует Markdown, совместимый со стандартом CommonMark, с YAML frontmatter и 7 пользовательскими компонентами для создания функциональной интерактивной документации.

## Основы Markdown

DocPlatform поддерживает полную спецификацию CommonMark и распространенные расширения.

### Заголовки

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
```

Заголовки автоматически генерируют якорные идентификаторы для глубоких ссылок: `## My Section` -> `#my-section`.

### Форматирование текста

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

### Цитаты

```markdown
> This is a blockquote.
>
> It can span multiple paragraphs.
```

### Блоки кода

Огражденные блоки кода с подсветкой синтаксиса для конкретных языков (200+ языков через Shiki):

````markdown
```go
func main() {
    fmt.Println("Hello, DocPlatform!")
}
```
````

### Таблицы

```markdown
| Feature | Status | Notes |
|---|---|---|
| Editor | Complete | Tiptap-based |
| Search | Complete | Bleve engine |
| Git sync | Complete | Bidirectional |
```

Таблицы поддерживают выравнивание по левому краю, по центру и по правому краю:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
```

### Горизонтальные линии

```markdown
---
```

### Ссылки между страницами

Ссылайтесь на другие страницы workspace с помощью относительных путей:

```markdown
See the [Installation guide](../getting-started/installation.md).
Check the [API reference](../reference/api.md) for endpoint details.
```

DocPlatform проверяет внутренние ссылки. Команда `doctor` сообщает о битых ссылках.

## Frontmatter

Каждая страница начинается с блока YAML frontmatter, ограниченного `---`:

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

| Поле | Тип | Обязательно | По умолчанию | Описание |
|---|---|---|---|---|
| `title` | string | Да | — | Заголовок страницы в навигации и заголовках |
| `description` | string | Нет | — | Краткое описание для результатов поиска, SEO-метатегов |
| `tags` | string[] | Нет | `[]` | Категории для фильтрации и поиска |
| `published` | boolean | Нет | `false` | Включить в опубликованный сайт документации |
| `access` | string | Нет | `public` | Видимость: `public`, `workspace`, `restricted` |
| `allowed_roles` | string[] | Нет | `[]` | Роли с доступом (когда `access: restricted`) |

## Пользовательские компоненты

DocPlatform включает 7 встроенных компонентов, которые отображаются как интерактивные элементы в предпросмотре веб-редактора и опубликованной документации.

Компоненты используют синтаксис директив:

```
:::component-name{attributes}
Content goes here.
:::
```

### Callout

Выделяйте важную информацию с помощью стилизованных блоков-подсказок.

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

**Доступные типы:** `info`, `warning`, `danger`, `tip`, `note`

### Блок кода (расширенный)

Стандартные огражденные блоки кода автоматически дополняются:

- **Подсветка синтаксиса** — 200+ языков через Shiki
- **Кнопка копирования** — копирование в буфер обмена одним нажатием
- **Метка языка** — отображается в правом верхнем углу
- **Номера строк** — опционально, включаются с `showLineNumbers`

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

Группируйте связанный контент в переключаемые вкладки.

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

Выбор вкладки сохраняется при навигации между страницами — если пользователь выбрал "Docker", все группы вкладок на последующих страницах по умолчанию переключаются на "Docker", если такая метка существует.

### Accordion

Сворачиваемые секции для дополнительного контента.

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

Сетка карточек со ссылками для навигационных страниц или обзоров функций.

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

Пронумерованные пошаговые инструкции с визуальными индикаторами прогресса.

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

Документируйте API endpoints с метками методов, параметрами и примерами ответов.

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

## Использование компонентов в редакторе

### Режим форматированного текста

В режиме форматированного текста компоненты отображаются как интерактивные блоки. Вставляйте их с помощью:

- **Slash-команды** — введите `/`, затем имя компонента (например, `/callout`, `/tabs`)
- **Панель инструментов** — нажмите кнопку **+** -> выберите компонент
- **Клавиатура** — выделенных сочетаний нет (используйте slash-команды)

### Режим raw Markdown

В режиме raw пишите синтаксис директив напрямую. Редактор обеспечивает подсветку синтаксиса для блоков компонентов.

## Расширения Markdown

Помимо CommonMark, DocPlatform поддерживает:

| Расширение | Синтаксис | Описание |
|---|---|---|
| **Списки задач** | `- [ ] item` | Интерактивные чекбоксы |
| **Зачеркивание** | `~~text~~` | Зачеркнутый текст |
| **Таблицы** | Таблицы GFM | С поддержкой выравнивания |
| **Автоссылки** | `https://...` | URL автоматически становятся ссылками |
| **Сноски** | `[^1]` | Сноски в стиле ссылок |
| **Якоря заголовков** | Генерируются автоматически | Глубокие ссылки на разделы |
