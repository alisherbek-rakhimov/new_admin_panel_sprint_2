import os

from dotenv import load_dotenv

env_ready = load_dotenv()

dsn = {
    'dbname': os.environ.get('PG_DB_NAME'),
    'user': os.environ.get('PG_DB_USER'),
    'password': os.environ.get('PG_DB_PASSWORD'),
    'host': os.environ.get('PG_HOST'),
    'port': int(os.environ.get('PG_DB_PORT')),
    'options': f'-c search_path={os.environ.get("PG_DB_SEARCH_PATH")}',
}

db_path = os.path.join(os.getcwd(), os.environ.get('DB_PATH'))