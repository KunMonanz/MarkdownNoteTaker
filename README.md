# Notes API

A small Django REST Framework module providing note storage, grammar checking, and Markdown rendering endpoints.

## Requirements

- Django + Django REST Framework
- `django.core.cache` configured (e.g. Redis, Memcached, or local-memory cache)
- [`language_tool_python`](https://pypi.org/project/language-tool-python/) — wraps LanguageTool for grammar checking (requires Java, or downloads/runs a local LanguageTool server on first use)
- [`markdown`](https://pypi.org/project/Markdown/) — converts Markdown text to HTML

```bash
pip install language-tool-python markdown
```

> `language_tool_python` needs a Java runtime installed on the host unless you point it at a remote LanguageTool server (`language_tool_python.LanguageToolPublicAPI` or a self-hosted instance).

## Endpoints

### `NoteListCreateView`

`GET/POST /notes/`

Lists and creates notes belonging to the authenticated user.

- **Auth:** required (`IsAuthenticated`)
- **Parsers:** `multipart/form-data`, form-encoded (supports file/attachment uploads alongside note data)
- **Caching:** `GET` responses are cached per-user for 300 seconds under the key `notes:<user_id>`. Cache is invalidated automatically whenever the user creates a new note.
- **Scoping:** only returns notes owned by `request.user`; new notes are saved with `user=request.user`.

### `GrammarCheckView`

`POST /notes/check-grammar/`

Runs grammar/style checking on submitted text using LanguageTool (`en-US`).

**Request body:**

```json
{ "text": "Text too check for errors." }
```

**Response:**

```json
{
  "grammar_errors": [
    {
      "message": "Possible typo: you repeated a whitespace",
      "context": "...",
      "offset": 0,
      "errorLength": 0,
      "replacements": ["to"]
    }
  ]
}
```

- Returns `400` if `text` is missing or empty.
- Each match includes up to 3 suggested replacements.
- ⚠️ No `permission_classes` set on this view — it inherits DRF's global default (open by default unless `DEFAULT_PERMISSION_CLASSES` is restricted in settings). Add `permission_classes = [permissions.IsAuthenticated]` if it should be locked down like the note endpoints.
- The `LanguageTool("en-US")` instance is created lazily via a module-level `get_grammar_tool()` helper and reused across requests within the same worker process, instead of being re-instantiated on every call.

### `RenderMarkdownView`

`POST /notes/render/`

Converts raw Markdown into HTML.

**Request body:**

```json
{ "markdown": "# Hello\n\nSome **bold** text." }
```

**Response:**

```json
{ "html": "<h1>Hello</h1>\n<p>Some <strong>bold</strong> text.</p>" }
```

- No auth restriction by default (same caveat as above).
- Uses the base `markdown` library with default extensions — add `extensions=[...]` (e.g. `fenced_code`, `tables`) if richer Markdown support is needed.

## Notes / Things to Watch

- **Cache invalidation:** cache is cleared on create but not on update/delete, since this view only handles list/create. If a retrieve/update/destroy view is added later, mirror the same `cache.delete(cache_key)` pattern there.
- **`GrammarCheckView` and `RenderMarkdownView` are unauthenticated by default.** Confirm this is intentional; otherwise add `permission_classes`.
- **LanguageTool instance:** `GrammarCheckView` uses a lazy singleton (`get_grammar_tool()`) so the `LanguageTool("en-US")` server/process is started once on first use per worker process, instead of once per request. Note that `language_tool_python.LanguageTool` isn't guaranteed thread-safe under heavy concurrent load within a single process — if you're running a threaded server (e.g. Gunicorn `gthread` workers), consider adding a lock around `.check()` calls or switching to a remote LanguageTool server (`LanguageToolPublicAPI` or a self-hosted instance via `remote_server=...`).
