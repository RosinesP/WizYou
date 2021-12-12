from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import ParseMode
import os, random
import emotionDetection as ED
from TextModel import predict_text_sentiment

weights = [-0.5, -0.4, -0.4, 0.5, 0.3, -0.5, 0.4]


def choose_state(major_emotion, emotion_probs):

    if max(emotion_probs) > 0.7:
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
    if pred < 0.5:
        return "negativitat"
    elif pred > 0.6:
        return "positivitat"
    return "neutralitat"


def send_music(update, context):
    if "state" not in context.user_data:
        context.user_data['state'] = False
    
    if context.user_data['state'] is False:
        song = random.choice(os.listdir("Songs/neutralitat/"))
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open("Songs/neutralitat/" + song, 'rb'), )

    else:
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
    states_list = ["positivitat", "negativitat", "rock", "pop", "metal", "jazz", "reggaeton", "techno", "k-pop", "rap", "instrumental", "alegria", "tristesa", "neutral", "enfadat", "disgust", "sorpresa", "por"]
    
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
            context.bot.send_message(chat_id=update.effective_chat.id, text="Saps aquest acudit?")
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
    msg = "Prova a usar la comanda '/ajuda' per a veure la diferents funcionalitats del bot."
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def manage_photo(update, context):
    file_id = update.message.photo[-1].file_id
    newFile = context.bot.getFile(file_id)
    path = 'Photos/' + str(update.effective_chat.id) + '.jpg'
    newFile.download(path)
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Ja veig com et sents!")
    label, probs = ED.get_emotion(path)
    context.user_data['major_emotion'] = label
    context.user_data['emotion_probs'] = probs
    context.user_data['state'] = True
    print(probs)
    print(label)
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Detecto una certa " + label + ".")


def help(update, context):
    """Action that provides the telegram users with useful and basic information
    about the commands that they can use. """

    if len(context.args) == 0:
        msg =  "Bones \U0001F60A, WizYu està encantat d'acompanyar-te!\n"
        msg += "WitzYu és un sistema que t'ajuda a conèixer les teves emocions, a animar-te i estimar-te.\n\n"
        msg += "1. Si vols conèixer les teves emocions envia'm un text \U0001F4DD amb la comanda '/dia' o un foto teu d'ara\U0001F933.\n\n"
        msg += "2. Si vols escoltar una cançó segons el gènere o segons el teu estat d'ànim, envia un missatge de: '/genere tipus de gènere/estat emocional', com per exemple: '/genere metal'🎸"
        msg += "o bé '/genere tristesa' 😕 \n"
        msg += "Pots descobrir totes les opcions amb la comanda /ajuda musica.\n\n"
        msg += "3. Si no tens cap preferència musical en aquests moments, puc triar-te'n una, només has d'enviar un missatge dient: '/musica'.\U0001F3BC \U0001F3B5 \U0001F3B6\n\n"
        msg += "4. Si vols motivar-te un mica, envia un missatge dient: '/motivacio'.\U00002728 \n\n"
        msg += "5. Si vols alguna idea sobre que podries fer, envia un missatge dient: '/activitats'.\U0001F938 \n\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        if context.args[0] == 'musica':
            msg = "Els diferents gèneres o estats d'ànims disponibles són:\n"
            msg += "techno, rock, rap, pop, metal, enfadat, disgust, por, alegria, negativitat, neutralitat, positivitat, tristesa i sorpresa."
            context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def choose_activity(update, context):
    with open("Text/activitats") as file:
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
        print(p)
        label = prediction_to_categories(p[0])
        print(label)
        context.user_data['major_emotion'] = label
        context.user_data['state'] = True
        if label == "positivitat":
            context.user_data['emotion_probs'] = [0.02, 0.02, 0.02, 0.76, 0.08, 0.02, 0.08]
        elif label == "negativitat":
            context.user_data['emotion_probs'] = [0.25, 0.15, 0.19, 0.02, 0.08, 0.25, 0.08]
        else:
            context.user_data['emotion_probs'] = [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]

        msg = "Detecto una certa " + str(label) + "." + "\n"
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
    dispatcher.add_handler(MessageHandler(Filters.photo, manage_photo))

    updater.start_polling()


main()
