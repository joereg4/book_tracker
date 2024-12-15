import shutil
from datetime import datetime
import os

def backup_database():
    """Create a timestamped backup of the books database"""
    # Source database
    instance_dir = "instance"
    source = os.path.join(instance_dir, "books.db")
    
    if not os.path.exists(source):
        print(f"Error: Source database not found at {source}")
        return
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = "backups"
    backup_file = f"books_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_file)
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Copy the database file
    try:
        shutil.copy2(source, backup_path)
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
            
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

if __name__ == "__main__":
    backup_database() 