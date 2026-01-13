import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use DATABASE_URL from env if available (Supabase), else local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./trap_alert.db")

# Fix for some postgres URI starting with postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if "sqlite" in DATABASE_URL:
    print("DEBUG: Using local SQLite database")
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Mask password for safety
    import re
    masked_url = re.sub(r':([^@]+)@', r':****@', DATABASE_URL)
    print(f"DEBUG: Connecting to database: {masked_url}")
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is the "Cleaner" way to handle connections (Dependency Injection)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()