from sqlalchemy import create_engine, text, event, make_url
from sqlalchemy.orm import sessionmaker


sync_engine=None
SessionLocalSync=None

def get_db_url():
    connection_string = "postgresql://postgres:password@localhost:5432"
    url = make_url(connection_string)
    return url

def create_sync_db_engine():
    username = 'postgres'
    password = 'password'
    host = 'localhost'
    port = '5432'
    database = 'vectortutorial'
    schema = 'public'
    table_1 = 'data_experiment_x1_ds'
    table_2 = 'data_experiment_x1_is'
    # Create engine
    return create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')


def set_search_path_sync(dbapi_connection, connection_record):
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path='%s'" % "public")
    cursor.close()
    dbapi_connection.autocommit = existing_autocommit


def get_sync_engine():
    global sync_engine
    if sync_engine is None:
        sync_engine = create_sync_db_engine()
    event.listen(sync_engine, "connect", set_search_path_sync)
    return sync_engine


def get_sync_session_local():
    global SessionLocalSync
    if SessionLocalSync is None:
        SessionLocalSync = sessionmaker(
            autocommit=False, autoflush=False, bind=get_sync_engine()
        )
    return SessionLocalSync