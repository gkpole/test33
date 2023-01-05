import asyncio
import logging
from time import sleep
import os
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.exceptions import Throttled
from aiogram import types
from config import *
from random import *
import db1

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Mydialog(StatesGroup):
    otvet = State()
class Mydialog1(StatesGroup):
    otvet1 = State()
class Mydialog2(StatesGroup):
    otvet2 = State()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    try:
        pon = db1.get_zaya(message.chat.id)
        if pon == None:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="🛡️ | VPN", callback_data="zaya"))
            keyboard2 = types.InlineKeyboardMarkup()

            keyboard.add(types.InlineKeyboardButton(text="🔺 | тех. Помощь", callback_data="help"))
            await message.answer("<b> Здравствуйте!\nМы компания welat VPN </b>", reply_markup=keyboard, keyboard2)
        else:
            await message.answer('Вы уже отправили заявку!')
            
    except:
        db1.add_user(message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Подать заявку", callback_data="zaya"))
        await message.answer("Добро пожаловать в гей-тим, подайте заявку для получения билда", reply_markup=keyboard)

dp.callback_query_handler(text="help")

async def send_help(call: types.CallbackQuery):

    await call.message.edit_text('Ниже отпрвлены контакты:')
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('text', url='https://t.me/NoZiss')
        keyboard.add(button)

@dp.callback_query_handler(text="zaya")
async def send_start(call: types.CallbackQuery):
    await call.message.edit_text('⏳ | Выберете период:')
    button_one_month = KeyboardButton('1 месяц')
    button_three_month = KeyboardButton('3 месяца')
    button_six_month = KeyboardButton('6 месяцев')
    button_year = KeyboardButton('1 гоб')
    
greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_one_month)
greet_kb.add(button_three_month)
greet_kb.add(button_six_month)
greet_kb.add(button_year)
    await Mydialog.otvet.set()
    
@dp.message_handler(state=Mydialog.otvet)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        db1.add_text1(user_message, message.chat.id)
        await state.finish()

    await message.reply('✉️ | Введите вашу почту:')
    await Mydialog1.otvet1.set()
    
@dp.message_handler(state=Mydialog1.otvet1)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['text'] = message.text
        user_message1 = data1['text']
        db1.add_text2(db1.get_text1(message.chat.id), user_message1, message.chat.id)
        await state.finish()
        await Mydialog2.otvet2.set()
        await message.reply('Ваша заявка отправлена.')
        await state.finish()
    user_id = int(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    but1 = types.InlineKeyboardButton(text="Принять", callback_data=f"prin_{message.from_user.id}")
    but2 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"otkl_{message.from_user.id}")

    keyboard.add(but1, but2)
    await bot.send_message(chat_id=admin_used_id,
                           text=f'<a href="tg://user?id={message.chat.id}">{message.from_user.first_name}</a> Отправил заявку! Его данные:\nПериод - {db1.get_text1(message.chat.id)}\nПочта - {db1.get_text2(message.chat.id), }
                           parse_mode='HTML', reply_markup=keyboard)

    
    @dp.callback_query_handler(text_startswith=f"prin_{message.from_user.id}")
    async def send_prin(call: types.CallbackQuery):
        
        
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message2, user_id, 1)
        await bot.send_message(chat_id=user_id, text="Ваш заказ был принят")
        await call.message.delete()

    @dp.callback_query_handler(text_startswith=f"otkl_{message.from_user.id}")
    async def send_otkl(call: types.CallbackQuery):
        user_id = int(call.data.split("_")[1])
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message2, user_id, 2)
        await bot.send_message(chat_id=user_id, text="Ваш заказ отклонили")
        await call.message.delete()
        
         
        
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
