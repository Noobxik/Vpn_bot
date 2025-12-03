import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '8435774037:AAFVncIwpCYkS8bqncS4iJlxzY7y19jyu6E')

ADMIN_ID = int(os.getenv('ADMIN_ID', '738364860'))  

SECRETS_FILE = 'secrets.json'
LOG_FILE = 'bot.log'
