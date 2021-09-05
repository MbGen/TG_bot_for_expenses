from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import CONFIG
from loguru import logger
from os import path, curdir
from typing import Union

from expenses_types import Expenses, ProductExpenses, TransportExpenses, InternetExpenses, TechnicExpenses

from pydantic import ValidationError

bot = Bot(token=CONFIG.get("token"))
dispatcher = Dispatcher(bot, storage=MemoryStorage())

current_directory = path.abspath(curdir)


class ExpensesState(StatesGroup):
    waiting_for_product_amount = State()
    waiting_for_transport_amount = State()
    waiting_for_technic_amount = State()
    waiting_for_internet_amount = State()


class ExpensesBot:
    @staticmethod
    async def info(message: types.Message) -> None:
        await bot.send_message(message.chat.id,
                               "*Этот бот предназначен для учета ваших расходов*",
                               parse_mode="Markdown")

    @staticmethod
    async def start(message: types.Message) -> None:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        information_button = types.KeyboardButton(text="информация")
        add_expense_button = types.KeyboardButton(text="добавить расходы")
        show_expense_button = types.KeyboardButton(text="посмотреть расходы")

        buttons = (
            information_button,
            add_expense_button,
            show_expense_button
        )

        for _, button in enumerate(buttons):
            keyboard.add(button)

        await message.reply("Внизу вы можете увидеть список команд", reply_markup=keyboard)

    @staticmethod
    async def show_expenses_types(message: types.Message) -> None:
        # TODO : добавить в траты "другое"
        keyboard = types.InlineKeyboardMarkup()

        inline_products_expense_button = types.InlineKeyboardButton("Продукты",
                                                                    callback_data="Продукты")
        inline_transport_expense_button = types.InlineKeyboardButton("Транспорт",
                                                                     callback_data="Транспорт")
        inline_technic_expense_button = types.InlineKeyboardButton("Техника",
                                                                   callback_data="Техника")
        inline_internet_expense_button = types.InlineKeyboardButton("Интернет покупки",
                                                                    callback_data="Интернет покупки")
        buttons = (
            inline_products_expense_button,
            inline_transport_expense_button,
            inline_technic_expense_button,
            inline_internet_expense_button
        )

        for _, button in enumerate(buttons):
            keyboard.add(button)

        await message.reply("Выберите тип расхода", reply_markup=keyboard)

    @staticmethod
    async def process_callback_product_expense(callback_query: types.CallbackQuery) -> None:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите количество потраченных денег")
        await ExpensesState.waiting_for_product_amount.set()

    @staticmethod
    async def process_callback_transport_expense(callback_query: types.CallbackQuery) -> None:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите количество потраченных денег")
        await ExpensesState.waiting_for_transport_amount.set()

    @staticmethod
    async def process_callback_technic_expense(callback_query: types.CallbackQuery) -> None:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите количество потраченных денег")
        await ExpensesState.waiting_for_technic_amount.set()

    @staticmethod
    async def process_callback_intenet_expense(callback_query: types.CallbackQuery) -> None:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите количество потраченных денег")
        await ExpensesState.waiting_for_internet_amount.set()

    @staticmethod
    async def add_expense(message: types.Message, state: FSMContext, type_of_expense) -> None:
        try:
            await state.update_data(amount=await ExpensesBot.validate_number(message.text))

        except ValueError:
            await message.reply("Возможно вы ввели не коректные данные, попробуйте еще раз")

        expenses_data = await state.get_data()

        if expenses_data.get("amount") is not None:
            logger.debug(
                {repr(type_of_expense): type_of_expense(amount=expenses_data.get("amount")).json()}
            )
            type_of_expense(amount=expenses_data.get("amount")).save_expenses()

        await state.finish()

    @staticmethod
    async def show_expenses(message: types.Message) -> None:
        expenses = {
            "ProductExpenses": "Продукты",
            "TransportExpenses": "Транспорт",
            "TechnicExpenses": "Техника",
            "InternetExpenses": "Интернет-покупки"
        }
        for _, expense in enumerate(Expenses.get_expenses()):
            await bot.send_message(message.chat.id,
                                   f"_{expenses[expense]}_ -- _{Expenses.get_expenses()[expense]}_",
                                   parse_mode="Markdown")

    @staticmethod
    async def validate_number(number) -> Union[float, Exception]:
        try:
            if "," in number:
                number = number.replace(",", ".")

            return float(number)

        except ValueError:
            raise


@dispatcher.message_handler(commands=["start"])
async def start(message: types.Message) -> None:
    await ExpensesBot.info(message)
    await ExpensesBot.start(message)


@dispatcher.message_handler(regexp="информация")
async def info(message: types.Message) -> None:
    await ExpensesBot.info(message)


@dispatcher.message_handler(regexp="добавить расходы")
async def add_expenses(message: types.Message) -> None:
    await ExpensesBot.show_expenses_types(message)


@dispatcher.message_handler(regexp="посмотреть расходы")
async def show_expenses(message: types.Message) -> None:
    await ExpensesBot.show_expenses(message)


@dispatcher.callback_query_handler(lambda chat: chat.data == "Продукты")
async def process_callback_product_expense(callback_query: types.CallbackQuery) -> None:
    await ExpensesBot.process_callback_product_expense(callback_query)


@dispatcher.callback_query_handler(lambda chat: chat.data == "Транспорт")
async def process_callback_transport_expense(callback_query: types.CallbackQuery) -> None:
    await ExpensesBot.process_callback_transport_expense(callback_query)


@dispatcher.callback_query_handler(lambda chat: chat.data == "Техника")
async def process_callback_technic_expense(callback_query: types.CallbackQuery) -> None:
    await ExpensesBot.process_callback_technic_expense(callback_query)


@dispatcher.callback_query_handler(lambda chat: chat.data == "Интернет покупки")
async def process_callback_intenet_expense(callback_query: types.CallbackQuery) -> None:
    await ExpensesBot.process_callback_intenet_expense(callback_query)


@dispatcher.message_handler(state=ExpensesState.waiting_for_product_amount)
async def add_product_expense(message: types.Message, state: FSMContext) -> None:
    await ExpensesBot.add_expense(message, state, ProductExpenses)


@dispatcher.message_handler(state=ExpensesState.waiting_for_transport_amount)
async def add_product_expense(message: types.Message, state: FSMContext) -> None:
    await ExpensesBot.add_expense(message, state, TransportExpenses)


@dispatcher.message_handler(state=ExpensesState.waiting_for_technic_amount)
async def add_product_expense(message: types.Message, state: FSMContext) -> None:
    await ExpensesBot.add_expense(message, state, TechnicExpenses)


@dispatcher.message_handler(state=ExpensesState.waiting_for_internet_amount)
async def add_product_expense(message: types.Message, state: FSMContext) -> None:
    await ExpensesBot.add_expense(message, state, InternetExpenses)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
