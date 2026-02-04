"""
Setup v3.18 Environment with Matching Database Schema

This script:
1. Backs up current database
2. Checks out v3.18 code
3. Recreates v3.18 database schema
4. Verifies environment consistency

Usage: python scripts/python/setup_v3.18_environment.py
"""
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(cmd, cwd=None):
    """Run command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def main():
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "p2p_data.db"
    
    print("=" * 70)
    print("Setup v3.18 Environment with Matching Database Schema")
    print("=" * 70)
    
    # Step 1: Backup current database
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = project_root / f"p2p_data_backup_{timestamp}.db"
    
    print(f"\n1. Backing up current database...")
    print(f"   From: {db_path}")
    print(f"   To:   {backup_path}")
    
    if db_path.exists():
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"   [OK] Backup created")
    else:
        print(f"   [INFO] No existing database found")
    
    # Step 2: Get current git branch
    print(f"\n2. Checking current git state...")
    code, stdout, stderr = run_command("git branch --show-current", cwd=project_root)
    current_branch = stdout.strip()
    print(f"   Current branch: {current_branch}")
    
    # Step 3: Checkout v3.18
    print(f"\n3. Checking out v3.18...")
    code, stdout, stderr = run_command("git checkout v3.18", cwd=project_root)
    if code != 0:
        print(f"   [ERROR] {stderr}")
        return 1
    print(f"   [OK] Checked out v3.18")
    
    # Step 4: Recreate v3.18 database schema
    print(f"\n4. Creating v3.18 database schema...")
    
    # Read v3.18 schema SQL
    sql_path = project_root / "sql" / "sqlite" / "create_graph_ontology_tables.sql"
    
    if not sql_path.exists():
        print(f"   [ERROR] Schema file not found at {sql_path}")
        print(f"   [INFO] This may mean v3.18 doesn't have the SQL file in that location")
        return 1
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Drop existing database and recreate
    if db_path.exists():
        db_path.unlink()
        print(f"   [OK] Removed existing database")
    
    conn = sqlite3.connect(str(db_path))
    conn.executescript(sql_script)
    conn.commit()
    
    # Verify tables created
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'graph_%'
        ORDER BY name
    """)
    tables = cursor.fetchall()
    conn.close()
    
    print(f"   [OK] Database recreated with v3.18 schema")
    print(f"\n   Tables created:")
    for table in tables:
        print(f"     - {table[0]}")
    
    # Step 5: Summary
    print(f"\n" + "=" * 70)
    print("Environment Setup Complete!")
    print("=" * 70)
    print(f"\nYou are now on v3.18 with matching database schema")
    print(f"Backup saved to: {backup_path.name}")
    print(f"\nTo return to main branch:")
    print(f"  git checkout {current_branch}")
    print(f"  mv {backup_path.name} p2p_data.db")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())