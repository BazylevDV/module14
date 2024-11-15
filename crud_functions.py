import sqlite3

def initiate_db():
    """
    Создает таблицу Products и таблицу Users, если они ещё не созданы.
    """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Создание таблицы Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')

    # Создание таблицы Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def get_all_products():
    """
    Возвращает все записи из таблицы Products.
    """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    conn.close()
    return products

def add_user(username, email, age):
    """
    Добавляет нового пользователя в таблицу Users.
    Баланс у новых пользователей всегда равен 1000.
    """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO Users (username, email, age, balance)
    VALUES (?, ?, ?, 1000)
    ''', (username, email, age))

    conn.commit()
    conn.close()

def is_included(username):
    """
    Проверяет, есть ли пользователь с заданным именем в таблице Users.
    Возвращает True, если пользователь существует, иначе False.
    """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()
    return user is not None
