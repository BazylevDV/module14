from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = '7621891088:AAFbxb5UDSUYg2wFWrR1DQEZgEbkc9kSDmU'

# Создаем класс состояний
class UserState(StatesGroup):
    start = State()
    age = State()
    growth = State()
    weight = State()

# Создаем клавиатуру с кнопками "Рассчитать" и "Информация"
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Рассчитать"), KeyboardButton(text="Информация")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Создаем Inline-клавиатуру
inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")],
    ]
)

# Основная часть программы
if __name__ == '__main__':
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Функция для начала общения
    @dp.message(Command("start"))
    async def start(message: types.Message, state: FSMContext):
        await message.answer(f"Добро пожаловать {message.from_user.username}, ваш слуга - бот посчитает для Вас сейчас оптимальное количество калорий ", reply_markup=start_keyboard)
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
        await message.answer(f"Ваша норма калорий для сохранения веса: {calories_for_weight_maintenance:.2f} ккал в день.")
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