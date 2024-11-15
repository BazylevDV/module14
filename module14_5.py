from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
import asyncio
import os
import logging

# Импортируем функции из crud_functions.py
from crud_functions import initiate_db, get_all_products, add_user, is_included

# Импортируем inline_keyboard из модуля bot.module13_6
from bot.module13_6 import inline_keyboard

API_TOKEN = '7621891088:AAFbxb5UDSUYg2wFWrR1DQEZgEbkc9kSDmU'

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Создаем класс состояний
class UserState(StatesGroup):
    start = State()
    age = State()
    growth = State()
    weight = State()


# Создаем класс состояний для регистрации
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


# Создаем клавиатуру с кнопками "Рассчитать", "Информация", "Купить" и "Регистрация"
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать"), KeyboardButton(text="Информация"), KeyboardButton(text="Купить")],
        [KeyboardButton(text="Регистрация")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создаем Inline-клавиатуру для выбора продуктов
product_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Product1", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product2", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product3", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product4", callback_data="product_buying")],
    ]
)


# Класс CustomInputFile наследуется от InputFile и переопределяет метод read
class CustomInputFile(InputFile):
    def __init__(self, file_data: bytes, filename: str):
        super().__init__(filename)
        self.file_data = file_data
        self.filename = filename

    def read(self, bot=None):
        return self.file_data


# Основная часть программы
if __name__ == '__main__':
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Инициализируем базу данных и получаем все продукты
    initiate_db()
    products = get_all_products()

    # Функция для начала общения
    @dp.message(Command("start"))
    async def start(message: types.Message, state: FSMContext):
        await message.answer(
            f"Добро пожаловать {message.from_user.username}, ваш слуга - бот посчитает для Вас сейчас оптимальное количество калорий ",
            reply_markup=start_keyboard)
        await state.set_state(UserState.start)

    # Функция для обработки нажатия на кнопку "Рассчитать"
    @dp.message(F.text == "Рассчитать", StateFilter(UserState.start))
    async def main_menu(message: types.Message):
        await message.answer("Выберите опцию:", reply_markup=inline_keyboard)

    # Функция для обработки нажатия на кнопку "Информация"
    @dp.message(F.text == "Информация", StateFilter(UserState.start))
    async def show_info(message: types.Message):
        info_text = (
            "Формула Миффлина - Сан Жеора — это одна из наиболее точных формул для расчета суточной нормы калорий. "
            "Она учитывает ваш возраст, рост, вес и пол. "
            "Эта формула была разработана в 1990 году и с тех пор широко используется в диетологии."
        )
        await message.answer(info_text)

    # Функция для обработки нажатия на Inline кнопку "Формулы расчёта"
    @dp.callback_query(lambda call: call.data == "formulas")
    async def get_formulas(call: types.CallbackQuery):
        formula_text = (
            "Формула Миффлина - Сан Жеора для женщин:\n"
            "BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) - 161"
        )
        await call.message.answer(formula_text)
        await call.answer()

    # Функция для обработки нажатия на Inline кнопку "Рассчитать норму калорий"
    @dp.callback_query(lambda call: call.data == "calories")
    async def set_age(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer("Введите свой возраст:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(UserState.age)
        await call.answer()

    # Функция для установки возраста
    @dp.message(StateFilter(UserState.age))
    async def set_age_input(message: types.Message, state: FSMContext):
        await state.update_data(age=int(message.text))
        await message.answer("Введите свой рост в сантиметрах:")
        await state.set_state(UserState.growth)

    # Функция для установки роста
    @dp.message(StateFilter(UserState.growth))
    async def set_growth(message: types.Message, state: FSMContext):
        await state.update_data(growth=int(message.text))
        await message.answer("Введите свой вес в килограммах:")
        await state.set_state(UserState.weight)

    # Функция для установки веса
    @dp.message(StateFilter(UserState.weight))
    async def set_weight(message: types.Message, state: FSMContext):
        await state.update_data(weight=int(message.text))
        data = await state.get_data()
        age = data['age']
        growth = data['growth']
        weight = data['weight']

        # Формула Миффлина - Сан Жеора для женщин
        calories = 10 * weight + 6.25 * growth - 5 * age - 161

        # Норма калорий для похудения (уменьшение на 20%)
        calories_for_weight_loss = calories * 0.8

        # Норма калорий для сохранения веса
        calories_for_weight_maintenance = calories

        await message.answer(f"Ваша норма калорий для похудения: {calories_for_weight_loss:.2f} ккал в день.")
        await message.answer(
            f"Ваша норма калорий для сохранения веса: {calories_for_weight_maintenance:.2f} ккал в день.")
        await state.clear()

    # Функция для обработки нажатия на кнопку "Купить"
    @dp.message(F.text == "Купить", StateFilter(UserState.start))
    async def get_buying_list(message: types.Message):
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем путь к текущему скрипту
        base_path = os.path.join(base_dir, "files")  # Создаем путь к директории с файлами

        # Получаем все продукты из базы данных
        products = get_all_products()

        for product in products:
            product_id, title, description, price = product
            await message.answer(f"Название: {title} | Описание: {description} | Цена: {price}")
            # Отправка картинки продукта
            photo_path = os.path.join(base_path, f"product{product_id}.jpg")  # Создаем путь к файлу изображения
            logging.info(f"Проверка пути к файлу: {photo_path}")
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as file:  # Открываем файл в бинарном режиме
                    photo_data = file.read()  # Читаем данные файла
                    photo = CustomInputFile(photo_data, f"product{product_id}.jpg")
                    await message.answer_photo(photo=photo)  # Отправляем фото пользователю
            else:
                await message.answer(f"Фото для продукта {title} не найдено.")

        await message.answer("Выберите продукт для покупки:",
                             reply_markup=product_keyboard)  # Отправляем сообщение с клавиатурой выбора продукта

    # Функция для обработки нажатия на Inline кнопку "product_buying"
    @dp.callback_query(lambda call: call.data == "product_buying")
    async def send_confirm_message(call: types.CallbackQuery):
        await call.message.answer("Вы успешно приобрели продукт!")
        await call.answer()

    # Функция для обработки нажатия на кнопку "Регистрация"
    @dp.message(F.text == "Регистрация", StateFilter(UserState.start))
    async def sign_up(message: types.Message, state: FSMContext):
        await message.answer("Введите имя пользователя (только латинский алфавит):",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RegistrationState.username)

    # Функция для установки имени пользователя
    @dp.message(StateFilter(RegistrationState.username))
    async def set_username(message: types.Message, state: FSMContext):
        username = message.text
        if is_included(username):
            await message.answer("Пользователь существует, введите другое имя:")
        else:
            await state.update_data(username=username)
            await message.answer("Введите свой email:")
            await state.set_state(RegistrationState.email)

    # Функция для установки email
    @dp.message(StateFilter(RegistrationState.email))
    async def set_email(message: types.Message, state: FSMContext):
        await state.update_data(email=message.text)
        await message.answer("Введите свой возраст:")
        await state.set_state(RegistrationState.age)

    # Функция для установки возраста и завершения регистрации
    @dp.message(StateFilter(RegistrationState.age))
    async def set_age(message: types.Message, state: FSMContext):
        await state.update_data(age=int(message.text))
        data = await state.get_data()
        username = data['username']
        email = data['email']
        age = data['age']

        # Добавляем пользователя в базу данных
        add_user(username, email, age)

        await message.answer("Регистрация успешно завершена!")
        await state.clear()

    # Запуск бота
    async def main():
        try:
            bot_info = await bot.get_me()  # Получаем информацию о боте
            print(f"Бот {bot_info.username} запущен и готов к работе!")
            await dp.start_polling(bot)
        finally:
            await dp.storage.close()
            await bot.session.close()


    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
