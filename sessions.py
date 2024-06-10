import os
import ast
from langchain_community.utilities import SQLDatabase

import dotenv
dotenv.load_dotenv()

host = os.getenv('POSTGRES_HOST')
port = ast.literal_eval(os.getenv('POSTGRES_PORT'))
user = os.getenv('POSTGRES_USER')
database = os.getenv('POSTGRES_DATABASE')
password = os.getenv('POSTGRES_PASSWORD')
schemaname = os.getenv('POSTGRES_CHATHISTORY_SCHEMANAME')
tablename = ast.literal_eval(os.getenv('POSTGRES_CHATHISTORY_TABLENAME'))

session_db = SQLDatabase.from_uri(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
                          schema=schemaname,
                         sample_rows_in_table_info=0, # default 3
                         include_tables=tablename)

def session_by_id(session_id, user_id=None):
    query = f"SELECT chat_array FROM dev.chat_v4 WHERE session_id='{session_id}';"
    print(query)
    res = ast.literal_eval(session_db.run(query))
    return res
