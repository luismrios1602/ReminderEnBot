from modules import database, response_message
from classes import WordClass
from utils import utils

# diccionario principal con los datos de la palabra actual de cada usuario, para que no se convinen
current_words = {}

# funcion para cancelar la transacción
def cancel_process(chatId):
    # si le da clic en cancelar, limpiamos los pasos porque hay que empezar de nuevo
    global current_words
    current_words[chatId] = WordClass()

def clear_current_word(chatId): 
    global current_words
    del current_words[chatId]

# funcion para buscar todas las palabras del usuario
def search_all_words(chatId):
    words_all = database.query_select_all(chatId)
    return  response_message.show_all(0, words_all)

def search_scheduled_words():
    return database.query_select_scheduled_words()

# funcion para buscar una sola palabra
def search_word(chatId, word):
    global current_words
    word_found = database.query_select_word(word, chatId)

    # Si es None es porque la palabra no existe entonces invitamos a la persona a registrarla
    if word_found == None:
        # Agregamos o editamos la palabra actual del usuario con su chat_id. Porque si está en el current_words, lo va a modificar y si no es como un agregar
        current_words[chatId] = WordClass()
        current_words[chatId].word = word
        return "Palabra no encontrada"

    elif word_found == "error":
        raise 'Error consultando la palabra'

    # Si no es none ni error es porque encontró la palabra entonces procedemos a mostrarla
    else:
        current_words[chatId] = word_found
        return response_message.format_word(word_found)

#función para buscar la palabra actual de un chat especifico
def select_current_word(chatId):
    global current_words
    return current_words.get(chatId, None) #Si no está retorna None

#funcion para asignarle una nueva palabra actual al usuario
def assign_current_word(chatId, word, id=None):
    global current_words
    current_words[chatId] = WordClass(word=word, id=id)

def register_id_current_word(chatId, id):
    global current_words
    current_words[chatId].id = id

#funcion para registrar el idioma de la palabra a guardar
def register_lang_current_word(chatId, lang):    
    global current_words
    current_words[chatId].lang = lang
    return

def register_meaning_current_word(chatId, meaning):
    global current_words
    current_words[chatId].meaning = meaning
    return

def register_explain_current_word(chatId, explain):
    global current_words
    current_words[chatId].description = explain
    return

def register_example_current_word(chatId, example):
    global current_words
    current_words[chatId].example = example
    return

# funcion para registrar el idioma de la las traducciones de la palabra a guardar
def register_lang_meaning_current_word(chatId, lang):
    global current_words
    current_words[chatId].lang_meaning = lang
    return

# función para buscar la palabra actual del usuario y guardarla. Se debería llamar al finalizar la carga de los datos
def create_current_word(chatId):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return (False, response_message.error_manage_word(), None)

    # Si hay una palabra actual la mandamos a guardar en la BD
    created = database.query_create_word(cur_word, chatId)
    if created == 'error':
        return (False, response_message.error_manage_word(), None)

    # Si todo se guardó bien respondemos que se guardó correctamente,retornamos el mensaje a mostrar y la palabra guardada (para la pronunciacion)
    return (True, response_message.success_create_word(cur_word), cur_word.word)
    
# funcion para editar la propiedad word de la palabra actual del usuario
def update_word_current_word(chatId, new_word):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return response_message.error_manage_word()
    
    #Si hay una palabra actual entonces cambiamos su word y mandamos a actualizar toda la palabra
    cur_word.word = new_word
    updated = update_word(cur_word)

    if updated == 'success':
        return search_word(cur_word.word)
    else: 
        return None

 #funcion para editar la propiedad meaning de la palabra actual del usuario
def update_meaning_current_word(chatId, new_meaning):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return response_message.error_manage_word()

    # Si hay una palabra actual entonces cambiamos su word y mandamos a actualizar toda la palabra
    cur_word.meaning = new_meaning
    updated = update_word(cur_word)

    if updated == 'success':
        return search_word(cur_word.word)
    else:
        return None

# funcion para editar la propiedad explain de la palabra actual del usuario
def update_explain_current_word(chatId, new_explain):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return response_message.error_manage_word()

    # Si hay una palabra actual entonces cambiamos su word y mandamos a actualizar toda la palabra
    cur_word.description = new_explain
    updated = update_word(cur_word)

    if updated == 'success':
        return search_word(cur_word.word)
    else:
        return None
    
# funcion para editar la propiedad examples de la palabra actual del usuario
def update_examples_current_word(chatId, new_examples):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return response_message.error_manage_word()

    # Si hay una palabra actual entonces cambiamos su word y mandamos a actualizar toda la palabra
    cur_word.examples = new_examples
    updated = update_word(cur_word)

    if updated == 'success':
        return search_word(cur_word.word)
    else:
        return None
    
# funcion para editar toda la palabra
def update_word(word):
    updated = database.query_update_word(word)
    # Reprogramamos la palabra
    updated = database.query_reschedule_word(word)
    return updated

#funcion para eliminar una palabra de la base de datos. Retorna una tupla con el resultado exitoso (True | False) y el mensaje
def delete_word(chatId):
    global current_words
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return response_message.no_current_word()
    
    deleted = database.query_delete_word(cur_word.id)
    if deleted == 'success':
        del current_words[chatId]
        return (True, response_message.success_delete_word(cur_word.word))
    else: 
        return (False, response_message.error_manage_word())
    
def reschedule_word(objWord):
    return database.query_reschedule_word(objWord)

# funcion para reprogramar una palabra según los días especificados
def forget_word(chatId, months):
    # Debemos verificar primero si hay una palabra actual seleccionada
    cur_word = select_current_word(chatId) #Deberia traer el id al clicar asignado en el boton de forget
    if cur_word is None:
        return response_message.no_current_word()
    
    #Sabiendo que hay una palabra, buscamos la palabra completa por id
    cur_word = database.query_select_word_by_id(cur_word.id, chatId)
    if cur_word is None:
        return response_message.no_word_by_id()
    
    # Si la palabra existe, convertimos la cantidad de meses a días
    last_daysSchedule = cur_word.daysSchedule
    cur_word.daysSchedule = int(months) * 30
    resp = database.query_reschedule_word(cur_word)

    if resp == 'success':
        return response_message.success_reschedule_word(cur_word.word, last_daysSchedule. cur_word.daysSchedule)
    else:
        return response_message.error_reschedule_word()

