# AdXact AdOps Board API Documentation

## Overview
The AdXact AdOps Board is a Kanban-style project management system with REST API support. Designed for both human and LLM agent interaction.

## Authentication
All **write operations** (POST, PATCH, DELETE) require API key authentication via Bearer token:

```
Authorization: Bearer ***
```

**Exception:** `PATCH /api/v1/items/{item_id}` does not require authentication.

## Base URL
```
http://<host>:8889/api/v1
```

## Endpoints

### Board Management

#### GET /api/v1/boards
Retrieve the full board state including columns, cards (buckets), and subtasks (items).

**Response:**
```json
{
  "title": "AdXact Morning Prep Board",
  "columns": [{"id": 1, "board_id": 1, "name": "To Do", "sort_order": 1}, ...],
  "buckets": [{"id": 1, "column_id": 1, "name": "Card Title", ...}, ...],
  "items": [{"id": 1, "bucket_id": 1, "text": "Subtask text", ...}, ...]
}
```

#### POST /api/v1/setup
Initialize default columns ("To Do", "In Progress", "Done") if board is empty.

**Headers:** `Authorization: Bearer ***`

**Response:**
```json
{
  "status": "ok",
  "columns": [{"id": 1, "board_id": 1, "name": "To Do", "sort_order": 1}, ...]
}
```

### Column Operations

#### POST /api/v1/columns
Create a new column.

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "name": "Review"
}
```

**Response:**
```json
{
  "id": 4,
  "board_id": 1,
  "name": "Review",
  "sort_order": 4
}
```

#### PATCH /api/v1/columns/{column_id}
Update column name or sort order.

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "name": "In Review",
  "sort_order": 2
}
```

**Response:** Updated column JSON.

#### DELETE /api/v1/columns/{column_id}
Delete a column and all its cards (buckets) and subtasks (items).

**Headers:** `Authorization: Bearer ***`

### Card (Bucket) Operations

#### POST /api/v1/buckets
Create a new card (bucket).

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "column_id": 1,
  "name": "Design Landing Page",
  "description": "Create wireframes and mockups",
  "start_date": "2026-06-25",
  "due_date": "2026-07-10",
  "assigned_to": "Israel Alvarez"
}
```

**Response:**
```json
{
  "id": 30,
  "column_id": 1,
  "name": "Design Landing Page",
  "description": "Create wireframes and mockups",
  "sort_order": 999
}
```

#### PATCH /api/v1/buckets/{bucket_id}
Update card (bucket) details. All fields are optional.

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "name": "Updated Title",
  "description": "Updated description",
  "column_id": 2,
  "start_date": "2026-06-26",
  "due_date": "2026-07-15",
  "assigned_to": "Carson Harris"
}
```

**Response:** Updated bucket JSON.

#### POST /api/v1/buckets/{bucket_id}/move
Move a card to a different column.

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "column_id": 3
}
```

**Response:**
```json
{
  "status": "moved",
  "bucket_id": 30,
  "column_id": 3
}
```

#### DELETE /api/v1/buckets/{bucket_id}
Delete a card (bucket) and all its subtasks (items).

**Headers:** `Authorization: Bearer ***`

**Response:**
```json
{
  "status": "deleted"
}
```

### Subtask (Item) Operations

#### POST /api/v1/items
Create a subtask (item) within a card.

**Headers:** `Authorization: Bearer ***`

**Body:**
```json
{
  "bucket_id": 30,
  "text": "Create wireframes",
  "done": false
}
```

**Response:**
```json
{
  "id": 120,
  "bucket_id": 30,
  "text": "Create wireframes",
  "done": false,
  "sort_order": 999,
  "date_created": "2026-06-25 21:30:00",
  "date_completed": null,
  "start_date": null,
  "due_date": null,
  "assigned_to": null
}
```

#### PATCH /api/v1/items/{item_id}
Update subtask - toggle `done`, change text, or update fields. **No auth required.**

**Body:**
```json
{
  "done": true,
  "text": "Completed wireframes"
}
```

**Auto-behavior:**
- When `done` changes from `false` to `true`, `date_completed` is automatically set to the current timestamp
- When `done` changes from `true` to `false`, `date_completed` is cleared

**Response:**
```json
{
  "id": 120,
  "done": true,
  "date_completed": "2026-06-25 21:35:00"
}
```

#### DELETE /api/v1/items/{item_id}
Delete a subtask (item).

**Headers:** `Authorization: Bearer ***`

**Response:**
```json
{
  "status": "deleted"
}
```

### Data Export

#### GET /api/v1/export
Export board data as JSON.

**Query Parameters:**
- `completed=false` (default): Exclude completed cards (where ALL subtasks are marked `done=true`)
- `completed=true`: Include all cards

**Response:**
```json
{
  "board": "AdXact Morning Prep Board",
  "exported_at": "2026-06-25 21:40:00",
  "columns": [...],
  "buckets": [...],
  "items": [...]
}
```

### Real-time Updates (SSE)

> **Note:** SSE is currently **disabled** in production. The endpoint returns `{"status": "SSE disabled"}`.

#### GET /api/v1/events
Subscribe to real-time updates via Server-Sent Events.

**Response:** Continuous stream of events:
```
id: 1
event: bucket_created
data: {"bucket_id": 31, "column_id": 1}

id: 2
event: bucket_moved
data: {"bucket_id": 30, "from_column": 1, "to_column": 2}
```

**Event Types:**
- `bucket_created` - New card created
- `bucket_updated` - Card updated
- `bucket_moved` - Card moved to different column
- `bucket_deleted` - Card deleted
- `item_created` - Subtask added
- `item_updated` - Subtask toggled/updated
- `item_deleted` - Subtask deleted
- `column_created` - New column created
- `column_updated` - Column updated
- `column_deleted` - Column deleted

## Assignment Options
Cards and subtasks support assignment with the following values:
- `Israel Alvarez`
- `Carson Harris`
- Empty / `null` (Unassigned)

## Data Model

```
Board
+-- Columns (To Do, In Progress, Done, custom)
|   +-- Buckets (Cards)
|   |   +-- id, column_id, name, description, sort_order
|   |   +-- start_date, due_date, assigned_to
|   |   +-- Items (Subtasks)
|   |       +-- id, bucket_id, text, done, sort_order
|   |       +-- date_created (auto-set on creation)
|   |       +-- date_completed (auto-set when done=true)
+-- title, updated
```

## Example Usage (cURL)

```bash
# Get board
curl http://localhost:8889/api/v1/boards

# Create card
curl -X POST http://localhost:8889/api/v1/buckets \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d "{"column_id": 1, "name": "Test Card", "assigned_to": "Israel Alvarez"}"

# Move card
curl -X POST http://localhost:8889/api/v1/buckets/30/move \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d "{"column_id": 2}"

# Toggle subtask (no auth needed)
curl -X PATCH http://localhost:8889/api/v1/items/120 \
  -H "Content-Type: application/json" \
  -d "{"done": true}"

# Create subtask
curl -X POST http://localhost:8889/api/v1/items \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d "{"bucket_id": 30, "text": "Subtask", "done": false}"

# Export board (excluding completed cards)
curl http://localhost:8889/api/v1/export?completed=false

# Delete card
curl -X DELETE http://localhost:8889/api/v1/buckets/30 \
  -H "Authorization: Bearer ***`

# Delete subtask
curl -X DELETE http://localhost:8889/api/v1/items/120 \
  -H "Authorization: Bearer ***`
```

## Notes
- Cards are draggable between columns via the card header
- Subtasks auto-generate `date_created` on creation and `date_completed` when marked done
- All timestamps are in `YYYY-MM-DD HH:MM:SS` format
- A card is considered "completed" when ALL its subtasks are marked `done=true`
- Dragging cards between columns triggers the `bucket_moved` event (SSE)
- The board title defaults to "AdXact Morning Prep Board"
