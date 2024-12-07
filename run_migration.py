# run_migration.py
from migrations.user_login import upgrade

if __name__ == '__main__':
    upgrade('books.db')