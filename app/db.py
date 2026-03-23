import psycopg2
from psycopg2 import extras
import atexit

DB_CONFIG = {
    'dbname': 'pp05',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': 5432
}

_connection = None

def get_connection():
    """Возвращает или создает соединение с БД"""
    global _connection
    if _connection is None or _connection.closed:
        _connection = psycopg2.connect(**DB_CONFIG)
    return _connection

def close_connection():
    """Закрывает соединение с БД"""
    global _connection
    if _connection and not _connection.closed:
        _connection.close()
    _connection = None

atexit.register(close_connection)

def get_user(login):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur: # DictCursor выводит результат запроса в виде словаря
            cur.execute("SELECT * FROM public.user WHERE login = %s;", (login,))
            return cur.fetchone()

def update_user(login, **kwargs):
    """Обновляет поля пользователя: password, role, is_blocked"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            args = ', '.join(f"{key} = %s" for key in kwargs)
            values = list(kwargs.values()) + [login]
            cur.execute(f"UPDATE public.user SET {args} WHERE login = %s;", values)
            conn.commit()

def add_user(login, password, role='user', blocked='False'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO public.user (login, password, role, blocked)
                VALUES (%s, %s, %s, %s);
            """, (login, password, role, blocked))
            conn.commit()
            return True

def delete_user(login):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.user WHERE login = %s;", (login,))
            conn.commit()

def get_all_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT login, role, blocked FROM public.user;")
            return cur.fetchall()

def reset_failed_attempts(login):
    update_user(login, failed_attempts=0)

def increment_failed_attempts(login):
    user = get_user(login)
    if user and not user['blocked']:
        new_attempts = user['failed_attempts'] + 1
        if new_attempts >= 3:
            update_user(login, blocked=True, failed_attempts=0)
        else:
            update_user(login, failed_attempts=new_attempts)