import shutil
from datetime import datetime
import os

def backup_database():
    """Create a timestamped backup of the books database"""
    # Source database
    source = "books.db"
    
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
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

if __name__ == "__main__":
    backup_database() 