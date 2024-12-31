from app import create_app
import os
from dotenv import find_dotenv, load_dotenv

# Debug information about environment
print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir())

# Find and load .env file
env_path = find_dotenv()
print("Found .env at:", env_path)
load_dotenv(env_path, override=True, verbose=True)

# Print relevant environment variables
print("Environment after loading:")
print("FLASK_ENV:", os.getenv('FLASK_ENV'))
print("DATABASE_URL:", os.getenv('DATABASE_URL'))

app = create_app()

if __name__ == "__main__":
    app.run() 
