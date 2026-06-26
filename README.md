# AdXact AdOps Board

A Kanban board for advertising operations, built with FastAPI and SQLite.

## Tech Stack

- **Backend:** FastAPI + Python 3.11 + SQLite + SQLModel
- **Frontend:** Vanilla HTML/CSS/JS (single-page application)
- **Deployment:** Docker (single container, port 8889)

## Quick Start

```bash
# Build and run
cd kanban
docker build -t kanban .
docker run -d --name kanban --restart=unless-stopped -p 8889:8000 -v ./data:/app/data kanban
```

## URLs

| Environment | URL |
|---|---|
| Internal | `http://192.168.7.174:8889` |
| External (via reverse proxy) | `https://board.arlo.tools` |

## API

All write endpoints require Bearer token authentication.

**Token:** `kanban-secret-key`

### Authentication

```bash
Authorization: Bearer kanban-secret-key
```

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/boards` | Get full board state (columns, buckets, items) |
| POST | `/api/v1/buckets` | Create a new card (bucket) |
| PATCH | `/api/v1/buckets/:id` | Update card (title, description, assigned_to) |
| DELETE | `/api/v1/buckets/:id` | Delete a card |
| POST | `/api/v1/buckets/:id/move` | Move card to a different column |
| POST | `/api/v1/items` | Add a subtask to a card |
| PATCH | `/api/v1/items/:id` | Update a subtask (text, done status) |
| DELETE | `/api/v1/items/:id` | Delete a subtask |
| POST | `/api/v1/columns` | Create a new column |
| PATCH | `/api/v1/columns/:id` | Update a column (name, sort_order) |
| DELETE | `/api/v1/columns/:id` | Delete a column and all its cards |
| GET | `/api/v1/export` | Export board as JSON |

### Example: Create a Card

```bash
curl -X POST http://localhost:8889/api/v1/buckets \
  -H "Authorization: Bearer kanban-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"column_id": 1, "name": "New Card", "assigned_to": "John Doe"}'
```

### Example: Move a Card

```bash
curl -X POST http://localhost:8889/api/v1/buckets/1/move \
  -H "Authorization: Bearer kanban-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"column_id": 2}'
```

## Data Model

```
Board
  └── Columns (sort_order determines left-to-right order)
        └── Buckets (cards)
              ├── assigned_to (string)
              └── Items (subtasks)
                    ├── text
                    ├── done (boolean)
                    ├── start_date
                    ├── due_date
                    └── assigned_to
```

## Deployment Details

- Container name: `kanban`
- Port: `8889` (exposed), `8000` (inside container)
- Data volume: `/app/data/kanban.db` (bind-mounted to host)
- Restart policy: `unless-stopped`
- SQLite database is persistent across container restarts

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | `kanban-secret-key` | Bearer token for write endpoints |
| `DB_PATH` | `/app/data/kanban.db` | SQLite database path |
