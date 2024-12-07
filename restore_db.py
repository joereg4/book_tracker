import shutil
import os
from datetime import datetime
from glob import glob

def get_latest_backup():
    """Find the most recent backup file"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print(f"Error: Backup directory '{backup_dir}' not found")
        return None
        
    # Get all backup files
    backup_files = glob(os.path.join(backup_dir, "books_backup_*.db"))
    if not backup_files:
        print("Error: No backup files found")
        return None
        
    # Sort by modification time and get the latest
    latest_backup = max(backup_files, key=os.path.getmtime)
    return latest_backup

def restore_database():
    """Restore the database from the latest backup"""
    # Find latest backup
    latest_backup = get_latest_backup()
    if not latest_backup:
        return False
        
    print(f"Found latest backup: {latest_backup}")
    
    # Target database
    target = "books.db"
    
    # Create a backup of the current database just in case
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_backup = f"books_pre_restore_{timestamp}.db"
    current_backup_path = os.path.join("backups", current_backup)
    
    try:
        # Backup current database if it exists
        if os.path.exists(target):
            shutil.copy2(target, current_backup_path)
            print(f"Created safety backup: {current_backup_path}")
        
        # Restore from backup
        shutil.copy2(latest_backup, target)
        print(f"Successfully restored database from: {latest_backup}")
        
    except Exception as e:
        print(f"Error during restore: {str(e)}")
        if os.path.exists(current_backup_path):
            print("Attempting to rollback to safety backup...")
            shutil.copy2(current_backup_path, target)
            print("Rollback successful")
        return False
    
    return True

if __name__ == "__main__":
    if restore_database():
        print("Database restored successfully!")
    else:
        print("Database restore failed!") 