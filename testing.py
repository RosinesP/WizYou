from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import ParseMode
import os, random
import emotionDetection as ED
from TextModel import predict_text_sentiment

weights = [-0.4, -0.4, -0.4, 0.5, 0.3, -0.4, 0.4]


def choose_state(major_emotion, emotion_probs):

    if max(emotion_probs) > 0.5:
        print(major_emotion)
        return major_emotion
    else:
        result = 0.5
        for i in range(0, 7):
            result += weights[i] * emotion_probs[i]
        print(emotion_probs)
        print(result)
        if result <= 0.0:
            return 0
        elif result >= 1.0:
            return 1
        return result


def prediction_to_categories(pred):
    if pred < 0.35:
        return "negative"
    elif pred > 0.65:
        return "positive"
    return "neutral"


def send_music(update, context):
    if "state" not in context.user_data:
        context.user_data['state'] = False
    
    if context.user_data['state'] is False:
        context.bot.send_message(chat_id=update.effective_chat.id, text="NO STATE -> NEUTRAL SONG")
        song = random.choice(os.listdir("Songs/neutral/"))
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/neutral/" + song, 'rb'), )

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="STATE")
        state = choose_state(context.user_data['major_emotion'], context.user_data['emotion_probs'])
        if isinstance(state, str):
            song = random.choice(os.listdir("Songs/" + state + "/"))
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/" + state + "/" + song, 'rb'), )
        else:
            # numeric
            state = prediction_to_categories(state)
            song = random.choice(os.listdir("Songs/" + state + "/"))
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/" + state + "/" + song, 'rb'), )


def choose_music(update, context):
    entry = ' '.join(context.args)
    states_list = ["positive", "negative", "rock", "pop", "metal", "jazz", "reggaeton", "techno", "k-pop", "rap", "instrumental", "happy", "sad", "neutral", "angry", "disgust", "surprise", "fear"]
    
    if entry in states_list:
        song = random.choice(os.listdir("Songs/" + entry + "/"))
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/" + entry + "/" + song, 'rb'), )


def send_text(update, context):
    if "state" not in context.user_data:
        context.user_data['state'] = False

    if not context.user_data['state']:
        with open("Text/Acudit") as file:
            sentences = [line.rstrip() for line in file]
            msg = random.choice(sentences)
            msgs = msg.split("\\n")
            msg = ""
            for tmp in msgs:
                msg += tmp+"\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    else:
        state = choose_state(context.user_data['major_emotion'], context.user_data['emotion_probs'])
        if isinstance(state, str):
            with open("Text/" + state) as file:
                sentences = [line.rstrip() for line in file]
                msg = random.choice(sentences)
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        else:
            # numeric
            state = prediction_to_categories(state)
            with open("Text/" + state) as file:
                sentences = [line.rstrip() for line in file]
                msg = random.choice(sentences)
                context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    

def start(update, context):
    """ It begins the interaction with the user."""

    botname = context.bot.first_name
    name = update.effective_chat.first_name
    message_1 = "Hey %s!! %s et saluda!! \n" % (name, botname)
    message_2 = "Com t'està anant el dia?\n"
    message_3 = "Pots escriure '/ajuda' per descobrir el que puc fer per tu.\U0001F917 \n"
    context.user_data['state'] = False
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
    context.user_data['major_emotion'] = label
    context.user_data['emotion_probs'] = probs
    context.user_data['state'] = True
    print(probs)
    print(label)


def help(update, context):
    """Action that provides the telegram users with useful and basic information
    about the commands that they can use. """

    if len(context.args) == 0:
        msg =  "Bones \U0001F60A, WizYu està encantat d'acompanyar-te!\n"
        msg += "WitzYu és un sistema que t'ajuda a conèixer les teves emocions, a animar-te i estimar-te.\n\n"
        msg += "1. Si vols conèixer les teves emocions, envia'm un àudio \U0001F399, un text \U0001F4DD o un foto teu d'ara\U0001F933.\n\n"
        msg += "2. Si vols escoltar una cançó segons el gènere o segons el teu estat d'ànim, envia un missatge de: '/genere tipo de gènere/estat emocional', com per exemple: '/genere metal'🎸"
        msg += "o bé '/genere sad' 😕 \n"
        msg += "Pots descobrir totes les opcions amb la comanda /ajuda genere.\n\n"
        msg += "3. Si no tens cap preferència musical en aquests moments, puc triar-te'n una, només has d'enviar un missatge dient: '/musica'.\U0001F3BC \U0001F3B5 \U0001F3B6\n\n"
        msg += "4. Si vols motivar-te un mica, envia un missatge dient: '/motivacio'.\U00002728 \n\n"
        msg += "5. Si vols alguna idea sobre que podries fer, envia un missatge dient: '/activitats'.\U0001F938 \n\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        if context.args[0] == 'musica':
            msg = "Els diferents gèneres o estats d'ànims disponibles son:\n"
            msg += "techno, rock, rap, pop, metal, angry, disgust, fear, happy, negative, neutral, positive, sad i surprise"
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)  

def choose_activity(update, context):
    with open("activitats") as file:
        sentences = [line.rstrip() for line in file]
        msg = random.choice(sentences)
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

def day(update, context):
    if len(context.args) == 0:
        msg = "Epss compte! Després de '/dia' cal que m'expliquis el teu dia! Vull saber com et sents.\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        txt = ' '.join(context.args)
        p = predict_text_sentiment(txt)
        label = prediction_to_categories(p)
        msg = str(label)+"\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
def main():
    TOKEN = open('token.txt').read().strip()
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('inici', start))
    dispatcher.add_handler(CommandHandler('ajuda', help))
    dispatcher.add_handler(CommandHandler('musica', send_music))
    dispatcher.add_handler(CommandHandler('motivacio', send_text))
    dispatcher.add_handler(CommandHandler('genere', choose_music))
    dispatcher.add_handler(CommandHandler('activitats', choose_activity))
    dispatcher.add_handler(CommandHandler('dia', day))
    dispatcher.add_handler(MessageHandler(Filters.text, manage_text))
    dispatcher.add_handler(MessageHandler(Filters.voice, manage_audio))
    dispatcher.add_handler(MessageHandler(Filters.photo, manage_photo))

    updater.start_polling()


main()
