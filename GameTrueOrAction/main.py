
import telebot
from telebot import types
import random
from random import randrange
import simple_quest # импортируется словарь с вопросами и действиями.

# Это токен бота и словарь, в котором хранится информация об игроках.
bot = telebot.TeleBot('5717076672:AAFH7egwj_hUhozLI07cIzxdGj7DL7vsJn8')
INFO = {}

@bot.message_handler(commands=['start']) 

def start(message):
      """
      Если пользователь отправляет сообщение, начинающееся со слова /start, бот отправит
      пользователю сообщение с текстом :"Привет, (имя пользователя) Это игра правда или действие. Введите количество игроков "
      """
      bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}\nЭто игра правда или действие. Введите количество игроков") 

@bot.message_handler(content_types=['text'])

def NumberOfPlayers(message): 
     """
     Если текст сообщения находится в наборе строк {'2', '3', '4', '5', '6', '7', '8', '9', '10'}, затем
     отправьте сообщение пользователю с текстом "Отлично, вас {message.text} игроков", а затем зарегистрируйтесь
     следующим шагом обработчика должна быть функция GetNamePlayers с аргументами count_players и current_players.
     """
     global INFO
     INFO[message.chat.id] = {'players':{}} # Словарь, в котором хранится информация об игроках.
     if message.text in {'2', '3', '4', '5', '6', '7', '8', '9', '10'}:
         bot.send_message(message.chat.id, f"Отлично, вас {message.text} игроков")
         count_players = int(message.text) # общее количество игроков
         bot.send_message(message.chat.id, f"Введите имя 1 игрока")
         current_players = 1 # текущее количество игроков
         bot.register_next_step_handler(message, GetNamePlayers, count_players, current_players)
     else:
         bot.send_message(message.chat.id, f"К сожалению количество игроков должно быть от 2 до 10. Введите количество игроков заново")

def GetNamePlayers(message, count_players, current_players):
     """ В функции присваиваится имена остальным игрокам"""
     global INFO
     INFO[message.chat.id]['players'][current_players] = {"name_players":message.text , "scope":(0), "answer":[],"action":[]}
     if current_players != count_players:
         bot.send_message(message.chat.id, f"Введите имя {current_players+1} игрока")
         bot.register_next_step_handler(message, GetNamePlayers, count_players, current_players + 1)
         return
     else: 
         """Это цикл, в котором отображаются имена всех игроков."""
         current_players = 1
         start_text = "Игроки:\n"
         while current_players <= len(list(INFO[message.chat.id]['players'].keys())):
                name = INFO[message.chat.id]['players'][current_players].get("name_players")
                start_text += f"{current_players}:{name}\n"
                current_players += 1
         #Это клавиатура, которая появляется, когда пользователь отправляет сообщение.
         markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
         markup.add(telebot.types.KeyboardButton("Начать игру"), telebot.types.KeyboardButton("Занова заполнить"))
         bot.send_message(message.chat.id, start_text.format(message.from_user), reply_markup=markup)
         bot.register_next_step_handler(message, ButtonSelection)
         
def ButtonSelection(message):
     """
     Если пользователь нажимает кнопку "Занова заполнить", функция очищает словарь игроков и
     спрашивает пользователя, сколько в нем игроков. Если пользователь нажимает кнопку "Начать игру", функция
     запускает игру
     """
     if (message.text == "Занова заполнить"):
         INFO[message.chat.id] = {}
         bot.send_message(message.chat.id, f"Сколько вас будет игроков?")
         bot.register_next_step_handler(message, NumberOfPlayers)
         return
     elif (message.text == "Начать игру"):
         INFO[message.chat.id].update(simple_quest.simple_quest.items()) # добавляется к каждому пользователю словари с вопросами и действиями.
         CircularGameCycle(message, 1)
         return

def CircularGameCycle(message,current_players):
     """
     Если количество игроков меньше текущего количества игроков, текущее количество игроков
     имеет значение 1

     :параметр message: сообщение, отправленное пользователем
     :параметр current_players: номер текущего игрока
     """
     if len(list(INFO[message.chat.id]['players'].keys())) < current_players :
          current_players = 1
    # Это клавиатура, которая появляется, когда пользователь отправляет сообщение.
     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
     markup.add(telebot.types.KeyboardButton("Правда"), telebot.types.KeyboardButton("Действие"),telebot.types.KeyboardButton("Остановить"))
     bot.send_message(message.chat.id, f"Что выберет - {INFO[message.chat.id]['players'][current_players].get('name_players')}? Правду или действие?",reply_markup=markup)
     bot.register_next_step_handler(message,ButtonSelectionGame,current_players)

def ButtonSelectionGame(message,current_players):
     """
     :параметр message: сообщение, отправленное пользователем
     :параметр current_players: номер текущего игрока
     """
     # Это клавиатура, которая появляется, когда пользователь отправляет сообщение.
     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
     markup.add(telebot.types.KeyboardButton("Выполнил"), telebot.types.KeyboardButton("Не Выполнил"), telebot.types.KeyboardButton("Остановить") )
     # Это функция, которая случайным образом выбирает действие из словаря и отправляет его пользователю.
     if (message.text == "Правда"):
          key = list(INFO[message.chat.id]['dict_answer'].keys())[randrange(len(list(INFO[message.chat.id]['dict_answer'].keys())))]
          id_quest = 0
          bot.send_message(message.chat.id, f"Вопрос:{INFO[message.chat.id]['dict_answer'][key]}",reply_markup=markup)
          INFO[message.chat.id]['dict_answer'].pop(key)
          bot.register_next_step_handler(message, CheckResultGame,current_players, key, id_quest)

     # Это функция, которая случайным образом выбирает вопрос из словаря и отправляет его пользователю.
     elif (message.text == "Действие"):
          key = list(INFO[message.chat.id]['dict_actions'].keys())[randrange(len(list(INFO[message.chat.id]['dict_actions'].keys())))]
          id_quest = 1
          bot.send_message(message.chat.id, f"Действие: {INFO[message.chat.id]['dict_actions'][key]}",reply_markup=markup)
          INFO[message.chat.id]['dict_actions'].pop(key)
          bot.register_next_step_handler(message, CheckResultGame,current_players, key, id_quest)

    # Это функция, которая вызывается, когда пользователь нажимает кнопку "Остановить".
     elif (message.text == "Остановить"):
           bot.register_next_step_handler(message, ButtonNextOrEnd, current_players)
           
def CheckResultGame(message,current_players, key, id_quest):
     """
     Если пользователь введет "Выполнил" или "Не Выполнил", функция вызовет циклический игровой цикл
     функция, которая позволит продолжить игру

     :параметр message: сообщение, отправленное пользователем
     :параметр current_players: номер текущего игрока
     :параметр key: ключ словаря
     :параметр id_quest: 0 - ответ, 1 - действие
     :возврат: результат игры.
     """
     if message.text == "Выполнил":
          bot.send_message(message.chat.id, f"{INFO[message.chat.id]['players'][current_players].get('name_players')} получает один бал")
          INFO[message.chat.id]['players'][current_players]['scope'] += 1
          if id_quest == 0:
               INFO[message.chat.id]['players'][current_players]['answer'] += key
          else:
               INFO[message.chat.id]['players'][current_players]['action'] += key
          CircularGameCycle(message,current_players + 1 )
          return

     if message.text == "Не Выполнил":
          bot.send_message(message.chat.id, f"{INFO[message.chat.id]['players'][current_players].get('name_players')} не получает бал")
          CircularGameCycle(message,current_players + 1)
          return

     if message.text == "Остановить":
          bot.register_next_step_handler(message, ButtonNextOrEnd, current_players + 1)  
     return

def ButtonNextOrEnd(message, current_players):
     """
     Функция принимает сообщение и переменную current_players, а затем отправляет сообщение пользователю
     с текущими результатами всех игроков. Затем он отправляет пользователю сообщение с вопросом, хочет ли он
     продолжить или завершить игру. Затем он регистрирует обработчик для следующего сообщения, отправляемого пользователем, и
     передает переменную current_players обработчику

     :параметр message: сообщение, отправленное пользователем
     :параметр current_players: количество игроков в игре
     """
     scope_text = f'Счёт:\n'
     current_players = 1
     while current_players <= len(list(INFO[message.chat.id]['players'].keys())):
          name = INFO[message.chat.id]['players'][current_players].get("name_players")
          scope = INFO[message.chat.id]['players'][current_players].get("scope")
          scope_text += f"{name}:{scope}\n"
          current_players += 1
     bot.send_message(message.chat.id, scope_text.format(message.from_user))
     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
     markup.add(telebot.types.KeyboardButton("Продолжить"), telebot.types.KeyboardButton("Закончить игру"))
     bot.send_message(message.chat.id, f"Продолжим игру или закончим?", reply_markup=markup)
     bot.register_next_step_handler(message, NextOrEnd, current_players)

def NextOrEnd(message, current_players):
     """
     Если пользователь нажимает кнопку "Продолжить", игра продолжается, если пользователь нажимает кнопку "Завершить игру"
     кнопка, игра заканчивается.

     :параметр message: сообщение, отправленное пользователем
     :параметр current_players: список игроков
     """
     if message.text == "Продолжить":
          CircularGameCycle(message, current_players)
     if message.text == "Закончить игру":
          message.text = "Занова заполнить"
          ButtonSelection(message)

bot.polling(none_stop=True) # Функция, которая позволяет боту работать без остановки.