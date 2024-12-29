import os
import subprocess
from datetime import datetime
from glob import glob
from dotenv import load_dotenv
import gzip

def check_postgres_tools():
    """Check if required PostgreSQL tools are available"""
    try:
        subprocess.run(['psql', '--version'], capture_output=True)
        return True
    except FileNotFoundError:
        print("Error: psql command not found. Please install PostgreSQL command-line tools.")
        print("On macOS: brew install postgresql")
        print("On Ubuntu/Debian: sudo apt-get install postgresql-client")
        return False

def get_latest_backup():
    """Find the most recent backup file"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found")
        return None
        
    # Get all backup files (both compressed and uncompressed)
    backup_files = glob(os.path.join(backup_dir, "books_backup_*.sql*"))
    if not backup_files:
        print("Error: No backup files found")
        return None
        
    # Sort by modification time and get the latest
    latest_backup = max(backup_files, key=os.path.getmtime)
    return latest_backup

def restore_database():
    """Restore the database from the latest backup"""
    if not check_postgres_tools():
        return False
    
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
        pre_restore_backup = os.path.join("backups", f"books_pre_restore_{timestamp}.sql.gz")
        
        backup_command = [
            'pg_dump',
            '--clean',
            '--if-exists',
            '--no-owner',
            '--no-privileges',
            '-Fp',
            db_name
        ]
        
        with gzip.open(pre_restore_backup, 'wt') as f:
            result = subprocess.run(backup_command, env=env, stdout=f, text=True)
        if result.returncode == 0:
            print(f"Created safety backup: {pre_restore_backup}")
        else:
            print(f"Warning: Failed to create safety backup")
        
        # Restore from backup
        if latest_backup.endswith('.gz'):
            # For compressed backups, decompress and pipe to psql
            with gzip.open(latest_backup, 'rt') as f:
                restore_process = subprocess.Popen(
                    ['psql', '-d', db_name],
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = restore_process.communicate(input=f.read())
                result_code = restore_process.returncode
        else:
            # For uncompressed backups, use direct file input
            restore_process = subprocess.run(
                ['psql', '-d', db_name, '-f', latest_backup],
                env=env,
                capture_output=True,
                text=True
            )
            result_code = restore_process.returncode
            stderr = restore_process.stderr
        
        if result_code == 0:
            print(f"Successfully restored database from: {latest_backup}")
            return True
        else:
            print(f"Error during restore: {stderr}")
            print("Attempting to restore from safety backup...")
            
            # Try to restore from safety backup
            with gzip.open(pre_restore_backup, 'rt') as f:
                safety_restore = subprocess.Popen(
                    ['psql', '-d', db_name],
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = safety_restore.communicate(input=f.read())
            
            if safety_restore.returncode == 0:
                print("Successfully restored from safety backup")
            else:
                print(f"Error restoring from safety backup: {stderr}")
            return False
            
    except Exception as e:
        print(f"Error during restore: {str(e)}")
        return False

if __name__ == "__main__":
    if restore_database():
        print("Database restored successfully!")
    else:
        print("Database restore failed!") 