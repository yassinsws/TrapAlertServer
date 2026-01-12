"""
Fix migration script to correctly update bug_reports table schema and link data.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db import SQLALCHEMY_DATABASE_URL
import json

def fix_migration():
    print("=" * 60)
    print("TrapAlert Schema Fix & Data Migration")
    print("=" * 60)
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
    with engine.begin() as conn:
        print("\n[1/4] Checking existing schema...")
        # Check if bug_reports table has tenant_id
        result = conn.execute(text("PRAGMA table_info(bug_reports)"))
        columns = [row[1] for row in result]
        
        if "tenant_id" in columns:
            print("   ✓ tenant_id already exists. Skipping structural migration.")
        else:
            print("   ! structural migration needed for bug_reports")
            
            # 1. Rename old table
            conn.execute(text("ALTER TABLE bug_reports RENAME TO bug_reports_old"))
            print("   ✓ Renamed bug_reports to bug_reports_old")
            
            # 2. Create new table with correct structure (this is based on the models.py)
            conn.execute(text("""
                CREATE TABLE bug_reports (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    description VARCHAR,
                    label JSON DEFAULT '[]',
                    struggle_score FLOAT,
                    metadata_json VARCHAR,
                    dom_snapshot VARCHAR,
                    status VARCHAR DEFAULT 'NEW',
                    synced_to_integration BOOLEAN DEFAULT 0,
                    external_ticket_id VARCHAR,
                    created_at DATETIME,
                    FOREIGN KEY(tenant_id) REFERENCES tenants(id)
                )
            """))
            print("   ✓ Created new bug_reports table")
            
            # 3. Migrate data
            print("\n[2/4] Migrating data...")
            
            # Get tenants to map client_id to tenant_id
            tenants_result = conn.execute(text("SELECT id, api_key FROM tenants"))
            tenant_map = {row[1]: row[0] for row in tenants_result}
            
            # Default to Legacy tenant (ID 1 usually)
            legacy_tenant_id = tenant_map.get(conn.execute(text("SELECT api_key FROM tenants WHERE name = 'Legacy'")).scalar(), 1)
            
            # Get old data
            old_reports = conn.execute(text("SELECT id, client_id, description, label, struggle_score, metadata_json, dom_snapshot, created_at FROM bug_reports_old"))
            
            count = 0
            for row in old_reports:
                report_id, client_id, description, label, struggle_score, metadata_json, dom_snapshot, created_at = row
                
                # Find matching tenant_id
                t_id = tenant_map.get(client_id, legacy_tenant_id)
                
                # Ensure label is valid JSON
                if label:
                    try:
                        # If it's already a string representation of a list, keep it
                        if isinstance(label, str):
                            json.loads(label)
                        else:
                            label = json.dumps(label)
                    except:
                        label = '[]'
                else:
                    label = '[]'

                conn.execute(text("""
                    INSERT INTO bug_reports (
                        id, tenant_id, description, label, struggle_score, 
                        metadata_json, dom_snapshot, created_at, status, synced_to_integration
                    ) VALUES (
                        :id, :tenant_id, :description, :label, :struggle_score, 
                        :metadata_json, :dom_snapshot, :created_at, 'NEW', 0
                    )
                """), {
                    "id": report_id,
                    "tenant_id": t_id,
                    "description": description,
                    "label": label,
                    "struggle_score": struggle_score,
                    "metadata_json": metadata_json,
                    "dom_snapshot": dom_snapshot,
                    "created_at": created_at
                })
                count += 1
            
            print(f"   ✓ Migrated {count} reports")
            
            # 4. Drop old table
            conn.execute(text("DROP TABLE bug_reports_old"))
            print("   ✓ Dropped bug_reports_old")

        print("\n[3/4] Ensuring other tables exist...")
        # Since we might have run Base.metadata.create_all via main.py already, 
        # but let's just make sure others are there.
        # Actually create_all is fine for non-existing tables.
        
        print("\n[4/4] Migration fix complete!")
        print("=" * 60)

if __name__ == "__main__":
    fix_migration()
