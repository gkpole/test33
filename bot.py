import asyncio
import logging
from time import sleep
import os
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
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

my_channel_id = "ид канала"
channel_us = "ссылка на канал"
#если вам нужно меньше или больше каналов то просто убираете или добавляете

def no_sub():
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Канал 1', url=channel_us)
    urlkb.add(urlButton)
    return urlkb

async def ch_sub(sid):
    statuss = ['creator', 'administrator', 'member']
    x = await bot.get_chat_member(my_channel_id, sid)
    if x.status in statuss:
        return(1)
    else:
        await bot.send_message(sid, "Подпишись на каналы для продолжения", reply_markup=no_sub())

@dp.message_handler(commands="start")
async def start(message: types.Message):
    if await ch_sub(message.chat.id) == 1:
        try:
            pon = db1.get_zaya(message.chat.id)
            if pon == None:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="🛡️ | VPN", callback_data="zaya"))
                keyboard.add(types.InlineKeyboardButton(text="🔺 | Тех. помощь", url="t.me/welat_vpn_collaborator"))
                keyboard.add(types.InlineKeyboardButton(text="📘 | Отзывы", url="t.me/welat_vpn_reviews"))
                await message.answer(f"Здравствуйте! \n Мы компания Welat VPN", reply_markup=keyboard)
            else:
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text="🛡️ | Отправить еще раз", callback_data="zaya"))
                await message.answer('Вы уже отправили заявку!', reply_markup=keyboard)

        except:
            db1.add_user(message.chat.id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="🛡️ | VPN", callback_data="zaya"))
            keyboard.add(types.InlineKeyboardButton(text="🔺 | Тех. помощь", url="t.me/welat_vpn_collaborator"))
            await message.answer(f"Здравствуйте! \n Мы компания Welat VPN", reply_markup=keyboard)

#@dp.callback_query_handler(text="stoimost")
#async def stoimost(call: types.CallbackQuery):
    #keyboard = types.InlineKeyboardMarkup()
    #keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="zaya"))
    #await call.message.answer(f'Стоимость:n\ 1 месяц (3$)n\3 месяца (9$)n\6 месяцев(18$)n\1 год (30$)', reply_markup=keyboard)


@dp.callback_query_handler(text="zaya")
async def send_start(call: types.CallbackQuery):
    kb = [
        [
            types.KeyboardButton(text="1 мес."),
            types.KeyboardButton(text="3 мес."),
            types.KeyboardButton(text="6 мес."),
            types.KeyboardButton(text="1 год"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите срок..."
    )
    await call.message.answer(f'<b>⌛ | Выберете срок:</b> \n\n 💡 | Стоимость: \n 1 месяц (3$) \n 3 месяца (9$) \n 6 месяцев(18$) \n 1 год (30$)', reply_markup=keyboard, parse_mode="html")
    await Mydialog.otvet.set()


@dp.message_handler(state=Mydialog.otvet)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        db1.add_text1(user_message, message.chat.id)
        await state.finish()

    await message.reply('✉️ | Введите вашу почту:', reply_markup=types.ReplyKeyboardRemove())
    await Mydialog1.otvet1.set()


@dp.message_handler(state=Mydialog1.otvet1)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data1:
        data1['text'] = message.text
        user_message1 = data1['text']
        db1.add_text2(db1.get_text1(message.chat.id), user_message1, message.chat.id)
        await state.finish()
        await Mydialog2.otvet2.set()
        await message.reply('📨 | Ваша заявка отправлена на рассмотрение. ')
        await state.finish()
    user_id = int(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    but1 = types.InlineKeyboardButton(text="Принять", callback_data=f"prin_{message.from_user.id}")
    but2 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"otkl_{message.from_user.id}")

    keyboard.add(but1, but2)
    await bot.send_message(chat_id=admin_user_id,
                           text=f'<a href="tg://user?id={message.chat.id}">{message.from_user.first_name}</a> Отправил заявку! Его данные:\nСрок - {db1.get_text1(message.chat.id)}\nПочта - {db1.get_text2(message.chat.id)}',
                           parse_mode='HTML', reply_markup=keyboard)

    @dp.callback_query_handler(text_startswith=f"prin_{message.from_user.id}")
    async def send_prin(call: types.CallbackQuery):
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message1, user_id, 1)
        await bot.send_message(chat_id=user_id, text="✅ | Вашу заявку приняли. Ожидайте ответа.")
        await call.message.edit_text("Сообщил пользователю, что его заявка принята. Ожидает вашего ответа")

    @dp.callback_query_handler(text_startswith=f"otkl_{message.from_user.id}")
    async def send_otkl(call: types.CallbackQuery):
        user_id = int(call.data.split("_")[1])
        db1.add_confirm(db1.get_text1(message.chat.id), db1.get_text2(message.chat.id), user_message1, user_id, 2)
        await bot.send_message(chat_id=user_id, text="🚫 | Вашу заявку отменили")
        await call.message.edit_text("Сообщил пользователю, что его заявка отклонена. Ожидает вашего ответа")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
