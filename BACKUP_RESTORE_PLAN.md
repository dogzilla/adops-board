# Kanban Board — Backup & Restore Plan

## Current Data State (as of 2026-06-26 09:41 UTC)

| Element | Count |
|---|---|
| Boards | 1 (AdXact Morning Prep Board) |
| Columns | 3 |
| Cards (buckets) | 43 |
| Subtasks (items) | 128 |

## Storage Architecture

- **Database**: `/home/desi/kanban/data/kanban.db` (SQLite)
- **Volume mount**: bind mount → container at `/app/data`
- **JSON export**: `/home/desi/kanban/data/doc_0f2fe11fe60c_board_data.json`
- **Frontend**: `/home/desi/kanban/frontend/index.html` (single-file HTML/CSS/JS)

## Pre-Change Backup (2026-06-26 09:41)

Backup directory: `/home/desi/kanban/backup_20260626_094129/`

| File | Source | Purpose |
|---|---|---|
| `kanban.db.bak` | `kanban.db` | Binary database copy |
| `kanban_db_dump.sql` | `kanban.db` | Full SQL dump — complete schema + data |
| `board_data.json.bak` | JSON export | Board export backup |
| `index.html.pre-mobile.bak` | frontend/index.html | Frontend source before changes |

## Restore Procedures

### Option 1: Full database restore (recommended)
```bash
cp /home/desi/kanban/backup_20260626_094129/kanban.db.bak /home/desi/kanban/data/kanban.db
docker restart kanban
```

### Option 2: SQL dump restore (full fidelity)
```bash
sqlite3 /home/desi/kanban/data/kanban.db < /home/desi/kanban/backup_20260626_094129/kanban_db_dump.sql
docker restart kanban
```

### Option 3: Frontend-only rollback
```bash
cp /home/desi/kanban/backup_20260626_094129/index.html.pre-mobile.bak /home/desi/kanban/frontend/index.html
cd /home/desi/kanban && docker build -t kanban .
docker stop kanban && docker rm kanban
docker run -d --name kanban -p 8889:8000 -v kanban-data:/app/data kanban
```

### Option 4: JSON export import
If the database is corrupted but the JSON export is intact:
```bash
# Rebuild from JSON via API
curl -X POST http://localhost:8889/api/v1/import \
  -H "Authorization: Bearer kanban-secret-key" \
  -H "Content-Type: application/json" \
  -d @/home/desi/kanban/backup_20260626_094129/board_data.json.bak
```

## Important Notes

- **Data directory (`/home/desi/kanban/data`) must NEVER be deleted or wiped.** It is a bind mount and holds all persistent data.
- Frontend changes require a **Docker rebuild** (not just `docker restart`). The Dockerfile copies `index.html` into the image.
- Database changes are zero-risk since the data directory is never modified during frontend work.
- All backups are timestamped and stored outside the container.
