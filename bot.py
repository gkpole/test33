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
            keyboard.add(types.InlineKeyboardButton(text="Подать заявку", callback_data="zaya"))
            await message.answer("Добро пожаловать в гей-тим, подайте заявку для получения билда", reply_markup=keyboard)
        else:
            await message.answer('Вы уже отправили заявку!')
            
    except:
        db1.add_user(message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Подать заявку", callback_data="zaya"))
        await message.answer("Добро пожаловать в гей-тим, подайте заявку для получения билда", reply_markup=keyboard)


@dp.callback_query_handler(text="zaya")
async def send_start(call: types.CallbackQuery):
    await call.message.edit_text('Отправьте ссылку на ваш профиль lolz.guru')
    await Mydialog.otvet.set()
    
@dp.message_handler(state=Mydialog.otvet)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        db1.add_text1(user_message, message.chat.id)
        await state.finish()

    await message.reply('Есть ли у вас опыт? Если да - сколько?')
    await Mydialog1.otvet1.set()
    
@dp.message_handler(state=Mydialog1.otvet1)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['text'] = message.text
        user_message1 = data1['text']
        db1.add_text2(db1.get_text1(message.chat.id), user_message1, message.chat.id)
        await state.finish()
        await Mydialog2.otvet2.set()
        await message.reply('Сколько времени готовы уделять нашему проекту?')
        
@dp.message_handler(state=Mydialog2.otvet2)
async def process_message(message: types.Message, state: FSMContext):
    message.chat.id = int(message.chat.id)
    async with state.proxy() as data2:
        data2['text'] = message.text
        user_message2 = data2['text']
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        db1.add_text3(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message2, message.chat.id)

        await message.reply('Ваша заявка отправлена.')
        await state.finish()
    user_id = int(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    but1 = types.InlineKeyboardButton(text="Принять", callback_data=f"prin_{message.from_user.id}")
    but2 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"otkl_{message.from_user.id}")

    keyboard.add(but1, but2)
    await bot.send_message(chat_id = -1001814890080,
                           text=f'<a href="tg://user?id={message.chat.id}">{message.from_user.first_name}</a> Отправил заявку! Его данные:\nПрофиль lolz.guru - {db1.get_text1(message.chat.id)}\nЕсть ли опыт - {db1.get_text2(message.chat.id), }\nСколько времени готов уделять - {user_message2}',
                           parse_mode='HTML', reply_markup=keyboard)

    
    @dp.callback_query_handler(text_startswith=f"prin_{message.from_user.id}")
    async def send_prin(call: types.CallbackQuery):
        
        
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message2, user_id, 1)
        await bot.send_message(chat_id=user_id, text="тебя приняли, дурак")
        await call.message.delete()

    @dp.callback_query_handler(text_startswith=f"otkl_{message.from_user.id}")
    async def send_otkl(call: types.CallbackQuery):
        user_id = int(call.data.split("_")[1])
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message2, user_id, 2)
        await bot.send_message(chat_id=user_id, text="аххахахахахах пошол нахуй отклонен")
        await call.message.delete()
        
         
        
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
