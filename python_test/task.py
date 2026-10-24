import os
from datetime import datetime

import psycopg


def test_postgresql_connection():

    with psycopg.connect(
        
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
        
        connect_timeout=5,
        
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT now()")
            result = cursor.fetchone()

    assert result is not None, "Запрос вернул пустой результат "
    assert isinstance(result[0], datetime), "Ожидается datetime"