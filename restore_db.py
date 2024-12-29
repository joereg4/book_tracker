import os
import subprocess
from datetime import datetime
from glob import glob
from dotenv import load_dotenv

def get_latest_backup():
    """Find the most recent backup file"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found")
        return None
        
    # Get all backup files
    backup_files = glob(os.path.join(backup_dir, "books_backup_*.sql"))
    if not backup_files:
        print("Error: No backup files found")
        return None
        
    # Sort by modification time and get the latest
    latest_backup = max(backup_files, key=os.path.getmtime)
    return latest_backup

def restore_database():
    """Restore the database from the latest backup"""
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url or not database_url.startswith('postgresql://'):
        print("Error: DATABASE_URL not set or not a PostgreSQL database")
        return False
    
    # Parse database URL for connection info
    try:
        # Remove postgresql:// prefix and split remaining URL
        db_info = database_url.replace('postgresql://', '').split('/')
        db_name = db_info[1]  # Get database name
        connection_info = db_info[0].split('@')
        credentials = connection_info[0].split(':')
        host_info = connection_info[1].split(':')
        
        # Set environment variables for psql
        env = os.environ.copy()
        env['PGUSER'] = credentials[0]
        if len(credentials) > 1:
            env['PGPASSWORD'] = credentials[1]
        env['PGHOST'] = host_info[0]
        if len(host_info) > 1:
            env['PGPORT'] = host_info[1]
        
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {str(e)}")
        return False
    
    # Find latest backup
    latest_backup = get_latest_backup()
    if not latest_backup:
        return False
        
    print(f"Found latest backup: {latest_backup}")
    
    try:
        # Create a backup of the current database first
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = os.path.join("backups", f"books_pre_restore_{timestamp}.sql")
        
        backup_command = [
            'pg_dump',
            '--clean',
            '--if-exists',
            '--no-owner',
            '--no-privileges',
            '-Fp',
            '-f', pre_restore_backup,
            db_name
        ]
        
        result = subprocess.run(backup_command, env=env, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Created safety backup: {pre_restore_backup}")
        else:
            print(f"Warning: Failed to create safety backup: {result.stderr}")
        
        # Restore from backup
        restore_command = [
            'psql',
            '-d', db_name,
            '-f', latest_backup
        ]
        
        result = subprocess.run(restore_command, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully restored database from: {latest_backup}")
            return True
        else:
            print(f"Error during restore: {result.stderr}")
            print("Attempting to restore from safety backup...")
            
            # Try to restore from safety backup
            safety_restore = subprocess.run(
                ['psql', '-d', db_name, '-f', pre_restore_backup],
                env=env, capture_output=True, text=True
            )
            
            if safety_restore.returncode == 0:
                print("Successfully restored from safety backup")
            else:
                print(f"Error restoring from safety backup: {safety_restore.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during restore: {str(e)}")
        return False

if __name__ == "__main__":
    if restore_database():
        print("Database restored successfully!")
    else:
        print("Database restore failed!") 