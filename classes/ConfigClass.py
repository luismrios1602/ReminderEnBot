import os
import argparse
from dotenv import load_dotenv

def getEnv() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--l", action="store_true", help="Usar entorno de localhost")
    parser.add_argument("--c", action="store_true", help="Usar entorno de contabo")
    parser.add_argument("--p", action="store_true", help="Usar entorno de PythonAnywhere")
    args = parser.parse_args()

    # Determinar entorno
    if args.l:
        entorno = "local"
    elif args.c:
        entorno = "contabo"
    elif args.p:
        entorno = "p_anywhere"
    else:
        entorno = "local"  # valor por defecto

    # Cargar el .env correspondiente
    return f".env.{entorno}"

load_dotenv(getEnv()) # Cargar archivo .env.entorno

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

