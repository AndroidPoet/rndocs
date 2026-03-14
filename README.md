# rndocs

React Native docs in your terminal — search and read without opening a browser.

---

## Install

```bash
pip install rndocs
```

## Download the docs

```bash
rndocs sync
```

That's it. Everything works offline after this.

---

## Usage

**Search**
```bash
rndocs search "FlatList"
rndocs search "how to handle keyboard"
rndocs search "animation"
```

**Read a page**
```bash
rndocs get flatlist
rndocs get stylesheet
rndocs get animated
```

**Browse all pages**
```bash
rndocs ls
```

**Keep docs up to date**
```bash
rndocs sync
```

---

## Claude Code Integration

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "rndocs": {
      "command": "rndocs-mcp"
    }
  }
}
```

Claude can now search and read React Native docs directly in your conversations.
