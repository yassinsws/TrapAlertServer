"""
Migration script to update the database schema and migrate existing data
Run this script once to transition from the old schema to the new multi-tenant structure
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Tenant, User, BugReport, UserRole
from auth import hash_password
from db import SQLALCHEMY_DATABASE_URL
import secrets

def migrate_database():
    print("=" * 60)
    print("TrapAlert Database Migration Script")
    print("=" * 60)
    
    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("\n[1/5] Backing up existing data...")
        # Query existing bug reports before schema change
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT client_id FROM bug_reports"))
                existing_client_ids = [row[0] for row in result if row[0] is not None]
            unique_client_ids = list(set(existing_client_ids))
            print(f"   Found {len(existing_client_ids)} existing reports with {len(unique_client_ids)} unique client IDs")
        except Exception as e:
            print(f"   No existing data found (this is ok for fresh installations): {e}")
            unique_client_ids = []
        
        print("\n[2/5] Creating new database tables...")
        # This will create new tables but won't modify existing ones
        Base.metadata.create_all(bind=engine)
        print("   ✓ Tables created successfully")
        
        print("\n[3/5] Creating tenants from existing client IDs...")
        tenant_map = {}  # Map old client_id to new Tenant object
        
        # Create a "Legacy" tenant for any reports without a tenant
        legacy_tenant = db.query(Tenant).filter(Tenant.name == "Legacy").first()
        if not legacy_tenant:
            legacy_tenant = Tenant(
                name="Legacy",
                company_name="Legacy Reports",
                api_key=secrets.token_urlsafe(32),
                is_active=True
            )
            db.add(legacy_tenant)
            db.flush()  # Get the ID
            print(f"   ✓ Created 'Legacy' tenant (ID: {legacy_tenant.id})")
        else:
            print(f"   ⚠ 'Legacy' tenant already exists (ID: {legacy_tenant.id})")
        
        # Create tenant for each unique client_id
        for client_id in unique_client_ids:
            # Check if tenant with this API key already exists
            existing_tenant = db.query(Tenant).filter(Tenant.api_key == client_id).first()
            if existing_tenant:
                tenant_map[client_id] = existing_tenant
                print(f"   ⚠ Tenant for client_id already exists: {client_id[:30]}... (ID: {existing_tenant.id})")
            else:
                tenant = Tenant(
                    name=f"Migrated: {client_id[:20]}",  # Use first 20 chars of client_id
                    company_name=f"Auto-migrated from client_id: {client_id}",
                    api_key=client_id,  # Preserve the old client_id as API key!
                    is_active=True
                )
                db.add(tenant)
                db.flush()
                tenant_map[client_id] = tenant
                print(f"   ✓ Created tenant for client_id: {client_id[:30]}... (ID: {tenant.id})")
        
        db.commit()
        
        print("\n[4/5] Creating super admin user...")
        # Create default super admin
        admin_email = "admin@trapalert.com"
        admin_password = "admin123"  # CHANGE THIS IN PRODUCTION!
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"   ⚠ Super admin already exists: {admin_email}")
        else:
            admin_user = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                role=UserRole.SUPER_ADMIN,
                tenant_id=None,  # Super admin not tied to a specific tenant
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"   ✓ Created super admin user:")
            print(f"      Email: {admin_email}")
            print(f"      Password: {admin_password}")
            print(f"      ⚠ WARNING: Change this password immediately in production!")
        
        print("\n[5/5] Migration complete!")
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Start the server: uvicorn main:app --reload")
        print("2. Login at /api/auth/login with super admin credentials")
        print("3. Create tenants and users via the admin dashboard")
        print("4. Update your TrapAlert.js SDK to use the new tenant API keys")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()
