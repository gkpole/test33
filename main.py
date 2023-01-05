from pyrogram import Client, filters, types, idle
from convopyro import Conversation
from convopyro import listen_message
from pyrogram.types import (InlineQueryResultArticle, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
import asyncio
import pyromod

'''
How to get api_id and api_hash?
0. Sign up for Telegram using any application.
1. Log in to your Telegram core: https://my.telegram.org.
2. Go to 'API development tools' and fill out the form.
3. You will get basic addresses as well as the api_id and api_hash parameters required for user authorization.
4. For the moment each number can only have one api_id connected to it.
'''
api_id = 10475996 # put your api_id
api_hash = "59e438d2b2ba12ab84b9c2ae57d624c9" # put your api_hash
api_key = "5485921311:AAFXU90-MQ1O28AkzjwrYwEmeFxX1UaUaWE" # paste your bot token given from @BotFather

with Client("my_account", api_id, api_hash, api_key) as app:
    pass
Conversation(app)

@app.on_message(filters.command("start"))
async def start(_:app, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id,
         text=f"""<b>Здравствуйте!
Мы компания welat VPN </b>""",
            reply_markup=InlineKeyboardMarkup(
                                 [
                                [
                                                                   InlineKeyboardButton('🛡️ | VPN', callback_data='zakaz')
                                    ],[
                                        InlineKeyboardButton('🔺 | Тех. помощь', callback_data='help')
                                   ]]
                            ),)
                            
@app.on_message(filters.command("help"))
async def help(_:app, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id,
         text=f"""<b>🔺 | Контакты тех. помощи </b>""",
             reply_markup=InlineKeyboardMarkup(
                                [
                                [
                                                                   InlineKeyboardButton('🔺 | *контакт*', url='https://t.me/noziss')
                                    ],[
                                        InlineKeyboardButton('🔙 | назад', callback_data='start')
                                   ]]
                            ),)
                            
@app.on_message(filters.command("vpn"))
async def zakaz(_:app, message: types.Message):
    await app.send_message(
        chat_id=message.chat.id,
         text=f"""<b>🛡️| Выберете период: </b>""",
                reply_markup=InlineKeyboardMarkup(
                                 [
                                [
                                                                   InlineKeyboardButton('1 месяц', callback_data='one_months')
                                    ],[
                                        InlineKeyboardButton('3 месяца', callback_data='three_month')
                                    ],[
                                        InlineKeyboardButton('6 месяцев', callback_data='six_month')
                                    ],[
                                        InlineKeyboardButton('1 год', callback_data='year'),
                                    ]]
                            ),)                  
                        
@app.on_message(filters.regex(r'one_month'))
async def one_month(app, CallbackQuery, message):
	button = InlineKeyboardMarkup([[InlineKeyboardButton('❌ | отмена', callback_data = 'stop')]])
	question = await app.send_message(message.chat.id, '✉️ | Введите вашу почту в течение минуты.', reply_markup = button)
	# A nice flow of conversation
	try:
		response = await app.listen.Message(filters.text, id = filters.user(CallbackQuery.from_user.id), timeout = 60)
	except asyncio.TimeoutError:
		await message.reply('Ошибка | Прошло больше минуты.')
	else:
		if response:
			await response.reply(f'Ваша почта: {response.text}')
		else:
			await message.reply('Okay cancelled question!')
	
@app.on_callback_query()
async def button(bot, update):
      cb_data = update.data
      if "one_month" in cb_data:
        await update.message.delete()
        await one_month(bot, update.CallbackQuery)
      elif "zakaz" in cb_data:
        await update.message.delete()
        await zakaz(bot, update.message)
      elif "start" in cb_data:
        await update.message.delete()
        await start(bot, update.message)
	
app.run()
