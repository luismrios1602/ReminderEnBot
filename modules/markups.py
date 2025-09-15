from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from strings import emojis

# funcion para mapear los botones de siguiente, cerrar y anterior para los mensajes de paginacion
def pag_buttons():
    markup = InlineKeyboardMarkup(row_width=3)
    btn_anterior = InlineKeyboardButton("◀️ Anterior", callback_data="pag_anterior")
    btn_cerrar = InlineKeyboardButton("❌ Cerrar", callback_data="pag_cerrar")
    btn_siguiente = InlineKeyboardButton("▶️ Siguiente", callback_data="pag_siguiente")

    markup.row(btn_anterior, btn_cerrar, btn_siguiente)
    return markup

def word_no_found_buttons(message_text):
    markup = InlineKeyboardMarkup(row_width=3)
    btn_registrar = InlineKeyboardButton("➕ Registrar", callback_data="registrar")
    btn_pronunciacion = InlineKeyboardButton("🔊 Pronunciación", callback_data=f"{message_text}")
    btn_cancelar = InlineKeyboardButton("👨‍🏫 Definir", callback_data=f"def_{message_text}")

    markup.add(btn_registrar, btn_pronunciacion, btn_cancelar)
    return markup

def word_found_buttons(word):
    markup = InlineKeyboardMarkup(row_width=3)
    btn_editar = InlineKeyboardButton(f"🖊 Editar", callback_data="editar")
    btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{word}")
    btn_eliminar = InlineKeyboardButton(f"🗑 Eliminar", callback_data="eliminar")
    
    markup.add(btn_editar, btn_pronunciacion, btn_eliminar)
    return markup

def word_reminded_buttons(objWord):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{objWord.word}")
    btn_olvidar = InlineKeyboardButton(f"🧠 Olvidar", callback_data=f"forget_{objWord.id}")

    markup.add(btn_pronunciacion, btn_olvidar)
    return markup

#word_obj describe un objeto de tipo WordClass con sus caracteristicas
def edit_word_buttons(word_obj):
    markup = InlineKeyboardMarkup(row_width=4)
    btn_word = InlineKeyboardButton(
        f"{emojis.flags[word_obj.lang_word]} Palabra", callback_data="edit_word")
    
    btn_meaning = InlineKeyboardButton(
        f"{emojis.flags[word_obj.lang_meaning]} Traducciones", callback_data="edit_meaning")
    
    btn_explain = InlineKeyboardButton(
        f"{emojis.explain} Explicación", callback_data="edit_explain")
    
    btn_examples = InlineKeyboardButton(
        f"{emojis.examples} Ejemplos", callback_data="edit_examples")

    markup.add(btn_word, btn_meaning, btn_explain, btn_examples)
    return markup

def cancel_button():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

    markup.add(btn_cancelar)
    return markup

def pronunciation_button(word):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_pronunciacion = InlineKeyboardButton(f"🔊 Pronunciación", callback_data=f"{word}")

    markup.add(btn_pronunciacion)
    return markup

#funcion para agregar botones de idiomas. Type define si es para la palabra (word) o para las traducciones (meaning) o para la pronunciacion (pron)
def language_buttons(type):
    markup = InlineKeyboardMarkup(row_width=5)

    btn_ingles = InlineKeyboardButton(f"{emojis.flags['EN']}", callback_data=f"{type}_EN")
    btn_espanhol = InlineKeyboardButton(f"{emojis.flags['ES']}", callback_data=f"{type}_ES")
    btn_portugues = InlineKeyboardButton(f"{emojis.flags['BR']}", callback_data=f"{type}_BR")
    btn_frances = InlineKeyboardButton(f"{emojis.flags['FR']}", callback_data=f"{type}_FR")
    btn_italiano = InlineKeyboardButton(f"{emojis.flags['IT']}", callback_data=f"{type}_IT")

    btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

    markup.add(btn_ingles, btn_espanhol, btn_portugues,btn_frances, btn_italiano, btn_cancelar)
    return markup
    
def confirm_register_buttons():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_confirmar = InlineKeyboardButton("✅ Confirmar", callback_data="confirmar")
    btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

    markup.add(btn_confirmar, btn_cancelar)
    return markup

def forget_period_buttons(id_word):
    markup = InlineKeyboardMarkup(row_width=2)
    # El numero es la cantidad de meses
    btn_1_month = InlineKeyboardButton(f"1️⃣ Mes", callback_data="resche_1")
    btn_3_month = InlineKeyboardButton(f"3️⃣ Meses", callback_data="resche_3")
    btn_6_month = InlineKeyboardButton(f"6️⃣ Meses", callback_data="resche_6")
    btn_12_month = InlineKeyboardButton(f"1️⃣ Año", callback_data="resche_12")
    btn_for_ever = InlineKeyboardButton(f"✖️🧠 No recordar", callback_data=f"unsche_{id_word}")
    btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

    markup.add(btn_1_month, btn_3_month, btn_6_month,btn_12_month, btn_for_ever, btn_cancelar)
    return markup

def remove_keyboard(): 
    return ReplyKeyboardRemove()

def skip_button():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Omitir"))
    return markup

def register_button():
    markup = InlineKeyboardMarkup(row_width=3)
    btn_registrar = InlineKeyboardButton("➕ Registrar", callback_data="registrar")
    btn_cancelar = InlineKeyboardButton("✖ Cancelar", callback_data="cancelar")

    markup.add(btn_registrar, btn_cancelar)
    return markup