create_tables = """
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGINT PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    text TEXT
);
CREATE TABLE IF NOT EXISTS refs (
    message_id BIGINT PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    ref_link TEXT NOT NULL,
    ref_cite TEXT NOT NULL
);
"""
delete_redundant_messages = "DELETE FROM messages WHERE chat_id = %s AND message_id NOT IN (SELECT message_id FROM messages WHERE chat_id = %s ORDER BY message_id DESC LIMIT 3)"