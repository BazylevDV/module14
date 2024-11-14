import sqlite3

def initiate_db():
    """
    Создает таблицу Products, если она ещё не создана.
    """
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
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
