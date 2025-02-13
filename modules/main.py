from modules import database, response_message
from classes.WordClass import WordClass
from gtts import gTTS

from utils import utils

# diccionario principal con los datos de la palabra actual de cada usuario, para que no se convinen
current_words = {}

def clear_current_word(chatId): 
    global current_words
    try:
        del current_words[chatId]
    except Exception as err:
        print(f'El usuario {chatId} no tiene palabra actual por limpiar')

# funcion para buscar todas las palabras del usuario
def search_all_words(chatId):
    words_all = database.query_select_all(chatId)
    return  (words_all, response_message.show_all(0, words_all))

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
        return (None, response_message.word_no_found(word))

    elif word_found == "error":
        raise 'Error consultando la palabra'

    # Si no es none ni error es porque encontró la palabra entonces procedemos a mostrarla
    else:
        current_words[chatId] = word_found
        return (word_found, response_message.format_word(word_found))
    
def search_word_by_id(chatId, id_word):
    global current_words
    word_found = database.query_select_word_by_id(id_word, chatId)

    if word_found == 'error': 
        return (None, response_message.general_error('No especificado'))
    
    if word_found is None: 
        return (None, response_message.word_no_found)
    
    #Si encontramos la palabra la colocamos como actual y la retonamos
    current_words[chatId] = word_found
    return (word_found, 'Palabra Encontrada')

#función para buscar la palabra actual de un chat especifico
def select_current_word(chatId):
    global current_words
    return current_words.get(chatId, None) #Si no está retorna None

#funcion para asignarle una nueva palabra actual al usuario
def assign_current_word(chatId, word='', id=None):
    global current_words
    current_words[chatId] = WordClass(word=word, id=id)
    return current_words.get(chatId, None)

#funcion para registrar el idioma de la palabra a guardar
def register_lang_current_word(chatId, lang):    
    global current_words
    current_words[chatId].lang_word = lang
    return

def register_meaning_current_word(chatId, meaning):
    global current_words
    current_words[chatId].meaning = utils.escapar_caracteres_especiales(meaning)
    return

# funcion para registrar el idioma de la las traducciones de la palabra a guardar
def register_lang_meaning_current_word(chatId, lang):
    global current_words
    current_words[chatId].lang_meaning = lang
    return

def register_explain_current_word(chatId, explain):
    global current_words
    current_words[chatId].description = utils.escapar_caracteres_especiales(explain)
    return

def register_examples_current_word(chatId, examples):
    global current_words
    current_words[chatId].examples = utils.escapar_caracteres_especiales(examples)
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
    
# funcion para editar la propiedad (atr) de la palabra actual del usuario.
def update_current_word(chatId, atr, new_value):
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return (None, response_message.no_current_word())
    
    #Si hay una palabra actual entonces cambiamos su word y mandamos a actualizar toda la palabra
    setattr(cur_word, atr, new_value)
    updated = update_word(cur_word)

    if updated == 'success':
        return (cur_word, 'Palabra actualizada exitosamente.')
    else: 
        return (None, response_message.error_manage_word())
    
# funcion para editar toda la palabra
def update_word(objWord):
    updated = database.query_update_word(objWord)
    # Reprogramamos la palabra
    updated = database.query_reschedule_word(objWord)
    return updated

#funcion para eliminar una palabra de la base de datos. Retorna una tupla con el resultado exitoso (True | False) y el mensaje
def delete_current_word(chatId):
    global current_words
    cur_word = select_current_word(chatId)
    if cur_word is None:
        return (False, response_message.no_current_word())
    
    deleted = database.query_delete_word(cur_word.id)
    if deleted == 'success':
        del current_words[chatId]
        return (True, response_message.success_delete_word(cur_word.word))
    else: 
        return (False, response_message.error_manage_word())
    
def reschedule_word(objWord):
    return database.query_reschedule_word(objWord)

# funcion para reprogramar una palabra según los días especificados
def reschedule_current_word(chatId, months):
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
        return response_message.success_reschedule_word(cur_word.word, last_daysSchedule, cur_word.daysSchedule)
    else:
        return response_message.error_reschedule_word()

# funcion para olvidar una palabra para no volverla a enviar
def forget_word_by_id(chatId, id_word):
    # Primero buscamos la palabra para ver si existe ese id
    word_found = database.query_select_word_by_id(id_word, chatId)

    if word_found == 'error':
        return response_message.error_forget_word()

    # Si no hubo error revisamos si existe la palabra
    if word_found == None:
        return response_message.no_word_by_id()

    # Si encontramos la palabra, la olvidamos
    unscheduled = database.query_unschedule_word(id_word)

    if unscheduled == 'success':
        return response_message.success_forget_word(word_found.word)
    else:
        return response_message.error_forget_word()
    
# funcion para reprogramar palabras que no pudieron ser enviadas
def reschedule_words_earlier():
    # Primero consultamos las palabras vencidas de todos los usuarios
    words_found = database.query_search_expired_words()
    for word in words_found:
        resp = database.query_reschedule_word(word)
        print(resp)

# funcion para enviar pronunciacion 
def get_pronunciation(word, lang):
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
        return (f'{word}.mp3', 'Audio creado exitosamente')
        
    except Exception as err:
        return (None, response_message.error_playing_word(err))
