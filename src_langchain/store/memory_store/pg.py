import os
import sys
from typing import List
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import PostgresChatMessageHistory, ConversationBufferMemory

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import MEMORYDB_CONFIG  # pylint: disable=C0413


CONNECT_STR = MEMORYDB_CONFIG.get(
    'connect_str', 'postgresql://ramin:lydacious1@localhost:5432/chat_history')


class MemoryStore:
    '''Memory database APIs: add_history, get_history'''

    def __init__(self, table_name: str, session_id: str):
        '''Initialize memory storage: e.g. history_db'''
        self.table_name = table_name
        self.session_id = session_id

        self.history_db = PostgresChatMessageHistory(
            table_name=self.table_name,
            session_id=self.session_id,
            connection_string=CONNECT_STR,
        )
        self.memory = ConversationBufferMemory(
            memory_key='chat_history',
            chat_memory=self.history_db,
            return_messages=True
        )

    def add_history(self, messages: List[dict]):
        for qa in messages:
            if 'question' in qa:
                self.history_db.add_user_message(qa['question'])
            if 'answer' in qa:
                self.history_db.add_ai_message(qa['answer'])

    def get_history(self):
        records = self.history_db.messages
        messages = []
        for record in records:
            message_data = record[2]  # Assuming 'message' is the third column (index 2)
            if record[1] == "human":  # Assuming 'type' is the second column (index 1)
                messages.append((message_data, None))
            elif record[1] == "ai":   # Assuming 'type' is the second column (index 1)
                messages.append((None, message_data))
        return messages


    @staticmethod
    def connect(connect_str: str = CONNECT_STR):
        import psycopg2  # pylint: disable=C0415

        connection = psycopg2.connect(connect_str)
        cursor = connection.cursor()
        return connection, cursor

    @staticmethod
    def drop(table_name, connect_str: str = CONNECT_STR, session_id: str = None):
        connection, cursor = MemoryStore.connect(connect_str)

        existence = MemoryStore.check(table_name)

        if existence:
            if session_id and len(session_id) > 0:
                query = f'DELETE FROM {table_name} WHERE session_id = %s ;'
                cursor.execute(query, (session_id,))
            else:
                query = f'DROP TABLE {table_name};'
                cursor.execute(query)
            connection.commit()

        if not session_id or len(session_id) == 0:
            existence = MemoryStore.check(table_name)
            assert not existence, f'Failed to drop table {table_name}.'

    @staticmethod
    def check(table_name, connect_str: str = CONNECT_STR):
        _, cursor = MemoryStore.connect(connect_str)

        check = 'SELECT COUNT(*) FROM pg_class WHERE relname = %s;'
        cursor.execute(check, (table_name,))
        record = cursor.fetchall()
        # Assuming record is a tuple containing a single tuple with the count value
        return bool(record[0][0] > 0)

