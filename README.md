# rndocs

React Native documentation — offline CLI + MCP server.

Search and read all React Native docs without a browser. Works offline after a one-time sync. Integrates with Claude Code as an MCP server.

Inspired by [XCDocs](https://github.com/BitrigApp/XCDocs).

---

## Install

```bash
pip install rndocs
```

Then download the docs (one-time):

```bash
rndocs sync
```

This scrapes all 227 pages from [reactnative.dev](https://reactnative.dev/docs) and stores them in a local SQLite database at `~/.rndocs/docs.db`.

---

## Usage

### Search

```bash
rndocs search "FlatList"
rndocs search "animation"
rndocs search "StyleSheet flex"
```

### Get a full page

```bash
rndocs get flatlist
rndocs get animated
rndocs get stylesheet
rndocs get getting-started
```

### List all pages

```bash
rndocs ls                    # all pages grouped by section
rndocs ls --section APIs     # filter by section
```

### Stats

```bash
rndocs stats
```

---

## MCP Server (Claude Code)

Add to your Claude Code MCP config (`~/.claude/claude_desktop_config.json` or Claude Code settings):

```json
{
  "mcpServers": {
    "rndocs": {
      "command": "rndocs-mcp"
    }
  }
}
```

This exposes three tools to Claude:

- **`search_react_native_docs`** — search by keyword or concept
- **`get_react_native_doc`** — get full page content by slug
- **`list_react_native_docs`** — list all pages, optionally filtered by section

---

## Refresh docs

```bash
rndocs sync          # re-scrape all pages
```

---

## How it works

- Uses [Scrapling](https://github.com/D4Vinci/Scrapling) to scrape `reactnative.dev/docs`
- Stores content in SQLite with FTS5 full-text search
- All search and retrieval is fully offline after sync
- MCP server built with [FastMCP](https://github.com/jlowin/fastmcp)

---

## Requirements

- Python 3.11+
- macOS / Linux / Windows
