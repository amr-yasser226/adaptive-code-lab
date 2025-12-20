import os
from dotenv import load_dotenv

# Load environment variables from .env
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.web.app import create_app

# The app object that Gunicorn will use
app = create_app()

if __name__ == "__main__":
    app.run()
