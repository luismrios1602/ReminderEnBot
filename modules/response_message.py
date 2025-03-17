from strings import emojis
from utils import utils

num_row = 5

# funcion para mapear la respuesta del mostrartodos
def show_all(cur_page=0, listWords=[]):
    global num_row

    response = ''
    i = cur_page

    inicio = cur_page
    fin = len(listWords) if cur_page + num_row > len(listWords) else cur_page + num_row

    for word in listWords[inicio:fin]:
        i += 1
        response += f'[{i}]\n{emojis.flags[word.lang_word]} *{word.word}*\n{emojis.flags[word.lang_meaning]} {word.meaning}\n\n'

    header_resp = f'_Resultado *{cur_page +1}* al *{i}* de *{len(listWords)}*_\n'
    return header_resp + response

# funcion para formatear una palabra y mostrarla siempre de la misma forma
def format_word(word):
    #iniciamos las partes del texto que se van a mostrar 
    parts = [
        f"{emojis.flags[word.lang_word]} *{word.word}*" #primero solo la palabra
    ]

    #si hay una descripción, la unimos al array
    if word.description:
        parts.append(f"{emojis.explain} {word.description}")

    #si hay ejemplos, la unimos al array
    if word.examples:
        parts.append(f"{emojis.examples} _{word.examples}_")

    #al final juntamos las partes que faltan con un extend 
    parts.extend([
        f"{emojis.flags[word.lang_meaning]} ||{word.meaning}||",
        f"{emojis.date} {word.daysSchedule} días"
    ])

    #con el join, ahora los 2 saltos de linea funcionan como delimitadores para cada parte, y si no hay description o examples, no se ven esos saltos
    return "\n\n".join(parts)

def no_current_word():
    mensaje = '🤔 No hay una palabra actual, consultela nuevamente'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def no_word_by_id():
    mensaje = '🤔 No se ha encontrado la palabra con id seleccionado'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def word_no_found(word):
    mensaje = f'🔎 Palabra *{word}* no encontrada'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def question_language_register():
    mensaje = f"🌎 ¿En qué idioma está esta palabra? "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def question_forget_period(word):
    mensaje = f" 🧠 Olvidar *{word}*\n¿Por cuánto tiempo deseas que se reprograme la palabra?\n"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_meaning_register():
    mensaje = f"🌎 Ingrese su(s) traducción(es): "
    # mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_lang_meaning_register():
    mensaje = f"🌎 ¿En qué idioma están las traducciones?"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_explain_register():
    mensaje = f"{emojis.explain} Ingresa una breve explicación: "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_examples_register():
    mensaje = f"{emojis.examples} Ingresa ejemplos de frases con esta palabra: "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def question_edit(word): 
    mensaje = f"*{word}*\n¿Qué deseas editar?\n"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_word_edited(lang_word):
    mensaje = f"{emojis.flags[lang_word]} Ingrese la palabra corregida:"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_meaning_edited(lang_meaning):
    mensaje = f"{emojis.flags[lang_meaning]} Ingrese la(s) traduccion(es) corregida(s):"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_explain_edited():
    mensaje = f"{emojis.explain} Ingrese la explicación corregida: "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_examples_edited():
    mensaje = f"{emojis.examples} Ingrese los ejemplos corregidos: "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def ask_lang_listening(word):
    mensaje = f"""*{word}*
    🗣️ ¿En qué idioma quieres escuchar?"""
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def error_manage_word():
    mensaje = f'😪 Ups! Error al gestionar la palabra.'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def error_reschedule_word():
    mensaje = f"😪 Ups! Hubo un error al reprogramar la palabra.\n Consulte la palabra e intente olvidarla nuevamente. "
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def general_error(cause):
    mensaje = f"😪 Ups! Se ha presentado un error\n\nCausa:`{str(cause)}`"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def error_months():
    mensaje = '🤔 La cantidad escogida no es un número'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def error_forget_word():
    mensaje = f'😪 Ups! Error al olvidar la palabra'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def error_playing_word(cause):
    mensaje = f"😪 Ups! Error al reproducir la palabra\n\n Causa:`{str(cause)}`"
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def success_create_word(word):
    mensaje = f'''✅ Palabra guardada exitosamente
{format_word(word)}'''
    return mensaje

def success_update_word(objWord):
    mensaje = f'''🔃 Palabra actualizada exitosamente
{format_word(objWord)}'''
    return mensaje

def success_delete_word(word):
    mensaje = f"🗑 Palabra *{word}* eliminada."
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def success_reschedule_word(word, last_daysSchedule, new_daysSchedule):
    mensaje = f'🧠✅ Palabra *{word}* reprogramada exitosamente\\.\n_Recuerde que ahora la aleatoriedad en la que se reprograma esta palabra pasa de {last_daysSchedule} a {new_daysSchedule} días\\._ '
    return mensaje

def success_forget_word(word):
    mensaje = f'✅🧠 Palabra *{word}* olvidada exitosamente. Para activarla nuevamente puede buscarla y editarla'
    mensaje = utils.escapar_caracteres_especiales(mensaje)
    return mensaje

def skiped():
    mensaje = 'Omitido'
    return mensaje

def next_step():
    return 'Siguiente'