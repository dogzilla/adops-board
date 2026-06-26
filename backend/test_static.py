from fastapi import FastAPI, HTTPException, Depends, Request

app = FastAPI()

@app.patch("/test")
async def test_endpoint():
    return {"test": "works", "date_completed": "2026-06-25"}
