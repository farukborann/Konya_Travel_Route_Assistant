from asyncio.windows_events import NULL
import logging
from math import fabs
from time import sleep
from telegram import *
from telegram.ext import * 
from requests import *
import json
import rotations_algo

#User =>
# user => user chat id - user preferences
def load_users():
    try:
        global users
        file = open('Data/users.json')
        users = json.loads(file.read())
        file.close()
    except FileNotFoundError:
        file = open("data/users.json", "w")
        _json = json.dumps(users)
        file.write(_json)

def save_users():
    file = open("Data/users.json", "w")
    _json = json.dumps(users)
    file.write(_json)

def add_user(user):
    users.append(user)
    save_users()

def set_age(user, age):
    user["age"] = age
    save_users()

def remove_user(user):
    users.remove(user)
    save_users()

def set_user_preferences(user, preference):
    if(preference not in user["preferences"]):
        user["preferences"].append(preference)
    else:
        user["preferences"].remove(preference)
    save_users()
#User End

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup =>
def get_setup_preference_emoji(user, pref):
    if(pref in user["preferences"]):
        return "✔️"
    return "❌"

def get_setup_buttons(user):
    buttons =  [[InlineKeyboardButton("Müzeleri 🏛️" + get_setup_preference_emoji(user, 1), callback_data="preference 1"),  InlineKeyboardButton("Doğal Ortamları 🌳" + get_setup_preference_emoji(user, 2), callback_data="preference 2")], 
            [InlineKeyboardButton("Avmleri 🛒" + get_setup_preference_emoji(user, 3), callback_data="preference 3"), InlineKeyboardButton("Lunaparkları 🎠" + get_setup_preference_emoji(user, 4), callback_data="preference 4")], 
            [InlineKeyboardButton("Tamamdır ✔️", callback_data="finish setup")]]
    return InlineKeyboardMarkup(buttons)

def set_setup_buttons(user, callback_query):
    buttons = get_setup_buttons(user)
    callback_query.edit_message_reply_markup(buttons)

def set_preference(user, callback_query):
    set_user_preferences(user, int(callback_query.data[-1]))
    set_setup_buttons(user, callback_query)

def start_setup(effective_chat, context):
    user = {"id" : effective_chat.id, "preferences" : []}
    add_user(user)
    text = f'Öncelikle hoş geldin {effective_chat.first_name}\nŞimdi sana bir profil oluşturmamız lazım.\nYaşını şu şekilde ayarlayabilirsin => yas 19\nBana biraz kendinden bahset, mesela nereleri gezmekten hoşlanırsın ?'
    buttons = get_setup_buttons(user)
    context.bot.send_message(chat_id=effective_chat.id, text=text, reply_markup=buttons)
# Setup End

#Menu
is_entered = False
def get_menu_buttons():
    buttons = [[InlineKeyboardButton("Profili sıfırla 🔄", callback_data="reset profile")], [InlineKeyboardButton("Rotasyon oluştur 🗺️", callback_data="create rotation")]]
    return InlineKeyboardMarkup(buttons)

def update_location(update: Update, context: CallbackContext):
    user = {}
    for us in users:
        if(us["id"] == update.effective_user.id):
            user = us
            break

    user["current_pos"] = [update.message.location.latitude, update.message.location.longitude]
    text = 'Tamamdır, konumunu kaptım.'
    context.bot.send_message(chat_id=user["id"], text=text)

def get_input(update, context):
    user = {}
    for us in users:
        if(us["id"] == update.effective_user.id):
            user = us
            break
    
    if(update.message.text.startswith("yas")):
        set_age(user,int(update.message.text.split(" ")[1]))
        text = f'Ooo demek {update.message.text.split(" ")[1]} yaşındasın.'
        context.bot.send_message(chat_id=user["id"], text=text)
        return

    val = update.message.text.split(" ")
    user["hour"] = int(val[0])
    user["budget"] = "B"

    text = 'Süreni ve bütçeni kaydettim.'
    context.bot.send_message(chat_id=user["id"], text=text)

def create_rotations(user, context):
    if(user["current_pos"] == NULL):
        text = 'Sana uygun bir şeyler bulmak için konumuna ihtiyacım var, yollayabilir misin ?'
        context.bot.send_message(chat_id=user["id"], text=text)
        return

    context.bot.send_message(chat_id=user["id"], text="Sana en uygun rotayı bulmak için düşünüyorum.. Biraz bekleteceğim :)")
    result = rotations_algo.get_positions(user["current_pos"], user["preferences"], user["hour"] *60, user["budget"])
    user["locations"] = result[0]
    text = f"https://www.google.com/maps/dir/'{user['current_pos'][0]},{user['current_pos'][1]}'/{result[1][0]},{result[1][1]}/"
    buttons = [[InlineKeyboardButton("Devam ➡", callback_data="go next")]]
    buttons = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=user["id"], text=text, reply_markup=buttons)
    
def go_next(user, context):
    text = f"https://www.google.com/maps/dir/'{user['locations']['lat'].iloc[-1]},{user['locations']['long'].iloc[-1]}'/{user['locations']['lat'].iloc[-2]},{user['locations']['long'].iloc[-2]}/"
    user["locations"] = user["locations"][:-1]
    buttons = [[InlineKeyboardButton("Devam ➡", callback_data="go next")]]
    buttons = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=user["id"], text=text, reply_markup=buttons)

def start_menu(user, context):
    text = 'Süreni ve bütçeni şu şekilde girebilirsin => 2 saat 350 tl\nRotasyon belirlemeden önce bunları girmeli ve konumunu yüklemelisin.'
    context.bot.send_message(chat_id=user["id"], text=text)
    text = 'Ne yapmak istersin ?'
    context.bot.send_message(chat_id=user["id"], text=text, reply_markup=get_menu_buttons())
#Menu End

#Start Command
def start(update: Update, context: CallbackContext):
    for user in users:
        if(user["id"] == update.effective_user.id):
            text = f'Tekrar hoş geldin {update.effective_chat.first_name}.'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            start_menu(update.effective_chat, context)
            return

    start_setup(update.effective_chat, context)

#Button Click Events Handler =>
def callBackQuery(update: Update, context: CallbackContext):
    user = {}
    for _user in users:
        if(_user["id"] == update.effective_chat.id):
            user = _user
    if(user == {}):
        logger.warning("Var olmayan kullancı işlem yapmaya çalışıyor!")
        return
    
    if(update.callback_query.data.startswith("preference")):
        set_preference(user, update.callback_query)
    elif(update.callback_query.data == "finish setup"):
        update.callback_query.delete_message()
        start_menu(user, context)
    elif(update.callback_query.data == "reset profile"):
        remove_user(user)
        update.callback_query.delete_message()
        start_setup(update.effective_chat, context)
    elif(update.callback_query.data == "create rotation"):
        create_rotations(user, context)
    elif(update.callback_query.data == "go next"):
        go_next(user, context)

#Other funcs
def echo(update, context):
    update.message.reply_text("Ne dedin anlayamadım :'( Lütfen kontrol eder misin ?")


def error(update, context):
    logger.warning('Update => "%s" Error => "%s"', update, context.error)


def main():
    load_users()

    token = "Your Telegram Token Here"
    updater = Updater(token, use_context=True)

    dp = updater.dispatcher
        
    dp.add_handler(MessageHandler(Filters.location, update_location))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(callBackQuery))
    dp.add_handler(MessageHandler(Filters.text, get_input))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()