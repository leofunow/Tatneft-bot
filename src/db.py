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


def add_message(message_id: int, chat_id: int, text: str, context) -> None:
    try:
        cursor = get_cursor()
        cursor.execute("INSERT INTO messages VALUES (%s, %s, %s)",
                       (message_id, chat_id, text))
        cursor.execute(
            "SELECT COUNT(*) from messages WHERE chat_id = %s", (chat_id,))
        if (cursor.fetchone()[0] > 3):
            cursor.execute(migrations.delete_redundant_messages,
                           (chat_id, chat_id))
        logging.info("Message added!")
        for i in context:
            cursor.execute("INSERT INTO refs VALUES (%s, %s, %s, %s)",
                           (message_id, chat_id, i.metadata['link'], i.page_content))
        cursor.close()
    except Exception as e:
        logging.error("Message add error", e)

def get_ref(message_id: int, chat_id: int, n):
    cursor = get_cursor()
    print(str(message_id) + " " + str(chat_id) + " " + str(n), flush=True)
    cursor.execute("SELECT ref_cite, ref_link FROM refs WHERE message_id = %s AND chat_id = %s OFFSET %s LIMIT 1", (message_id, chat_id, n - 1))
    return cursor.fetchone()

