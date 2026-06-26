import os
import re
import time
import asyncio
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import Column, DateTime, Index

# --- CONFIGURATION ---
DB_PATH = os.getenv("DB_PATH", "/app/data/kanban.db")
SOURCE_MD_PATH = os.getenv("SOURCE_MD_PATH", "/app/data/DAILY_MORNING_PREP.md")
API_KEY = os.getenv("API_KEY", "kanban-secret-key")

# --- DATABASE SETUP ---
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = "AdXact Morning Prep Board"
    updated: str = ""

class Column(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    name: str  # e.g. "To Do", "In Progress", "Done"
    sort_order: int = 0

class Bucket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    column_id: int = Field(foreign_key="column.id")
    name: str  # Card title
    description: str = ""  # Summary for collapsed view
    sort_order: int = 0

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bucket_id: int = Field(foreign_key="bucket.id")
    text: str
    done: bool = False
    sort_order: int = 0
    date_created: Optional[str] = None  # Auto-set on creation
    date_completed: Optional[str] = None  # Auto-set when done=true
    start_date: Optional[str] = None  # YYYY-MM-DD (card level)
    due_date: Optional[str] = None    # YYYY-MM-DD (card level)
    assigned_to: Optional[str] = None

def init_db():
    SQLModel.metadata.create_all(engine)

# --- EVENTS SYSTEM (SSE) ---
class EventBroadcaster:
    def __init__(self):
        self.listeners: Dict[int, asyncio.Queue] = {}
        self.counter = 0

    async def subscribe(self):
        q = asyncio.Queue()
        self.listeners[id(q)] = q
        try:
            while True:
                event = await q.get()
                yield f"id: {self.counter}\nevent: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                self.counter += 1
        finally:
            del self.listeners[id(q)]

    async def broadcast(self, event_type: str, data: dict):
        payload = {"type": event_type, "data": data}
        for q in self.listeners.values():
            await q.put(payload)

broadcaster = EventBroadcaster()

# --- APP LIFECYCLE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    asyncio.create_task(sync_worker())
    yield

app = FastAPI(title="Kanban API", lifespan=lifespan)

# --- AGENT AUTH ---
def verify_agent(request: Request):
    key = request.headers.get("Authorization")
    if key != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return request

# --- ROUTES ---
@app.get("/api/v1/setup")
def setup_defaults(agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        board = session.get(Board, 1)
        if not board:
            board = Board(title="AdXact Morning Prep Board", updated=datetime.now().strftime("%Y-%m-%d"))
            session.add(board)
            session.commit()
        
        col_names = ["To Do", "In Progress", "Done"]
        for i, name in enumerate(col_names):
            col = session.exec(select(Column).where(Column.name == name)).first()
            if not col:
                col = Column(board_id=board.id, name=name, sort_order=i+1)
                session.add(col)
        
        session.commit()
        cols = session.exec(select(Column).where(Column.board_id == board.id)).all()
        return {"status": "ok", "columns": [c.dict() for c in cols]}

@app.get("/api/v1/boards")
def get_board():
    with Session(engine) as session:
        board = session.get(Board, 1)
        if not board:
            board = Board(title="AdXact Morning Prep Board", updated=datetime.now().strftime("%Y-%m-%d"))
            session.add(board)
            session.commit()
        columns = session.exec(select(Column).where(Column.board_id == board.id)).all()
        buckets = session.exec(select(Bucket)).all()
        items = session.exec(select(Item)).all()
        
        return {
            "title": board.title,
            "columns": [c.dict() for c in columns],
            "buckets": [b.dict() for b in buckets],
            "items": [i.dict() for i in items]
        }

# --- COLUMN CRUD ---
@app.post("/api/v1/columns")
async def create_column(data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        board = session.get(Board, 1)
        if not board: raise HTTPException(404, "Board not found")
        
        max_order = session.exec(select(Column.sort_order).where(Column.board_id == board.id)).all()
        max_order = max(max_order) if max_order else 0
        
        column = Column(board_id=board.id, name=data["name"], sort_order=max_order + 1)
        session.add(column)
        session.commit()
        
        await broadcaster.broadcast("column_created", {"column_id": column.id})
        return column.dict()

@app.patch("/api/v1/columns/{column_id}")
async def update_column(column_id: int, data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        column = session.get(Column, column_id)
        if not column: raise HTTPException(404, "Column not found")
        
        if "name" in data:
            column.name = data["name"]
        if "sort_order" in data:
            column.sort_order = data["sort_order"]
        session.commit()
        
        await broadcaster.broadcast("column_updated", {"column_id": column.id})
        return column.dict()

@app.delete("/api/v1/columns/{column_id}")
async def delete_column(column_id: int, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        column = session.get(Column, column_id)
        if not column: raise HTTPException(404, "Column not found")
        
        # Delete all buckets and items in this column
        buckets = session.exec(select(Bucket).where(Bucket.column_id == column_id)).all()
        for bucket in buckets:
            items = session.exec(select(Item).where(Item.bucket_id == bucket.id)).all()
            for item in items:
                session.delete(item)
            session.delete(bucket)
        
        session.delete(column)
        session.commit()
        
        await broadcaster.broadcast("column_deleted", {"column_id": column_id})
        return {"status": "deleted"}

# --- BUCKET (CARD) ROUTES ---
@app.post("/api/v1/buckets")
async def create_bucket(data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        col = session.get(Column, data["column_id"])
        if not col: raise HTTPException(404, "Column not found")
        
        bucket = Bucket(column_id=data["column_id"], name=data["name"], description=data.get("description", ""), sort_order=999)
        session.add(bucket)
        session.commit()
        
        await broadcaster.broadcast("bucket_created", {"bucket_id": bucket.id, "column_id": bucket.column_id})
        return bucket.dict()

@app.patch("/api/v1/buckets/{bucket_id}")
async def update_bucket(bucket_id: int, data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        bucket = session.get(Bucket, bucket_id)
        if not bucket: raise HTTPException(404, "Bucket not found")
        
        for k, v in data.items():
            setattr(bucket, k, v)
        session.commit()
        
        await broadcaster.broadcast("bucket_updated", {"bucket_id": bucket.id})
        return bucket.dict()

@app.post("/api/v1/items")
async def create_item(data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        bucket = session.get(Bucket, data["bucket_id"])
        if not bucket: raise HTTPException(404, "Bucket not found")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = Item(
            bucket_id=data["bucket_id"],
            text=data["text"],
            done=data.get("done", False),
            sort_order=999,
            date_created=now,
            start_date=data.get("start_date"),
            due_date=data.get("due_date"),
            assigned_to=data.get("assigned_to")
        )
        session.add(item)
        session.commit()
        
        await broadcaster.broadcast("item_created", {"item_id": item.id, "bucket_id": item.bucket_id})
        return item.dict()

@app.patch("/api/v1/items/{item_id}")
async def update_item(item_id: int, data: dict = ...):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item: raise HTTPException(404, "Item not found")
        
        old_done = item.done
        if data.get("done") is not None:
            item.done = data["done"]
        
        # Auto-set dates
        if data.get("done") and not old_done:
            item.date_completed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for k, v in data.items():
            if k not in ("done",):
                setattr(item, k, v)
        
        session.add(item)
        session.commit()
        
        return {"id": item.id, "done": item.done, "date_completed": item.date_completed}

@app.delete("/api/v1/items/{item_id}")
async def delete_item(item_id: int, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if not item: raise HTTPException(404, "Item not found")
        
        bucket_id = item.bucket_id
        session.delete(item)
        session.commit()
        
        await broadcaster.broadcast("item_deleted", {"item_id": item_id, "bucket_id": bucket_id})
        return {"status": "deleted"}

@app.post("/api/v1/buckets/{bucket_id}/move")
async def move_bucket(bucket_id: int, data: dict, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        bucket = session.get(Bucket, bucket_id)
        if not bucket: raise HTTPException(404, "Bucket not found")
        
        new_col_id = data.get("column_id")
        target_col = session.get(Column, new_col_id)
        if not target_col: raise HTTPException(404, "Target column not found")
        
        old_col_id = bucket.column_id
        bucket.column_id = new_col_id
        session.commit()
        
        await broadcaster.broadcast("bucket_moved", {"bucket_id": bucket.id, "from_column": old_col_id, "to_column": new_col_id})
        return {"status": "moved", "bucket_id": bucket.id, "column_id": new_col_id}

@app.delete("/api/v1/buckets/{bucket_id}")
async def delete_bucket(bucket_id: int, agent: Request = Depends(verify_agent)):
    with Session(engine) as session:
        bucket = session.get(Bucket, bucket_id)
        if not bucket: raise HTTPException(404, "Bucket not found")
        
        bucket_id_to_delete = bucket.id
        column_id = bucket.column_id
        
        items = session.exec(select(Item).where(Item.bucket_id == bucket_id)).all()
        for item in items:
            session.delete(item)
        
        session.delete(bucket)
        session.commit()
        
        await broadcaster.broadcast("bucket_deleted", {"bucket_id": bucket_id_to_delete, "column_id": column_id})
        return {"status": "deleted"}

@app.get("/api/v1/events")
async def sse_endpoint():
    # Temporarily disabled for debugging
    return {"status": "SSE disabled"}

# async def sse_endpoint():
#     return StreamingResponse(broadcaster.subscribe(), media_type="text/event-stream")

# --- SYNC WORKER ---
async def parse_markdown():
    if not os.path.exists(SOURCE_MD_PATH):
        print(f"Source MD not found at {SOURCE_MD_PATH}")
        return

    with open(SOURCE_MD_PATH, 'r') as f:
        content = f.read()

    await broadcaster.broadcast("sync_complete", {"status": "ok"})

async def sync_worker():
    while True:
        await parse_markdown()
        await asyncio.sleep(60)

# --- STATIC FILES ---
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("/app/frontend/index.html")

@app.get("/api/v1/export")
async def export_board(completed: bool = False):
    """Export board as JSON. If completed=false, excludes completed cards (buckets) but keeps all items."""
    with Session(engine) as session:
        board = session.get(Board, 1)
        if not board: return {"error": "Board not found"}
        
        columns = session.exec(select(Column).where(Column.board_id == board.id)).all()
        buckets = session.exec(select(Bucket)).all()
        items = session.exec(select(Item)).all()
        
        # Filter buckets if excluding completed
        if not completed:
            # A card is "completed" if ALL its items are done
            bucket_ids = [b.id for b in buckets]
            items_by_bucket = {}
            for item in items:
                if item.bucket_id in items_by_bucket:
                    items_by_bucket[item.bucket_id].append(item)
                else:
                    items_by_bucket[item.bucket_id] = [item]
            
            filtered_buckets = []
            for bucket in buckets:
                b_items = items_by_bucket.get(bucket.id, [])
                if not b_items:
                    filtered_buckets.append(bucket)
                elif all(i.done for i in b_items):
                    continue  # Skip completed cards
                else:
                    filtered_buckets.append(bucket)
            
            buckets = filtered_buckets
        
        # Build response
        result = {
            "board": board.title,
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "columns": [c.dict() for c in columns],
            "buckets": [b.dict() for b in buckets],
            "items": [i.dict() for i in items if i.bucket_id in [b.id for b in buckets]]
        }
        return result
