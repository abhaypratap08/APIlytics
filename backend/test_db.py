"""Run from APIlytics/backend with: python ../scripts/test_db.py"""
from sqlalchemy import text
from app.db.session import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1")).scalar()
    print(f"DB connection OK, SELECT 1 => {result}")
