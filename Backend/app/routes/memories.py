import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Response, status
from typing import Optional

from app.db import session
from app.schemas.memories import MemorySchema, MemoriesResponse, MetaSchema, MemoryCreate

router = APIRouter(tags=["memories"])

@router.get("/memories", response_model=MemoriesResponse)
def get_memories(page: int = 1, limit: int = 20, search: Optional[str] = None):
    with session() as conn:
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        if search:
            where_clause = "WHERE content LIKE ?"
            params.append(f"%{search}%")
            
        count_query = f"SELECT COUNT(*) as total FROM memories {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]
        
        offset = (page - 1) * limit
        query = f"SELECT * FROM memories {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            tags = json.loads(row["tags"]) if row["tags"] else []
            data.append(MemorySchema(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"],
                tags=tags
            ))
            
        return MemoriesResponse(
            data=data,
            meta=MetaSchema(total=total, page=page, limit=limit)
        )

@router.post("/memory", response_model=MemorySchema, status_code=status.HTTP_201_CREATED)
def create_memory(memory: MemoryCreate):
    mem_id = f"mem_{uuid.uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    tags_json = json.dumps(memory.tags) if memory.tags else "[]"
    
    with session() as conn:
        conn.execute(
            "INSERT INTO memories (id, content, created_at, tags) VALUES (?, ?, ?, ?)",
            (mem_id, memory.content, created_at, tags_json)
        )
        
    return MemorySchema(
        id=mem_id,
        content=memory.content,
        created_at=created_at,
        tags=memory.tags or []
    )

@router.delete("/memory/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(id: str):
    with session() as conn:
        conn.execute("DELETE FROM memories WHERE id = ?", (id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
