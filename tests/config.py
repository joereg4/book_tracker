import os
import tempfile

def get_test_db_url():
    """Get test database URL without affecting environment variables"""
    db_fd, db_path = tempfile.mkstemp()
    return db_fd, db_path, f'sqlite:///{db_path}'

def cleanup_test_db(db_fd, db_path):
    """Clean up test database"""
    os.close(db_fd)
    os.unlink(db_path) 