import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))

DATABASE_URL = os.environ["DATABASE_URL"]
API_KEY = os.environ["API_KEY"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]