from app import create_app
import os
from dotenv import load_dotenv

print("Before load_dotenv:")
print("ENV FILE PATH:", os.path.abspath('.env'))
print("ENV EXISTS:", os.path.exists('.env'))
print("DATABASE_URL:", os.getenv('SQLALCHEMY_DATABASE_URI'))

load_dotenv('/var/www/book_tracker/.env', verbose=True)

print("After load_dotenv:")
print("DATABASE_URL:", os.getenv('SQLALCHEMY_DATABASE_URI'))

app = create_app()

if __name__ == "__main__":
    app.run() 
