from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import ParseMode
import os, random
import emotionDetection as ED


def prediction_to_categories(pred):
    if pred <= 1.0:
        return "0-1"
    elif pred >= 3:
        return "3-4"
    return "1-3"


def send_audio(update, context):
    # Fer-ho segons rang de puntuacions
    pred = random.uniform(0.0, 4.0)
    print(pred)
    state = prediction_to_categories(pred)
    song = random.choice(os.listdir("Songs/" + state + "/"))
    context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/" + state + "/" + song, 'rb'), )


def choose_music(update, context):
    entry = ' '.join(context.args)
    states_list = ["rock", "pop", "metal", "jazz", "reggaeton", "techno", "k-pop", "rap", "instrumental", "happy", "sad", "neutral", "angry", "sorrowful", "desgasted", "optimistic"]
    
    if entry in states_list:
        song = random.choice(os.listdir("Songs/" + entry + "/"))
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/" + entry + "/" + song, 'rb'), )


def send_text(update, context):
    # Enviar una frase de manera aleatòria d'entre les que hi ha en un document
    # Fer-ho segons rang de puntuacions
    pred = random.uniform(0.0, 4.0)
    print(pred)
    state = prediction_to_categories(pred)
    with open("Text/" + state) as file:
        sentences = [line.rstrip() for line in file]

    msg = random.choice(sentences)   
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    

def start(update, context):
    """ It begins the interaction with the user."""

    botname = context.bot.first_name
    name = update.effective_chat.first_name
    message_1 = "Hey %s. Welcome to %s. \n" % (name, botname)
    message_2 = " How are you doing today?"
    message_3 = " Please type '/help' to see everything I can do!"
    context.bot.send_message(chat_id=update.effective_chat.id,text=message_1 + message_2 + message_3)


def manage_text(update, context):
    msg = "Te leo"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def manage_audio(update, context):
    file_id = update.message.voice.file_id
    newFile = context.bot.get_file(file_id)
    newFile.download('Audios/' + str(update.effective_chat.id) + '.ogg')
    context.bot.sendMessage(chat_id=update.message.chat_id, text="download succesfull")


def manage_photo(update, context):
    file_id = update.message.photo[-1].file_id
    newFile = context.bot.getFile(file_id)
    path = 'Photos/' + str(update.effective_chat.id) + '.jpg'
    newFile.download(path)
    context.bot.sendMessage(chat_id=update.message.chat_id, text="download succesfull")
    label, probs = ED.get_emotion(path)
    msg_1 = "" + label
    msg_2 = "" + str(probs)
    context.bot.sendMessage(chat_id=update.message.chat_id, text=msg_1+msg_2)



def help(update, context):
    """Action that provides the telegram users with useful and basic information
    about the commands that they can use. """

    msg = "Hi there, WizYu is glad to serve you!\n"
    msg += "..."
    # Comandes possibles
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def main():
    TOKEN = open('token.txt').read().strip()
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('music', send_audio))
    dispatcher.add_handler(CommandHandler('motivation', send_text))
    dispatcher.add_handler(CommandHandler('genre', choose_music))
    dispatcher.add_handler(MessageHandler(Filters.text, manage_text))
    dispatcher.add_handler(MessageHandler(Filters.voice, manage_audio))
    dispatcher.add_handler(MessageHandler(Filters.photo, manage_photo))

    updater.start_polling()


main()