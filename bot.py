import os
import time
import telebot
import threading

from config import *
from modules import main, markups, response_message
from strings import emojis
from utils import utils
from datetime import datetime, time as hora

# instanciamos el bot de Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# variables de paginacion de busquedas
pagination = []
num_row = 5
words_all = []


# region === COMANDOS DEL BOT ===

@bot.message_handler(commands=["test"])
def cmd_test(message):
    lang = main.select_lang_current_user(message.chat.id)
    bot.reply_to(message, response_message.test(lang))

@bot.message_handler(commands=["start"])
def cmd_start(message):
    """responde al comando /start"""
    chatId = message.chat.id
    username = message.from_user.username

    lang = main.select_lang_current_user(chatId)
    bot.reply_to(message, response_message.welcome(username, lang))

@bot.message_handler(commands=["lang"])
def cmd_lang(message):
    """comando para cambiar el idioma del usuario"""
    markup = markups.language_buttons('user')
    bot.send_message(message.chat.id, response_message.question_language_user(), reply_markup=markup)

@bot.message_handler(commands=["help"])
def cmd_help(message):
    """responde al comando /help
    :parameter message propiedades del mensaje"""
    chatId = message.chat.id
    lang = main.select_lang_current_user(chatId)

    markup = markups.remove_keyboard()
    #markup = markups.skip_button()

    mensaje = response_message.help(lang)

    bot.reply_to(message, mensaje, reply_markup=markup, parse_mode="MarkdownV2")


# responde al comando /all
@bot.message_handler(commands=["all"])
def cmd_mostrartodos(message):
    chatId = message.chat.id

    words_found, response = main.search_all_words(chatId)
    words_all = words_found

    markup = markups.pag_buttons()

    resp = bot.send_message(chatId, response, parse_mode="MarkdownV2", reply_markup=markup)

    pagination.append({"pag": 0, "message": resp.id, "words": words_all})


# responde a los mensajes de texto
@bot.message_handler(content_types=["text"])
def bot_message_text(message):
    message_text = utils.escapar_caracteres_especiales(message.text)
    chatId = message.chat.id
    lang_bot = main.select_lang_current_user(chatId)

    print("Message Text: " + message_text)
    # evitamos que manden comandos que no existen en vez de mensajes
    if message_text and message_text.startswith("/"):
        if message_text == '/cancel':
            main.clear_current_word(chatId)
            send_cancel_message(chatId)
        else:
            bot.send_message(message.chat.id, "¿Ese comando qué?")
    else:  # si es un texto normal es porque debe ser una palabra y la buscamos
        word_found, mensaje = main.search_word(chatId, message_text)

        # Si no hubo excepciones es porque la consulta salió correctamente
        markup = None
        if word_found is None:
            markup = markups.word_no_found_buttons(message_text)
        else:
            markup = markups.word_found_buttons(message_text)

        bot.reply_to(message, mensaje, reply_markup=markup, parse_mode="MarkdownV2")


# función para manipular los botones inline
@bot.callback_query_handler(func=lambda x: True)
def inline_buttom(call):
    # print(call)
    chatId = call.from_user.id
    messageId = call.message.id
    global pagination, num_row

    # Buscamos el objeto de paginacion del user actual
    pag_user = [objeto for objeto in pagination if objeto["message"] == messageId]

    if call.data == 'cancelar':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        # Cuando termine elimino el mensaje
        bot.delete_message(chatId, messageId)
        return

    elif call.data == 'pag_cerrar':
        # Limpiamos la lista de palabras de la paginación del mensaje que las mostraba usando una list comprehesion
        pagination = [objeto for objeto in pagination if objeto["message"] != messageId]
        cur_page = 0
        num_row = 5
        words_all = []

        bot.delete_message(chatId, messageId)

    elif call.data == 'pag_siguiente':
        final = 0
        cur_page = 0
        words_all = []

        if pag_user:
            cur_page = pag_user[0]["pag"]
            words_all = pag_user[0]["words"]
            final = len(words_all)

        # Si llegamos hasta aquí, validamos si al sumarle la cantidad de registros no se pasa del len
        last = cur_page + num_row
        print(f'last: {last} | final: {final}')
        if last > final:
            # Si es mayor entonces se pasa, vamos a asignarle la cantidad que le falte
            last = cur_page + (final - cur_page)

        if last == final:
            bot.answer_callback_query(call.id, "No hay más resultados")
            return

        cur_page = last
        pag_update(cur_page, messageId, words_all)
        response = response_message.show_all(cur_page, words_all)
        markup = markups.pag_buttons()
        bot.edit_message_text(response, chatId, messageId, parse_mode="MarkdownV2", reply_markup=markup)

    elif call.data == 'pag_anterior':
        final = 0
        cur_page = 0
        words_all = []

        if pag_user:
            cur_page = pag_user[0]["pag"]
            words_all = pag_user[0]["words"]
            final = len(words_all)

        if cur_page == 0:
            bot.answer_callback_query(call.id, "No hay más resultados")
            return

        # Si llegamos hasta aquí, validamos si al sumarle la cantidad de registros no se pasa del len
        first = cur_page - num_row
        if first < 0:
            # Si es menor entonces mostramos la cantidad de resultados faltantes sumandole lo que falte para 0, o sea, el mismo
            first = (first + first)

        cur_page = first
        pag_update(cur_page, messageId, words_all)
        response = response_message.show_all(cur_page, words_all)
        markup = markups.pag_buttons()
        bot.edit_message_text(response, chatId, messageId, parse_mode="MarkdownV2", reply_markup=markup)

    elif call.data == 'editar':
        current_word_user = main.select_current_word(chatId)
        print(f'Current word: {current_word_user}')

        if current_word_user:
            markup = markups.edit_word_buttons(current_word_user)
            mensaje = response_message.question_edit(current_word_user.word)
            bot.send_message(chatId, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data == 'edit_word':
        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            markup = markups.cancel_button()
            mensaje = response_message.ask_word_edited(current_word_user.lang_word)

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_update_word_current_word)
            bot.delete_message(chatId, messageId)
        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data == 'edit_meaning':
        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            markup = markups.cancel_button()
            mensaje = response_message.ask_meaning_edited(current_word_user.lang_meaning)

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_update_meaning_current_word)
            bot.delete_message(chatId, messageId)
        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data == 'edit_explain':
        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            markup = markups.cancel_button()
            mensaje = response_message.ask_explain_edited()

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_update_explain_current_word)
            bot.delete_message(chatId, messageId)
        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data == 'edit_examples':
        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            markup = markups.cancel_button()
            mensaje = response_message.ask_examples_edited()

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_update_examples_current_word)
            bot.delete_message(chatId, messageId)
        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data == 'eliminar':
        # llamamos al metodo de eliminación de la palabra. Como viene una tupla la descomponemos en exitoso (true o false) y el mensaje
        deleted, resp = main.delete_current_word(chatId)

        if deleted:
            # Al final elimino el mensaje donde mostraba la palabra salga error o no y limpio el current word
            bot.delete_message(chatId, messageId)

        bot.send_message(chatId, resp, parse_mode="MarkdownV2")

    # Realiza la inserción en la base de datos usando 'word', 'meaning', 'descripcion' y 'examples'
    elif call.data == 'confirmar':
        try:
            created, resp, word = main.create_current_word(chatId)

            if not created:
                bot.send_message(chatId, resp)
            else:
                markup = markups.pronunciation_button(word)
                bot.send_message(chatId, resp, reply_markup=markup, parse_mode="MarkdownV2",
                                 disable_web_page_preview=True)

        except Exception as err:
            print(err)
            mensaje = response_message.general_error(err)
            bot.send_message(chatId, mensaje)

        # Cuando termine elimino el mensaje
        bot.delete_message(chatId, messageId)

    elif call.data == 'registrar':
        bot.delete_message(chatId, messageId)

        mensaje = response_message.question_language_register()
        markup = markups.language_buttons(type="word")

        bot.send_message(chatId, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

    elif call.data in ['word_EN', 'word_ES', 'word_BR', 'word_FR', 'word_IT']:
        bot.delete_message(chatId, messageId)

        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            # sacamos las 2 ultimas letras que contienen el codigo del idioma
            lang = call.data[-2:]
            lang = utils.escapar_caracteres_especiales(lang)

            main.register_lang_current_word(chatId, lang)
            markup = markups.cancel_button()
            mensaje = response_message.ask_meaning_register()

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_receive_meaning)

        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data in ['meaning_EN', 'meaning_ES', 'meaning_BR', 'meaning_FR', 'meaning_IT']:
        bot.delete_message(chatId, messageId)

        current_word_user = main.select_current_word(chatId)
        if current_word_user:
            # sacamos las 2 ultimas letras que contienen el codigo del idioma
            lang = call.data[-2:]
            lang = utils.escapar_caracteres_especiales(lang)

            main.register_lang_meaning_current_word(chatId, lang)
            markup = markups.skip_button()
            mensaje = response_message.ask_explain_register()

            bot.send_message(chatId, mensaje, reply_markup=markup)
            bot.register_next_step_handler(call.message, step_receive_explain)

        else:
            mensaje = response_message.no_current_word()
            bot.send_message(chatId, mensaje)

    elif call.data in ['pron_EN', 'pron_ES', 'pron_BR', 'pron_FR', 'pron_IT']:
        # sacamos las 2 ultimas letras que contienen el codigo del idioma
        lang_word = call.data[-2:]
        cur_word = main.select_current_word(chatId)

        if cur_word is None:
            # cur_word = main.assign_current_word(chatId, word)
            pass

        word = utils.dropEspecialCaracters(cur_word.word)

        # Ponemos que responda dos mensajes mas arriba porque el id es el selector de idiomas, 1 es palabra no encontrada y 2 el mensaje del usuario
        send_pronunciation(word, lang_word, chatId, call.message)

        # eliminamos el ultimo mensaje para que no escojan otro idioma
        bot.delete_message(chatId, messageId)
    elif call.data in ['user_EN', 'user_ES', 'user_BR', 'user_FR', 'user_IT']:
        user = call.from_user
        user_selected, message = main.select_user(chatId, user.username)
        if user_selected is None:
            bot.send_message(chat_id=chatId, text=message)

        # Si lo encuentra, mandamos a actualizarle el idioma
        new_lang = call.data[-2:]  # Sacamos las letras del idioma seleccionado

        updated, message = main.update_user_lang(chatId, new_lang)
        bot.send_message(chatId, text=message)

        # eliminamos el ultimo mensaje para que no escojan otro idioma
        bot.delete_message(chatId, messageId)

    elif call.data.split("_")[0] == 'forget':
        id_word = call.data.split("_")[1]
        # Colocamos como palabra actual la palabra que queremos olvidar
        cur_word, mensaje = main.search_word_by_id(chatId, id_word)

        if cur_word is None:
            bot.send_message(chatId, mensaje)
            return

            # Mostramos los botones de tiempo a reprogramar
        markup = markups.forget_period_buttons(id_word)
        mensaje = response_message.question_forget_period(cur_word.word)

        bot.edit_message_reply_markup(chat_id=chatId, message_id=messageId, reply_markup=markup)

    # Verificamos si quiere reprogramar la palabra (el boton envia la cantidad de meses a reprogramar)
    elif call.data.split("_")[0] == 'resche':
        months = call.data.split("_")[1]

        # Primero nos aseguramos que sea un número
        if not months.isnumeric():
            mensaje = response_message.error_months()
            bot.send_message(chatId, mensaje)
            return

            # Sabiendo que es un numero, llamamos al preprogramar para que reprograme la palabra actual
        mensaje = main.reschedule_current_word(chatId, months)
        bot.send_message(chatId, mensaje, parse_mode="MarkdownV2")

        # Al final elimino el mensaje donde mostraba la palabra salga error o no y limpio el current word
        main.clear_current_word(chatId)
        bot.delete_message(chatId, messageId)

    # Verificamos si quiere olvidar la palabra (el boton envia unsche_id)
    elif call.data.split("_")[0] == 'unsche':
        id_word = call.data.split("_")[1]
        mensaje = main.forget_word_by_id(chatId, id_word)

        bot.send_message(chatId, mensaje, parse_mode="MarkdownV2")

        # Al final elimino el mensaje donde mostraba la palabra salga error o no y limpio el current word
        bot.delete_message(chatId, messageId)
        main.clear_current_word(chatId)

    # Si no es ninguno es porque es pronunciacion
    else:
        word = utils.dropEspecialCaracters(call.data)
        send_pronunciation(word, None, chatId, call.message)

        # Después de mandar la pronunciación quitamos los botones inline para que no puedan hacer más nada
        remove_inlinebuttons(chatId, messageId)


# endregion

# region === METODOS DE PASOS DE RECEPCION DE DATOS ===

# funcion para recibir las traducciones
def step_receive_meaning(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    current_word_user = main.select_current_word(chatId)
    if current_word_user:
        # Cuando envie las traducciónes eliminamos el mensaje del bot (-1 porque el id es el que envia el usuario) que pide las traducciones para evitar bugazos
        bot.delete_message(chatId, messageId - 1)

        main.register_meaning_current_word(chatId, message.text)
        markup = markups.language_buttons(type="meaning")
        mensaje = response_message.ask_lang_meaning_register()

        bot.reply_to(message, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

    else:
        mensaje = response_message.no_current_word()
        bot.send_message(chatId, mensaje)


# funcion para recibir la explicación
def step_receive_explain(message):
    messageText = message.text
    chatId = message.chat.id

    if messageText == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    current_word_user = main.select_current_word(chatId)
    if current_word_user:
        if messageText == 'Omitir':
            mensaje = response_message.skiped()
            messageText = ''
        else:
            mensaje = response_message.next_step()

        # Mandamos un mensaje de siguiente (o omitido) como excusa para quitar el boton de omitir por si no omiten
        markup = markups.remove_keyboard()
        bot.send_message(chatId, mensaje, reply_markup=markup)

        main.register_explain_current_word(chatId, messageText)
        markup = markups.skip_button()
        mensaje = response_message.ask_examples_register()

        bot.send_message(message.chat.id, mensaje, parse_mode="MarkdownV2", reply_markup=markup)
        bot.register_next_step_handler(message, step_receive_examples)

    else:
        mensaje = response_message.no_current_word()
        bot.send_message(chatId, mensaje)


# funcion para recibir la explicación
def step_receive_examples(message):
    messageText = message.text
    chatId = message.chat.id
    lang_bot = main.select_lang_current_user(chatId)

    if messageText == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    current_word_user = main.select_current_word(chatId)
    print(f'Palabra a guardar: {current_word_user}')

    if current_word_user:
        if messageText == 'Omitir':
            mensaje = response_message.skiped()
            messageText = ''
        else:
            mensaje = response_message.next_step()

        # Mandamos un mensaje de siguiente (o omitido) como excusa para quitar el boton de omitir por si no omiten
        markup = markups.remove_keyboard()
        bot.send_message(chatId, mensaje, reply_markup=markup)

        main.register_examples_current_word(chatId, messageText)
        markup = markups.confirm_register_buttons()
        mensaje = response_message.format_word(current_word_user, lang_bot)

        bot.send_message(message.chat.id, mensaje, reply_markup=markup, parse_mode="MarkdownV2",
                         disable_web_page_preview=True)

    else:
        mensaje = response_message.no_current_word()
        bot.send_message(chatId, mensaje)


# endregion

# region === METODOS DE PASOS DE RECEPCION DE DATOS PARA UPDATE ===
# funcion para editar la propiedad word de la palabra actual del usuario
def step_update_word_current_word(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    new_word = utils.escapar_caracteres_especiales(message.text)
    objWord, resp = main.update_current_word(chatId, atr='word', new_value=new_word)

    finish_step_update(chatId, messageId, objWord, resp)


# funcion para editar la propiedad meaning de la palabra actual del usuario
def step_update_meaning_current_word(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    new_meaning = utils.escapar_caracteres_especiales(message.text)
    objWord, resp = main.update_current_word(chatId, atr='meaning', new_value=new_meaning)

    finish_step_update(chatId, messageId, objWord, resp)


# funcion para editar la propiedad description de la palabra actual del usuario
def step_update_explain_current_word(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    new_explain = utils.escapar_caracteres_especiales(message.text)
    objWord, resp = main.update_current_word(chatId, atr='description', new_value=new_explain)

    finish_step_update(chatId, messageId, objWord, resp)


# funcion para editar la propiedad examples de la palabra actual del usuario
def step_update_examples_current_word(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
        main.clear_current_word(chatId)
        send_cancel_message(chatId)
        return

    new_examples = utils.escapar_caracteres_especiales(message.text)
    objWord, resp = main.update_current_word(chatId, atr='examples', new_value=new_examples)

    finish_step_update(chatId, messageId, objWord, resp)


# funcion para terminar los step de update de las update
def finish_step_update(chatId, messageId, objWord, response):
    # Si el objeto de la nueva palabra viene None es porque hubo error al actualizar
    if objWord is None:
        bot.send_message(chatId, response, parse_mode="MarkdownV2")

    # Si no es ninguna es porque se guardó bien, entonces procedemos a mandar el mensaje de success
    mensaje = response_message.success_update_word(objWord)
    bot.send_message(chatId, mensaje, parse_mode="MarkdownV2")

    # eliminamos el penultimo mensaje que es el ultimo del bot y limpiamos los pasos del proceso
    bot.delete_message(chatId, messageId - 1)
    bot.clear_step_handler_by_chat_id(chat_id=chatId)
    
# endregion

# region === METODOS DE BUSQUEDA Y PROGRAMACION ===

# funcion para consultar las palabras programadas para el día hoy
def search_words_today():
    # Esperamos 1 minuto para realizar la siguiente consulta
    time.sleep(60)

    # Obtener la hora actual en formato 00:00 
    hora_actual = hora(datetime.now().time().hour, datetime.now().time().minute)

    # Define la hora mañana (08:00) en horario UTC+0 del servidor
    hora_manhana = hora(HORA_MORNING, 0)

    # Define la hora noche (22:00) en horario UTC+0 del servidor
    hora_noche = hora(HORA_NIGHT, 0)

    print(f'hora actual: {hora_actual}')

    if hora_actual == hora_manhana:
        print("Buenos dias")
        bot.send_message(243692305, f"👋 Buenos días, estoy activo ✌")
        return

    if hora_actual == hora_noche:
        print("Buenas noches")
        bot.send_message(243692305, f"😴 Hasta mañana, hoy estuve activo ✌")
        return

        # Si la hora actual es menor a la hora de la mañana 13 pero es mayor que la noche 3
    # Es porque está entre las 3 y las 13 entonces a esa hora no hacemos nada
    if hora_actual < hora_manhana and hora_actual > hora_noche:
        print("Estoy durmiendo zzz")
        return

    # Si llega hasta aquí es porque la hora es mayor que la hora de la mañana o menor que la hora de la noche y ambos casos messirve
    words_now = main.search_scheduled_words()
    if len(words_now) > 0:
        # Si hay palabras, empezamos a mandarlas a cada usuario
        for word in words_now:
            # añadimos un markup para los botones inline en el mensaje
            chatId = word.chatId
            lang_bot = main.select_lang_current_user(chatId)
            markup = markups.word_reminded_buttons(word)

            message = response_message.format_word(word, lang_bot)
            # main.assign_current_word(chatId, word.word)
            bot.send_message(chatId, message, parse_mode="MarkdownV2", reply_markup=markup,
                             disable_web_page_preview=True)

            # Reprogramamos la palabra
            updated = main.reschedule_word(word)
    else:
        print("No hay palabras")


def send_cancel_message(chatId):
    bot.send_message(chatId, "❌ Acción Cancelada")
    bot.clear_step_handler_by_chat_id(chat_id=chatId)


# endregion

# region === METODOS UTILS ===
# funcion para actualizar la paginacion de un usuario
def pag_update(pag, messageId, words_all):
    global pagination
    # Es muy dificil buscar y reemplazar en python entonces eliminamos el que tenga el message id y metemos otros con los nuevos datos
    pagination = [objeto for objeto in pagination if objeto["message"] != messageId]
    pagination.append({"pag": pag, "message": messageId, "words": words_all})


# funcion para enviar pronunciacion. replyTo es el id del mensaje al que se quiere responder (el que tiene la palabra)
def send_pronunciation(word, lang, chatId, message):
    try:
        cur_word = main.select_current_word(chatId)
        if cur_word is None:
            cur_word = main.assign_current_word(chatId, word)
            mensaje = response_message.ask_lang_listening(cur_word.word)
            markup = markups.language_buttons('pron')

            bot.reply_to(message, mensaje, parse_mode="MarkdownV2", reply_markup=markup)
            return

        # Si mandan directamente el idioma es porque quieren escuchar la pronunciacion de una palabra ya elegida
        if lang is not None:
            cur_word.lang_word = lang

        # Validamos si la palabra actual es del usuario tiene un lenguaje.
        if cur_word.lang_word != '':
            name_voice_file, mensaje = main.get_pronunciation(word, cur_word.lang_word)
            print(name_voice_file)

            if name_voice_file is None:
                bot.send_message(chatId, mensaje)
                return

            voice_message = open(name_voice_file, 'rb')
            bot.send_voice(chatId, voice_message, caption=f'{emojis.flags[cur_word.lang_word]} {word}')

            # Cierra el archivo después de enviarlo
            voice_message.close()

            # Elimina el archivo del sistema
            os.remove(name_voice_file)

            # Limpiar la palabra actual
            main.clear_current_word(chatId)

        # Si no tiene un lenguaje es porque o es una palabra sin registrar o están buscando la pronunciación de una palabra programada.
        else:
            # Si no hay lengauje es porque quiere escuchar la pronunciacion de una palabra o frase no registrada
            cur_word = main.assign_current_word(chatId, word)
            mensaje = response_message.ask_lang_listening(cur_word.word)
            markup = markups.language_buttons('pron')

            bot.send_message(chatId, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

    except Exception as err:
        print(err)
        mensaje = response_message.error_playing_word(err)
        bot.send_message(chatId, mensaje)


# funcion para quitar los botones inline de un mensaje
def remove_inlinebuttons(chatId, messageId):
    bot.edit_message_reply_markup(chatId, messageId, reply_markup=None)
    return


# endregion

# region === METODOS DE INICIO DEL BOT ===
# funcion para quedarse recibiendo mensajes nuevos
def receive_messages():
    print("Se sigue ejecutando, SIIIU")
    main.reschedule_words_earlier()
    bot.infinity_polling()


# funcion para iniciar hilo del bot y de consulta de palabras programadas
def iniciar_bot():
    # Creamos un hilo en el sistema para que se quede esperando mensajes pero seguir haciendo cosas en el main
    hilo_bot = threading.Thread(name="hilo_bot", target=receive_messages)
    hilo_bot.start()

    while True:
        try:
            # Iniciar un nuevo hilo para la consulta a la base de datos en cada iteración del bucle
            hilo_consulta_bd = threading.Thread(name="hilo_consulta_bd", target=search_words_today)
            hilo_consulta_bd.start()

            # Esperar a que el hilo de la consulta a la base de datos termine antes de continuar
            hilo_consulta_bd.join()

        except KeyboardInterrupt:
            # Manejar la interrupción del teclado (Ctrl+C) para detener los hilos y salir graciosamente
            bot.stop_polling()
            break


# endregion


# === MAIN ===
if __name__ == '__main__':
    print("Bot Iniciado")
    bot.send_message(MY_CHAT_ID, f"Bot Iniciado en {MYSQL_HOST}")

    # agregamos los comandos personalizados
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Iniciar el bot"),
        telebot.types.BotCommand("/help", "Aprender a usar el bot"),
        telebot.types.BotCommand("/all", "Muestra todas las palabras registradas"),
        telebot.types.BotCommand("/cancel", "Cancela la transacción actual"),
        telebot.types.BotCommand("/lang", "Cambiar el idioma en el que responde el bot")
    ])

    iniciar_bot()

    # Si llega a aquí es porque la palmó o lo detuvieron
    bot.send_message(MY_CHAT_ID, f"Bot en {MYSQL_HOST} Detenido.")
    print("Bot Detenido")
