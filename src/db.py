import psycopg2
from os import getenv
import logging

import migrations

def get_cursor() -> psycopg2.extensions.cursor:
    connection = psycopg2.connect(
            dbname=getenv("POSTGRES_DB"),
            user=getenv("POSTGRES_USER"),
            password=getenv("POSTGRES_PASSWORD"),
            host=getenv("POSTGRES_HOST"),
            port=getenv("POSTGRES_PORT"),
        )
    connection.autocommit = True
    cursor = connection.cursor()
    return cursor
    
def migrate_postgres() -> None:
    """
    Migrate postgres database to latest version
    """
    try:
        logging.info("Migrating postgres database...")
        cursor = get_cursor()
        cursor.execute(migrations.create_tables)
        # logging.info(cursor.fetchall())
        cursor.close()
        logging.info("Postgres database migrated!")
    except Exception as e:
        logging.error(e)

def add_message(message_id: int, chat_id: int, text: str) -> None:
    try:
        cursor = get_cursor()
        cursor.execute("INSERT INTO messages VALUES (%s, %s, %s)", (message_id, chat_id, text))
        cursor.execute("SELECT COUNT(*) from messages WHERE chat_id = %s", (chat_id,))
        if (cursor.fetchone()[0] > 3):
            cursor.execute(migrations.delete_redundant_messages, (chat_id,chat_id))
        cursor.close()
        logging.info("Message added!")
    except Exception as e:
        logging.error("Message add error",e)
