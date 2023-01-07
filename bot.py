import asyncio
import sqlite3
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
ADMIN=admin_id

conn = sqlite3.connect('db2.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id INTEGER,
   block INTEGER);
""")
conn.commit()


class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()


kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
kb.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
kb.add(types.InlineKeyboardButton(text="Статистика"))

class Mydialog(StatesGroup):
    otvet = State()


class Mydialog1(StatesGroup):
    otvet1 = State()


class Mydialog2(StatesGroup):
    otvet2 = State()

my_channel_id=sub_channel_id
channel_us=sub_channel_url
#если вам нужно меньше или больше каналов то просто убираете или добавляете

def no_sub():
    urlkb = InlineKeyboardMarkup(row_width=1)
    urlButton = InlineKeyboardButton(text='Welat VPN', url=channel_us)
    urlkb.add(urlButton)
    return urlkb

async def ch_sub(sid):
    statuss = ['creator', 'administrator', 'member']
    x = await bot.get_chat_member(my_channel_id, sid)
    if x.status in statuss:
        return(1)
    else:
        await bot.send_message(sid, "🗨️ | Подпишись на каналы для продолжения", reply_markup=no_sub())


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    cur = conn.cursor()
    cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
    result = cur.fetchone()
    if message.from_user.id == ADMIN:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Статистика"))
        await message.answer('Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=kb)

@dp.message_handler(commands="start")
async def start(message: types.Message):
    if await ch_sub(message.chat.id) == 1:
        cur = conn.cursor()
        cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
        result = cur.fetchone()
        if result is None:
            cur = conn.cursor()
            cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
            entry = cur.fetchone()
            if entry is None:
                cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}', '0')''')
                conn.commit()
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
                    keyboard.add(types.InlineKeyboardButton(text="📘 | Отзывы", url="t.me/welat_vpn_reviews"))
                    await message.answer(f"Здравствуйте! \n Мы компания Welat VPN", reply_markup=keyboard)
        else:
            await message.answer('Ты был заблокирован!')

@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: types.Message):
    if message.from_user.id == ADMIN:
        await dialog.spam.set()
        await message.answer('Напиши текст рассылки')
    else:
        await message.answer('Вы не являетесь админом')


@dp.message_handler(state=dialog.spam)
async def start_spam(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Статистика"))
        await message.answer('Главное меню', reply_markup=keyboard)
        await state.finish()
    else:
        cur = conn.cursor()
        cur.execute(f'''SELECT user_id FROM users''')
        spam_base = cur.fetchall()
        print(spam_base)
        for z in range(len(spam_base)):
            print(spam_base[z][0])
        for z in range(len(spam_base)):
            await bot.send_message(spam_base[z][0], message.text)
        await message.answer('Рассылка завершена')
        await state.finish()


@dp.message_handler(state='*', text='Назад')
async def back(message: types.Message):
    if message.from_user.id == ADMIN:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Статистика"))
        await message.answer('Главное меню', reply_markup=keyboard)
    else:
        await message.answer('Вам не доступна эта функция')


@dp.message_handler(content_types=['text'], text='Добавить в ЧС')
async def hanadler(message: types.Message, state: FSMContext):
    if message.chat.id == ADMIN:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Назад"))
        await message.answer(
            'Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку ниже',
            reply_markup=keyboard)
        await dialog.blacklist.set()


@dp.message_handler(state=dialog.blacklist)
async def proce(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Статистика"))
        await message.answer('Отмена! Возвращаю назад.', reply_markup=keyboard)
        await state.finish()
    else:
        if message.text.isdigit():
            cur = conn.cursor()
            cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
            result = cur.fetchall()
            # conn.commit()
            if len(result) == 0:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
                await state.finish()
            else:
                a = result[0]
                id = a[0]
                if id == 0:
                    cur.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
                    conn.commit()
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                    await message.answer('Пользователь успешно добавлен в ЧС.', reply_markup=keyboard)
                    await state.finish()
                    await bot.send_message(message.text, 'Ты получил БАН от администрации.')
                else:
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                    await message.answer('Данный пользователь уже получил бан', reply_markup=keyboard)
                    await state.finish()
        else:
            await message.answer('Ты вводишь буквы...\n\nВведи ID')


@dp.message_handler(content_types=['text'], text='Убрать из ЧС')
async def hfandler(message: types.Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
    result = cur.fetchone()
    if result is None:
        if message.chat.id == ADMIN:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.InlineKeyboardButton(text="Назад"))
            await message.answer(
                'Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже',
                reply_markup=keyboard)
            await dialog.whitelist.set()


@dp.message_handler(state=dialog.whitelist)
async def proc(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
        keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
        keyboard.add(types.InlineKeyboardButton(text="Статистика"))
        await message.answer('Отмена! Возвращаю назад.', reply_markup=keyboard)
        await state.finish()
    else:
        if message.text.isdigit():
            cur = conn.cursor()
            cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
            result = cur.fetchall()
            conn.commit()
            if len(result) == 0:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
                await state.finish()
            else:
                a = result[0]
                id = a[0]
                if id == 1:
                    cur = conn.cursor()
                    cur.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
                    conn.commit()
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                    await message.answer('Пользователь успешно разбанен.', reply_markup=keyboard)
                    await state.finish()
                    await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
                else:
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
                    keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
                    keyboard.add(types.InlineKeyboardButton(text="Статистика"))
                    await message.answer('Данный пользователь не получал бан.', reply_markup=keyboard)
                    await state.finish()
        else:
            await message.answer('Ты вводишь буквы...\n\nВведи ID')

@dp.message_handler(content_types=['text'], text='Статистика')
async def hfandler(message: types.Message, state: FSMContext):
    cur = conn.cursor()
    cur.execute('''select * from users''')
    results = cur.fetchall()
    await message.answer(f'Людей которые когда либо заходили в бота: {len(results)}')

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
