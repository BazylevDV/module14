import sqlite3

# Создаем подключение к базе данных
conn = sqlite3.connect('not_telegram_next.db')
cursor = conn.cursor()

# Удаление пользователя с id=6
cursor.execute('''
DELETE FROM Users WHERE id = 6
''')

# Подсчёт кол-ва всех пользователей
cursor.execute('''
SELECT COUNT(*) FROM Users
''')
total_users = cursor.fetchone()[0]

# Подсчёт суммы всех балансов
cursor.execute('''
SELECT SUM(balance) FROM Users
''')
all_balances = cursor.fetchone()[0]

# Выводим результат в консоль
results = cursor.fetchall()
for row in results:
    print(f'Имя: {row[0]} | Почта: {row[1]} | Возраст: {row[2]} | Баланс: {row[3]}')

# Выводим средний баланс на пользователя
if total_users > 0:
    average_balance = all_balances / total_users
    print(f'Средний баланс на пользователя: {average_balance}')
else:
    print('Нет пользователей в базе данных.')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
