# Database Setup Guide

This guide walks you through setting up the PostgreSQL database for the Diablo 4 Item Comparator.

## Prerequisites

1. **PostgreSQL 14+** installed and running
2. **Python 3.10+** with virtual environment activated
3. **Dependencies installed** from `requirements.txt`

## Installation Steps

### 1. Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Or use WSL2 with Linux installation

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

### 2. Create Database

```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE diablo4_items;
CREATE USER diablo_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE diablo4_items TO diablo_user;

# Exit psql
\q
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```env
DATABASE_URL=postgresql://diablo_user:your_secure_password@localhost:5432/diablo4_items
```

### 4. Initialize Database

**Option A: Using the init script (Recommended)**
```bash
cd src
python init_db.py --all
```

This will:
- Create all database tables
- Seed reference data (classes, item types, affixes, aspects)

**Option B: Manual steps**
```bash
# Create tables only
python init_db.py --create-tables

# Seed data only (after tables exist)
python init_db.py --seed
```

### 5. Verify Installation

```bash
# Connect to database
psql postgresql://diablo_user:your_secure_password@localhost:5432/diablo4_items

# List tables
\dt

# Check data
SELECT COUNT(*) FROM affixes;
SELECT COUNT(*) FROM aspects;
SELECT COUNT(*) FROM classes;

# Exit
\q
```

Expected counts after seeding:
- **Classes:** 7 (Barbarian, Druid, Necromancer, Rogue, Sorcerer, Spiritborn, Paladin)
- **Item Types:** ~34 (weapons, armor, accessories)
- **Affixes:** ~1,188 (from d4lf data)
- **Aspects:** ~466 (from d4lf data)
- **Affix Categories:** 5 (Offensive, Defensive, Utility, Resource, Mobility)

---

## Database Migrations with Alembic

We use Alembic for schema version control and migrations.

### Create Initial Migration

After setting up the database for the first time:

```bash
# Generate initial migration from models
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Common Migration Commands

```bash
# Create a new migration
alembic revision -m "Add new column to items"

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

---

## Resetting the Database

**CAUTION:** This will delete all data!

```bash
# Drop all tables
python -c "from database import drop_db; drop_db()"

# Recreate everything
python init_db.py --all
```

Or via psql:
```bash
psql postgresql://diablo_user:your_secure_password@localhost:5432/diablo4_items

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO diablo_user;
\q

# Then reinitialize
python init_db.py --all
```

---

## Testing Database Connection

Create a test script `test_db.py`:

```python
from database import get_db
from models import Affix, ItemType, Class

with get_db() as db:
    # Query some data
    affixes = db.query(Affix).limit(5).all()
    item_types = db.query(ItemType).all()
    classes = db.query(Class).all()

    print(f"Affixes: {len(affixes)}")
    print(f"Item Types: {len(item_types)}")
    print(f"Classes: {len(classes)}")

    # Print sample
    print("\nSample affixes:")
    for affix in affixes:
        print(f"  - {affix.name} (ID: {affix.internal_id})")
```

Run it:
```bash
python test_db.py
```

---

## Common Issues

### Issue: "psycopg2.OperationalError: could not connect"

**Solutions:**
1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check DATABASE_URL in `.env` is correct
3. Verify user/password: `psql postgresql://diablo_user:password@localhost:5432/diablo4_items`

### Issue: "relation does not exist"

**Solution:**
Tables haven't been created. Run:
```bash
python init_db.py --create-tables
```

### Issue: "FATAL: password authentication failed"

**Solution:**
1. Reset password in PostgreSQL:
```bash
sudo -u postgres psql
ALTER USER diablo_user WITH PASSWORD 'new_password';
\q
```
2. Update `.env` with new password

### Issue: "Permission denied for schema public"

**Solution:**
```bash
sudo -u postgres psql diablo4_items
GRANT ALL ON SCHEMA public TO diablo_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO diablo_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO diablo_user;
\q
```

---

## Schema Documentation

See `docs/database_schema.md` for complete schema documentation, including:
- Entity relationship diagram
- Table definitions
- Index strategy
- Query examples

---

## Next Steps

Once your database is set up:

1. **Explore the data:**
   ```bash
   psql postgresql://diablo_user:password@localhost:5432/diablo4_items
   SELECT * FROM affixes WHERE name ILIKE '%critical%' LIMIT 10;
   ```

2. **Create your first build:**
   ```python
   from database import get_db
   from models import Build, BuildAffixWeight, Class, Affix

   with get_db() as db:
       # Get Sorcerer class
       sorcerer = db.query(Class).filter_by(name='Sorcerer').first()

       # Create build
       build = Build(
           name='Fire Sorcerer',
           class_id=sorcerer.id,
           description='Focuses on fire damage and critical strikes'
       )
       db.add(build)
       db.flush()

       # Add affix priorities
       crit_affix = db.query(Affix).filter(
           Affix.internal_id == 'critical_strike_damage'
       ).first()

       if crit_affix:
           weight = BuildAffixWeight(
               build_id=build.id,
               affix_id=crit_affix.id,
               weight=95.0,  # High priority
               priority=1,
               is_required=True
           )
           db.add(weight)

       print(f"Created build: {build.name}")
   ```

3. **Start building the OCR pipeline** (next phase)
