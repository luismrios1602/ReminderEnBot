from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv() # Cargar archivo .env 

@dataclass
class ConfigClass:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    MY_CHAT_ID: int = int(os.getenv("MY_CHAT_ID", 0))
    
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "") 
    MYSQL_USERNAME: str = os.getenv("MYSQL_USERNAME", "") 
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "")

    HORA_MORNING: int = int(os.getenv("HORA_MORNING", 0))
    HORA_NIGHT: int = int(os.getenv("HORA_NIGHT", 23))