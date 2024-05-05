from config import *
from emojis import *
from WordClass import WordClass
from database_queries import *
import os
import time
from datetime import datetime, time as hora
import telebot
import threading
from telebot.types import  InputTextMessageContent, InputMediaDocument
from telebot.types import  InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultVoice, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telebot.types import ForceReply
from gtts import gTTS

# instanciamos el bot de Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#diccionario principal con los datos de la palabra actual de cada usuario, para que no se convinen
current_words = {}

#variables de paginacion de busquedas
pagination = [] 
num_row = 5
words_all = []

#region === COMANDOS DEL BOT === 
# responde al comando /start
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.reply_to(message, f'''Bienvenido 👋, soy RemindEn tu recordatorio de palabras ✌
Para conocer cómo funciono, envía /help para ayuda''')

# responde al comando /help
@bot.message_handler(commands=["help"])
def cmd_help(message):
    markup = ReplyKeyboardRemove()
    
    mensaje = ('🤖 _¿Qué puedo hacer?:_\n\n'
    '🔍 *Buscar:* Enviame una palabra, si la palabra está registrada la mostraré\\. \n\n'
    '➕ *Registrar:* Si la palabra ingresada no existe, tendrá la opción de registrarla \n\n'
    '   Traducción, Explicación y Ejemplos \n\n'
    '*🔊 Pronunciación:* Cuando envías una palabra tienes la opción de escuchar su pronunciación antes de registrarla\\. \n\n'
    '*📅 Recordatorio:* Cada palabra registrada será recordada en un lapso de 7 días\\. El día y hora serán al azar entre las 8:00 UTC\\-5 y las 22:00 UTC\\-5 \n\n'
    '*🗑 Eliminar:* Busque la palabra a eliminar y haga clic en Eliminar\\.\n\n'
    '*🖊 Editar:* Busque la palabra a editar y haga clic en Editar\\. Posteriormente, seleccione qué quiere editar y siga las instrucciones\\. \n\n'
    '*🧹 Limpiar:* Si limpias este chat, no se eliminarán las palabras registradas anteriormente, y seguirás recibiendo tus recordatorios\\.\n\n'
    '*🛑 Detener recordatorios:* Usa la opción de Stop Bot de Telegram para dejar de recibir mensajes automáticos\\.\n\n')

    # mensaje = escapar_caracteres_especiales(mensaje)
    bot.reply_to(message, mensaje, reply_markup=markup, parse_mode="MarkdownV2")

# responde al comando /all
@bot.message_handler(commands=["all"])
def cmd_mostrartodos(message):
    #Busca todas las palabras registradas
    message_text = escapar_caracteres_especiales(message.text)
    chatId = message.chat.id

    words_all = search_all_words(chatId)
    response = show_all(0,words_all)
    markup = add_pag_buttons()
    resp = bot.send_message(chatId, response, parse_mode="MarkdownV2", reply_markup=markup)
    pagination.append({"pag":0, "message":resp.id, "words":words_all})

#responde a los mensajes de texto
@bot.message_handler(content_types=["text"])
def bot_message_text(message):
    #responder a los mensajes
    # print(message)

    message_text = escapar_caracteres_especiales(message.text)
    chatId = message.chat.id
    global current_words

    print("Message Text: "+message_text)
    #evitamos que manden comandos que no existen en vez de mensajes 
    if message_text and message_text.startswith("/"):
        if message_text == '/cancel':
            cancel(chatId)
        else: 
            bot.send_message(message.chat.id, "¿Ese comando qué?")

    #si es un texto normal es porque debe ser una palabra y la buscamos
    else:
        word_found = search_word(message_text, chatId)

        #Si es None es porque la palabra no existe entonces invitamos a la persona a registrarla
        if word_found == None:

            # Agregamos o editamos la palabra actual del usuario con su chat_id. Porque si está en el current_words, lo va a modificar y si no es como un agregar
            current_words[chatId] = WordClass()
            current_words[chatId].word = message_text

            markup = InlineKeyboardMarkup(row_width = 3)
            btn_registrar = InlineKeyboardButton("➕ Registrar", callback_data="registrar")
            btn_pronunciacion = InlineKeyboardButton("🔊 Pronunciación", callback_data=f"{message_text}")
            btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")
            
            markup.add(btn_registrar,btn_pronunciacion,btn_cancelar)
            bot.reply_to(message, "Palabra no encontrada", reply_markup=markup)

        elif word_found == "error":
            bot.reply_to(message, f"😪 Ups... Error consultando la palabra")

        #Si no es none ni error es porque encontró la palabra entonces procedemos a mostrarla
        else:
            markup = InlineKeyboardMarkup(row_width = 3)
            btn_editar = InlineKeyboardButton(f"🖊 Editar", callback_data="editar")
            btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{word_found.word}")
            btn_eliminar = InlineKeyboardButton(f"🗑 Eliminar", callback_data="eliminar")
            markup.add(btn_editar,btn_pronunciacion,btn_eliminar)

            current_words[chatId] = word_found

            response = format_word(word_found)
            bot.reply_to(message, response, reply_markup=markup, parse_mode="MarkdownV2")
            
        # bot.send_message(message.chat.id, response, parse_mode="MarkdownV2", reply_markup=markup)

#función para manipular los botones inline 
@bot.callback_query_handler(func=lambda x: True)
def inline_buttom(call):
    # print(call)
    chatId = call.from_user.id 
    messageId = call.message.id
    global current_words, pagination, num_row

    #Buscamos el objeto de paginacion del user actual
    pag_user = [objeto for objeto in pagination if objeto["message"] == messageId] 

    if call.data == 'cancelar':
        cancel(chatId)
        #Cuando termine elimino el mensaje    
        bot.delete_message(chatId, messageId)
        return

    elif call.data == 'cerrar':
        pagination = [objeto for objeto in pagination if objeto["message"] != messageId]
        cur_page = 0
        num_row = 5
        words_all = []

        bot.delete_message(chatId, messageId)

    elif call.data == 'siguiente':

        final = 0
        cur_page = 0
        words_all = []

        if pag_user:
            cur_page = pag_user[0]["pag"]
            words_all = pag_user[0]["words"]
            final = len(words_all)

        #Si llegamos hasta aquí, validamos si al sumarle la cantidad de registros no se pasa del len
        last = cur_page + num_row
        if last > final:
            #Si es mayor entonces se pasa, vamos a asignarle la cantidad que le falte
            last = cur_page + (final - cur_page )
        
        if last == final:
          bot.answer_callback_query(call.id, "No hay más resultados")
          return

        cur_page = last
        update_pag(cur_page, messageId, words_all)
        response = show_all(cur_page, words_all)
        markup = add_pag_buttons()
        bot.edit_message_text(response, chatId, messageId, parse_mode="MarkdownV2", reply_markup=markup)

    elif call.data == 'anterior':

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
                
        #Si llegamos hasta aquí, validamos si al sumarle la cantidad de registros no se pasa del len
        first = cur_page - num_row
        if first < 0:
            #Si es menor entonces mostramos la cantidad de resultados faltantes sumandole lo que falte para 0, o sea, el mismo
            first = (first + first)
        
        cur_page = first
        update_pag(cur_page, messageId, words_all)
        response = show_all(cur_page, words_all)
        markup = add_pag_buttons()
        bot.edit_message_text(response, chatId, messageId, parse_mode="MarkdownV2", reply_markup=markup)

    elif call.data == 'editar':
        if chatId in current_words:
            markup = InlineKeyboardMarkup(row_width = 4)
            btn_word = InlineKeyboardButton(f"{emoji_flags[current_words[chatId].lang_word]} Palabra", callback_data="edit_word")
            btn_meaning = InlineKeyboardButton(f"{emoji_flags[current_words[chatId].lang_meaning]} Traducciones", callback_data="edit_meaning")
            btn_explain = InlineKeyboardButton(f"{emoji_explain} Explicación", callback_data="edit_explain")
            btn_example = InlineKeyboardButton(f"{emoji_example} Ejemplos", callback_data="edit_example")

            markup.add(btn_word, btn_meaning, btn_explain, btn_example)

            mensaje = f"*{current_words[chatId].word}*\n¿Qué deseas editar?\n"
            mensaje = escapar_caracteres_especiales(mensaje)

            bot.send_message(chatId, mensaje, parse_mode="MarkdownV2", reply_markup=markup)
            
        else:
            mensaje = '🤔 No hay una palabra actual para editar, consultela nuevamente'
            mensaje = escapar_caracteres_especiales(mensaje)
            bot.send_message(chatId, mensaje)

    elif call.data == 'edit_word':
        #añadimos un markup para los botones inline en el mensaje
        markup = InlineKeyboardMarkup(row_width = 2)
        btn_cancelar = InlineKeyboardButton("Cancelar", callback_data="cancelar")

        markup.add(btn_cancelar)

        mensaje = f"{emoji_flags[current_words[chatId].lang_word]} Ingrese la palabra corregida:"
        mensaje = escapar_caracteres_especiales(mensaje)

        bot.send_message(chatId, mensaje, reply_markup=markup)
        bot.register_next_step_handler(call.message, update_current_word)
        bot.delete_message(chatId, messageId)

    elif call.data == 'edit_meaning':
        #añadimos un markup para los botones inline en el mensaje
        markup = InlineKeyboardMarkup(row_width = 2)
        btn_cancelar = InlineKeyboardButton("Cancelar", callback_data="cancelar")

        markup.add(btn_cancelar)

        mensaje = f"{emoji_flags[current_words[chatId].lang_meaning]} Ingrese la(s) traduccion(es) corregida(s):"

        bot.send_message(chatId, mensaje, reply_markup=markup)
        bot.register_next_step_handler(call.message, update_current_meaning)
        bot.delete_message(chatId, messageId)
        
    elif call.data == 'edit_explain':
        #añadimos un markup para los botones inline en el mensaje
        markup = InlineKeyboardMarkup(row_width = 2)
        btn_cancelar = InlineKeyboardButton("Cancelar", callback_data="cancelar")

        markup.add(btn_cancelar)

        mensaje = f"{emoji_explain} Ingrese la explicación corregida: "

        bot.send_message(chatId, mensaje, reply_markup=markup)
        bot.register_next_step_handler(call.message, update_current_explain)
        bot.delete_message(chatId, messageId)

    elif call.data == 'edit_example':
        #añadimos un markup para los botones inline en el mensaje
        markup = InlineKeyboardMarkup(row_width = 2)
        btn_cancelar = InlineKeyboardButton("Cancelar", callback_data="cancelar")

        markup.add(btn_cancelar)

        mensaje = f"{emoji_example} Ingrese los ejemplos corregidos: "

        bot.send_message(chatId, mensaje, reply_markup=markup)
        bot.register_next_step_handler(call.message, update_current_examples)
        bot.delete_message(chatId, messageId)

    elif call.data == 'eliminar':
        word_id = current_words[chatId].id
        deleted = ''

        if word_id: 
            deleted = delete_word(word_id)
        else:
            bot.send_message(chatId,"🤔 id no encontrado.")
            return 
        
        if deleted == 'success':
            resp = f"🗑 Palabra *{current_words[chatId].word}* eliminada."
            resp = escapar_caracteres_especiales(f"🗑 Palabra *{current_words[chatId].word}* eliminada.")
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")
        else: 
            resp = f'😪 Ups... Error al eliminar la palabra.'
            resp = escapar_caracteres_especiales(resp)
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")

        #Al final elimino el mensaje donde mostraba la palabra salga error o no y limpio el current word
        bot.delete_message(chatId,messageId)
        current_words[chatId] = WordClass()

    # Realiza la inserción en la base de datos usando 'word', 'meaning', 'descripcion' y 'examples'
    elif call.data == 'confirmar':
        try:
            create = query_create_word(current_words[chatId], chatId)
                
            if create == 'success': 
                #añadimos un markup para el boton inline en el mensaje
                markup = InlineKeyboardMarkup(row_width = 2)
                btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{current_words[chatId].word}")
                # btn_pronunciacion = InlineKeyboardButton('🔎 Pesquisar', switch_inline_query_current_chat=f'{current_words[chatId].word}')

                markup.add(btn_pronunciacion)

                response = f'''✅ Palabra guardada exitosamente
                {format_word(current_words[chatId])}'''

                bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode="MarkdownV2", disable_web_page_preview=True)

                # bot.send_message(chatId, "Palabra guardada exitosamente", reply_markup=markup)
            else: 
                bot.send_message(chatId, f"😪 Ups... Error al guardar la palabra.\n\nCausa:`{str(err)}`", reply_markup=markup)

        except Exception as err:
            bot.send_message(chatId, f"😪 Ups... Error al guardar la palabra.\n\nCausa:`{str(err)}`", reply_markup=markup)
            print(err)

        #Cuando termine elimino el mensaje    
        bot.delete_message(chatId, messageId)
    
    elif call.data == 'registrar':
        try:
            bot.delete_message(chatId, messageId)

            mensaje = f"🌎 ¿En qué idioma está esta palabra? "
            mensaje = escapar_caracteres_especiales(mensaje)

            markup = InlineKeyboardMarkup(row_width = 5)
            btn_ingles = InlineKeyboardButton(f"{emoji_flags['EN']}", callback_data="word_EN")
            btn_espanhol = InlineKeyboardButton(f"{emoji_flags['ES']}", callback_data="word_ES")
            btn_portugues = InlineKeyboardButton(f"{emoji_flags['BR']}", callback_data="word_BR")
            btn_frances = InlineKeyboardButton(f"{emoji_flags['FR']}", callback_data="word_FR")
            btn_italiano = InlineKeyboardButton(f"{emoji_flags['IT']}", callback_data="word_IT")
            btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")
            
            markup.add(btn_ingles, btn_espanhol, btn_portugues, btn_frances, btn_italiano, btn_cancelar)

            bot.send_message(call.message.chat.id, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

        except Exception as err:
            prin(err)
            bot.send_message(call.message.chat.id, f"😪 Ups... Se ha presentado un error")

    elif call.data in ['word_EN', 'word_ES', 'word_BR', 'word_FR', 'word_IT']:
        bot.delete_message(chatId, messageId)

        try:
            lang = call.data[-2:] #sacamos las 2 ultimas letras que contienen el codigo del idioma
            current_words[chatId].lang_word = escapar_caracteres_especiales(lang)

            mensaje = f"🌎 Ingrese su(s) traducción(es): "
            mensaje = escapar_caracteres_especiales(mensaje)

            markup = InlineKeyboardMarkup(row_width=2)
            btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

            markup.add(btn_cancelar)

            bot.send_message(chatId, mensaje,parse_mode="MarkdownV2", reply_markup=markup)
            bot.register_next_step_handler(call.message, receive_meaning)

        except Exception as err:
            print(err)
            bot.send_message(chatId, "Se ha presentado un error")

    elif call.data in ['meaning_EN', 'meaning_ES', 'meaning_BR', 'meaning_FR', 'meaning_IT']:
        bot.delete_message(chatId, messageId)

        try:
            # sacamos las 2 ultimas letras que contienen el codigo del idioma
            lang = call.data[-2:]
            current_words[chatId].lang_meaning = escapar_caracteres_especiales(lang)

            mensaje = f"{emoji_explain} Ingresa una breve explicación: "

            markup = InlineKeyboardMarkup(row_width=2)
            btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

            markup.add(btn_cancelar)

            bot.send_message(chatId, mensaje, parse_mode="MarkdownV2", reply_markup=markup)
            bot.register_next_step_handler(call.message, receive_explain)
            

        except Exception as err:
            print(err)
            bot.send_message(chatId, "Se ha presentado un error")

    elif call.data in ['pron_EN', 'pron_ES', 'pron_BR', 'pron_FR', 'pron_IT']:
        # sacamos las 2 ultimas letras que contienen el codigo del idioma
        lang_word = call.data[-2:]
        word = dropEspecialCaracters(current_words[chatId].word)
        send_pronunciation(word, lang_word, chatId, messageId)

    # Si no es ninguno es porque es pronunciacion
    else:
        try:
            word = dropEspecialCaracters(call.data)
            lang_word = ''

            if len(current_words) > 0:
                lang_word = current_words[chatId].lang_word
            
            print(f'Language: {lang_word}')

            if lang_word != '':
                send_pronunciation(word, lang_word, chatId, messageId)
            
            else: 
                #Si no hay palabra es porque quiere escuchar la pronunciacion de una palabra o frase no registrada
                if len(current_words) == 0:
                    current_words[chatId] = WordClass()

                current_words[chatId].word = call.data #Guardamos la palabra provicionalmente

                mensaje = f"🗣️ ¿En qué idioma quieres escuchar?"
                mensaje = escapar_caracteres_especiales(mensaje)

                markup = InlineKeyboardMarkup(row_width=5)
                btn_ingles = InlineKeyboardButton(f"{emoji_flags['EN']}", callback_data="pron_EN")
                btn_espanhol = InlineKeyboardButton(f"{emoji_flags['ES']}", callback_data="pron_ES")
                btn_portugues = InlineKeyboardButton(f"{emoji_flags['BR']}", callback_data="pron_BR")
                btn_frances = InlineKeyboardButton(f"{emoji_flags['FR']}", callback_data="pron_FR")
                btn_italiano = InlineKeyboardButton(f"{emoji_flags['IT']}", callback_data="pron_IT")
                btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

                markup.add(btn_ingles, btn_espanhol, btn_portugues,btn_frances, btn_italiano, btn_cancelar)

                bot.reply_to(call.message, mensaje, parse_mode="MarkdownV2",reply_markup=markup)

        except Exception as err:
            bot.send_message(chatId, f"😪 Ups... Error al reproducir la palabra.\n\n Causa:`{str(err)}`")
            print(err)
        
#endregion 

#region === METODOS DE PASOS DE RECEPCION DE DATOS === 

#funcion para recibir las traducciones
def receive_meaning(message):
    chatId = message.chat.id

    try:
        global current_words
        current_words[chatId].meaning = escapar_caracteres_especiales(message.text)
        
        mensaje = f"🌎 ¿En qué idioma están las traducciones?"
        mensaje = escapar_caracteres_especiales(mensaje)

        markup = InlineKeyboardMarkup(row_width=5)
        btn_ingles = InlineKeyboardButton(f"{emoji_flags['EN']}", callback_data="meaning_EN")
        btn_espanhol = InlineKeyboardButton(f"{emoji_flags['ES']}", callback_data="meaning_ES")
        btn_portugues = InlineKeyboardButton(f"{emoji_flags['BR']}", callback_data="meaning_BR")
        btn_frances = InlineKeyboardButton(f"{emoji_flags['FR']}", callback_data="meaning_FR")
        btn_italiano = InlineKeyboardButton(f"{emoji_flags['IT']}", callback_data="meaning_IT")
        btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

        markup.add(btn_ingles, btn_espanhol, btn_portugues, btn_frances, btn_italiano, btn_cancelar)

        bot.reply_to(message, mensaje, parse_mode="MarkdownV2", reply_markup=markup)

    except Exception as err:
        print(err)
        bot.send_message(message.chat.id, "Se ha presentado un error")

#funcion para recibir la explicación
def receive_explain(message):
    chatId = message.chat.id

    try:
        global current_words
        current_words[chatId].description = escapar_caracteres_especiales(message.text)
        
        mensaje = f"{emoji_example} Ingresa ejemplos de frases con esta palabra: "

        markup = InlineKeyboardMarkup(row_width = 2)
        btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")
        
        markup.add(btn_cancelar)

        bot.send_message(message.chat.id, mensaje, parse_mode="MarkdownV2", reply_markup=markup)
        bot.register_next_step_handler(message, receive_examples)

    except Exception as err:
        print(err)
        bot.send_message(message.chat.id, "Se ha presentado un error")

#funcion para recibir la explicación
def receive_examples(message):
    chatId = message.chat.id

    try:
        global current_words
        current_words[chatId].examples = escapar_caracteres_especiales(message.text)
        
        #añadimos un markup para los botones inline en el mensaje
        markup = InlineKeyboardMarkup(row_width = 2)
        btn_confirmar = InlineKeyboardButton("Confirmar", callback_data="confirmar")
        btn_cancelar = InlineKeyboardButton("Cancelar", callback_data="cancelar")

        markup.add(btn_confirmar, btn_cancelar)

        response = format_word(current_words[chatId])
        bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode="MarkdownV2", disable_web_page_preview=True)

    except Exception as err:
        print(err)
        bot.send_message(message.chat.id, "Se ha presentado un error")

#funcion para cancelar la transacción
def cancel(chat_id):
    #si le da clic en cancelar, limpiamos los pasos porque hay que empezar de nuevo
    global current_words 
    current_words[chat_id] = WordClass()

    bot.send_message(chat_id, "❌ Acción Cancelada")
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)

#endregion 

#region === METODOS DE UPDATE === 
#funcion para editar la propiedad word de la palabra actual del usuario
def update_current_word(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
      cancel(chatId)
      return

    try:
        global current_words
        current_words[chatId].word = escapar_caracteres_especiales(message.text)

        updated = update_word(current_words[chatId])

        if updated == 'success':
            response = f'''🔃 Palabra actualizada exitosamente
            {format_word(current_words[chatId])}'''

            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
            bot.delete_message(chatId, messageId)

        else:
            resp = f'😪 Ups... Error al actualizar la palabra.'
            resp = escapar_caracteres_especiales(resp)
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")
        
    except Exception as err:
        print(err)
        resp = f'😪 Ups... Error al actualizar la palabra.'
        resp = escapar_caracteres_especiales(resp)
            
        bot.send_message(chatId, resp, parse_mode="MarkdownV2")
    
    #eliminamos el penultimo mensaje que es el ultimo del bot
    bot.delete_message(chatId, messageId-1)
    bot.clear_step_handler_by_chat_id(chat_id=chatId)

#funcion para editar la propiedad meaning de la palabra actual del usuario
def update_current_meaning(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
      cancel(chatId)
      return

    try:
        global current_words
        current_words[chatId].meaning = escapar_caracteres_especiales(message.text)

        updated = update_word(current_words[chatId])

        if updated == 'success':
            response = f'''🔃 Palabra actualizada exitosamente
            {format_word(current_words[chatId])}'''

            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
            bot.delete_message(chatId, messageId)

        else:
            resp = f'😪 Ups... Error al actualizar la palabra.'
            resp = escapar_caracteres_especiales(resp)
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")
        
    except Exception as err:
        print(err)
        resp = f'😪 Ups... Error al actualizar la palabra.'
        resp = escapar_caracteres_especiales(resp)
            
        bot.send_message(chatId, resp, parse_mode="MarkdownV2")
    
    #eliminamos el penultimo mensaje que es el ultimo del bot
    bot.delete_message(chatId, messageId-1)
    bot.clear_step_handler_by_chat_id(chat_id=chatId)

#funcion para editar la propiedad description de la palabra actual del usuario
def update_current_explain(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
      cancel(chatId)
      return

    try:
        global current_words
        current_words[chatId].description = escapar_caracteres_especiales(message.text)

        updated = update_word(current_words[chatId])

        if updated == 'success':
            response = f'''🔃 Palabra actualizada exitosamente
            {format_word(current_words[chatId])}'''

            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
            bot.delete_message(chatId, messageId)

        else:
            resp = f'😪 Ups... Error al actualizar la palabra.'
            resp = escapar_caracteres_especiales(resp)
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")
        
    except Exception as err:
        print(err)
        resp = f'😪 Ups... Error al actualizar la palabra.'
        resp = escapar_caracteres_especiales(resp)
            
        bot.send_message(chatId, resp, parse_mode="MarkdownV2")
    
    #eliminamos el penultimo mensaje que es el ultimo del bot
    bot.delete_message(chatId, messageId-1)
    bot.clear_step_handler_by_chat_id(chat_id=chatId)

#funcion para editar la propiedad examples de la palabra actual del usuario
def update_current_examples(message):
    chatId = message.chat.id
    messageId = message.id

    if message.text == '/cancel':
      cancel(chatId)
      return

    try:
        global current_words
        current_words[chatId].examples = escapar_caracteres_especiales(message.text)

        updated = update_word(current_words[chatId])

        if updated == 'success':
            response = f'''🔃 Palabra actualizada exitosamente
            {format_word(current_words[chatId])}'''

            bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
            bot.delete_message(chatId, messageId)

        else:
            resp = f'😪 Ups... Error al actualizar la palabra.'
            resp = escapar_caracteres_especiales(resp)
            
            bot.send_message(chatId, resp, parse_mode="MarkdownV2")
        
    except Exception as err:
        print(err)
        resp = f'😪 Ups... Error al actualizar la palabra.'
        resp = escapar_caracteres_especiales(resp)
            
        bot.send_message(chatId, resp, parse_mode="MarkdownV2")
    
    #eliminamos el penultimo mensaje que es el ultimo del bot
    bot.delete_message(chatId, messageId-1)
    bot.clear_step_handler_by_chat_id(chat_id=chatId)

#endregion 

#region === METODOS DE BUSQUEDA === 
#funcion para consultar las palabras programadas para el día hoy
def search_words_today():
    
    #Esperamos 1 minuto para realizar la siguiente consulta
    time.sleep(60)

    # Obtener la hora actual en formato 00:00 
    hora_actual = hora(datetime.now().time().hour, datetime.now().time().minute)

    # Define la hora mañana (08:00) en horario UTC+0 del servidor
    hora_manhana = hora(HORA_MORNING, 0)

    # Define la hora noche (22:00) en horario UTC+0 del servidor
    hora_noche = hora(HORA_NIGHT,0)

    print(f'hora actual: {hora_actual}')

    if hora_actual == hora_manhana:
        print("Buenos dias")
        bot.send_message(243692305, f"👋 Buenos días, estoy activo ✌")
        return 
    
    if hora_actual == hora_noche:
        print("Buenas noches")
        bot.send_message(243692305, f"😴 Hasta mañana, hoy estuve activo ✌")
        return 

    #Si la hora actual es menor a la hora de la mañana 13 pero es mayor que la noche 3
    #Es porque está entre las 3 y las 13 entonces a esa hora no hacemos nada
    if hora_actual < hora_manhana and hora_actual > hora_noche:
        print("Estoy durmiendo zzz")
        return
    
    #Si llega hasta aquí es porque la hora es mayor que la hora de la mañana o menor que la hora de la noche y ambos casos messirve
    words_now = query_select_words()
    if len(words_now) > 0:
        #Si hay palabras, empezamos a mandarlas a cada usuario
        for word in words_now:
            #añadimos un markup para los botones inline en el mensaje
            chatId = word.chatId
            markup = InlineKeyboardMarkup(row_width = 2)
            btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{word.word}")
            
            markup.add(btn_pronunciacion)

            message = format_word(word)
            current_words[chatId] = WordClass()
            current_words[chatId].word = word.word
            bot.send_message(chatId, message,  parse_mode="MarkdownV2", reply_markup=markup, disable_web_page_preview=True)

            #Reprogramamos la palabra
            updated = query_reschedule_word(word)
    else:
        print("No hay palabras")        
    
#funcion para buscar una sola palabra
def search_word(word, chatId):
    word_found = query_select_word(escapar_caracteres_especiales(word), chatId)
    return word_found

#funcion para buscar todas las palabras del usuario
def search_all_words(chatId):
    words_found = query_select_all(chatId)
    return words_found

#funcion para mapear la respuesta del mostrartodos
def show_all(cur_page=0, listWords=[]):
    global num_row

    response = ''
    i = cur_page
    
    inicio = cur_page
    fin = len(listWords) if cur_page + num_row > len(listWords) else cur_page + num_row

    for word in listWords[inicio:fin]:
        i += 1
        response += f'[{i}]\n{emoji_flags[word.lang_word]} *{word.word}*\n{emoji_flags[word.lang_meaning]} {word.meaning}\n\n'

    header_resp = f'_Resultado *{cur_page+1}* al *{i}* de *{len(listWords)}*_\n'
    return header_resp + response

#funcion para reprogramar palabras que no pudieron ser enviadas
def reschedule_words_earlier():
    #Primero consultamos las palabras vencidas de todos los usuarios
    words_found = query_search_expired_words()
    for word in words_found:
        resp = query_reschedule_word(word)
        print(resp)

#endregion 

#region === METODOS DE UPDATE Y DELETE WORDS === 
#funcion para editar toda la palabra
def update_word(word):
    updated = query_update_word(word)
    return updated

#funcion para eliminar la palabra que el usuario elija eliminar
def delete_word(word_id):
    deleted = query_delete_word(word_id)
    return deleted

#endregion 

#region === METODOS UTILS === 
#funcion para realizar escape de string
def escapar_caracteres_especiales(text):
    caracteres_reservados = r'|!-[]()~`<>.#+={}'
    for char in caracteres_reservados:
        text = text.replace(char, '\\' + char)
    return text

#funcion para eliminar caracteres especiales de una palabra para que no se rompa el nombre del archivo
def dropEspecialCaracters(text):
    caracteres_reservados = r'|?!-[]()~`<>.#+={}¿'
    for char in caracteres_reservados:
        text = text.replace(char, '')
    return text

#funcion para mapear los botones de siguiente, cerrar y anterior para los mensajes de paginacion
def add_pag_buttons():
    markup = InlineKeyboardMarkup(row_width = 3)
    btn_anterior = btn_registrar = InlineKeyboardButton("◀️ Anterior", callback_data="anterior")
    btn_cerrar = btn_registrar = InlineKeyboardButton("❌ Cerrar", callback_data="cerrar")
    btn_siguiente = btn_registrar = InlineKeyboardButton("▶️ Siguiente", callback_data="siguiente")

    markup.row(btn_anterior,btn_cerrar,btn_siguiente)
    return markup

#funcion para actualizar la paginacion de un usuario
def update_pag(pag, messageId, words_all):
    global pagination
    #Es muy dificil buscar y reemplazar en python entonces eliminamos el que tenga el message id y metemos otros con los nuevos datos
    pagination = [objeto for objeto in pagination if objeto["message"] != messageId]
    pagination.append({"pag":pag, "message":messageId, "words":words_all})

# funcion para formatear una palabra y mostrarla siempre de la misma forma
def format_word(word):
    return f'''
{emoji_flags[word.lang_word]} *{word.word}*

{emoji_explain} {word.description}

{emoji_example} {word.examples}

{emoji_flags[word.lang_meaning]} ||{word.meaning}|| '''

#funcion para enviar pronunciacion 
def send_pronunciation(word, lang, chatId, messageId):
    try:
        global current_words
        accents = {
            'EN': 'us',
            'ES': 'es',
            'PT': 'com.br',
            'FR': 'fr',
            'IT': 'it'
        }
        # si es brasileño tenemos que pasarlo a portugues
        lang = 'PT' if lang == 'BR' else lang

        tts = gTTS(text=f' {word}', lang=f'{lang.lower()}', tld=f'{accents[lang]}')
        tts.save(f'{word}.mp3')  # Guarda el archivo de audio

        # Envía el archivo de audio al usuario
        voice_message = open(f'{word}.mp3', 'rb')
        bot.send_voice(chatId, voice_message, reply_to_message_id=messageId)

        # Cierra el archivo después de enviarlo
        voice_message.close()

        # Elimina el archivo del sistema
        os.remove(f'{word}.mp3')

    except Exception as err:
        bot.send_message(chatId, f"😪 Ups... Error al reproducir la palabra.\n\n Causa:`{str(err)}`")
        print(err)
    

    
        

#endregion 

#region === METODOS DE INICIO DEL BOT === 
#funcion para quedarse recibiendo mensajes nuevos
def receive_messages():
    print("Se sigue ejecutando, SIIIU")
    reschedule_words_earlier()
    bot.infinity_polling()

#funcion para iniciar hilo del bot y de consulta de palabras programadas
def iniciar_bot():
    #Creamos un hilo en el sistema para que se quede esperando mensajes pero seguir haciendo cosas en el main
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
 
#endregion 


# === MAIN ===
if __name__ == '__main__':
    print("Bot Iniciado")
    #agregamos los comandos personalizados
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "Iniciar el bot"),
        telebot.types.BotCommand("/help", "Aprender a usar el bot"),
        telebot.types.BotCommand("/all", "Muestra todas las palabras registradas"),
        telebot.types.BotCommand("/cancel", "Cancela la transacción actual")
    ]);

    iniciar_bot()

    #Si llega a aquí es porque la palmó o lo detuvieron
    print("Bot Detenido")
