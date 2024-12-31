from app import create_app
import os
from dotenv import find_dotenv, load_dotenv

# Load environment variables
env_path = find_dotenv()
load_dotenv(env_path, override=True)

app = create_app()

if __name__ == "__main__":
    app.run(port=5000) 
