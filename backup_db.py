import os
import subprocess
from datetime import datetime
import shutil
from dotenv import load_dotenv

def backup_database():
    """Create a timestamped backup of the PostgreSQL database"""
    # Load environment variables
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url or not database_url.startswith('postgresql://'):
        print("Error: DATABASE_URL not set or not a PostgreSQL database")
        return
    
    # Parse database URL for connection info
    # Format: postgresql://username:password@hostname:port/dbname
    try:
        # Remove postgresql:// prefix and split remaining URL
        db_info = database_url.replace('postgresql://', '').split('/')
        db_name = db_info[1]  # Get database name
        connection_info = db_info[0].split('@')
        credentials = connection_info[0].split(':')
        host_info = connection_info[1].split(':')
        
        # Set environment variables for pg_dump
        env = os.environ.copy()
        env['PGUSER'] = credentials[0]
        if len(credentials) > 1:
            env['PGPASSWORD'] = credentials[1]
        env['PGHOST'] = host_info[0]
        if len(host_info) > 1:
            env['PGPORT'] = host_info[1]
        
    except Exception as e:
        print(f"Error parsing DATABASE_URL: {str(e)}")
        return
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = "backups"
    backup_file = f"books_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_file)
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        # Create backup using pg_dump
        command = [
            'pg_dump',
            '--clean',  # Clean (drop) database objects before recreating
            '--if-exists',  # Add IF EXISTS to DROP commands
            '--no-owner',  # Don't output commands to set ownership
            '--no-privileges',  # Don't output privileges
            '-Fp',  # Plain-text SQL script
            '-f', backup_path,  # Output file
            db_name  # Database name
        ]
        
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Database backup created successfully: {backup_path}")
            
            # List all backups and their sizes
            backups = sorted(
                [f for f in os.listdir(backup_dir) if f.startswith("books_backup_")],
                reverse=True
            )
            print("\nExisting backups:")
            for backup in backups:
                size_mb = os.path.getsize(os.path.join(backup_dir, backup)) / (1024 * 1024)
                print(f"{backup}: {size_mb:.2f} MB")
                
            # Clean up old backups (keep last 7 days)
            for backup in backups:
                backup_file_path = os.path.join(backup_dir, backup)
                if (datetime.now() - datetime.fromtimestamp(os.path.getctime(backup_file_path))).days > 7:
                    os.remove(backup_file_path)
                    print(f"Removed old backup: {backup}")
        else:
            print(f"Error creating backup: {result.stderr}")
            
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

if __name__ == "__main__":
    backup_database() 