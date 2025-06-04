from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT, HORA_MORNING, HORA_NIGHT
from classes.WordClass import WordClass
from classes.UserClass import UserClass

import mysql.connector
import random
import datetime

from modules.response_message import user_found


def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        port=MYSQL_PORT,
        database=MYSQL_DATABASE)

#funcion para crear el audio en la bd
def query_create_word(objWord, chatId):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else: 
        try:
            print('Conectado a la BD')
            
            # Generar fecha y hora aleatorias
            fecha_aleatoria = generar_fecha_aleatoria(7) #Mandamos 7 días por defecto
            hora_aleatoria = generar_hora_aleatoria()
            # Combinar fecha y hora en un objeto datetime
            fecha_hora_aleatoria = datetime.datetime.combine(fecha_aleatoria.date(), hora_aleatoria.time())

            cursor = conexion.cursor()
            sql = f"INSERT INTO words(word, lang_word, meaning, lang_meaning, description, examples, chat_id, scheduled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            print(f'Guardando palabra {objWord.word}...')
            
            parametros = (objWord.word, objWord.lang_word, objWord.meaning, objWord.lang_meaning, objWord.description, objWord.examples, chatId, fecha_hora_aleatoria)
            cursor.execute(sql, parametros)
            conexion.commit()
            
        except Exception as err:
            print(err)
            return "error"

        finally:
            if conexion.is_connected():
                conexion.close()

        return "success"

def query_create_user(objUser):
    try:
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')

            # Generar fecha y hora aleatorias
            fecha_aleatoria = generar_fecha_aleatoria(7)  # Mandamos 7 días por defecto
            hora_aleatoria = generar_hora_aleatoria()
            # Combinar fecha y hora en un objeto datetime
            fecha_hora_aleatoria = datetime.datetime.combine(fecha_aleatoria.date(), hora_aleatoria.time())

            cursor = conexion.cursor()
            sql = f"INSERT INTO users(chat_id, name, lang) VALUES (%s, %s, %s)"
            print(f'Guardando usuario {objUser.chatId}, {objUser.name}...')

            parametros = (objUser.chatId, objUser.name, objUser.lang)
            cursor.execute(sql, parametros)
            conexion.commit()

        except Exception as err:
            print(err)
            return "error"

        finally:
            if conexion.is_connected():
                conexion.close()

        return "success"

#función para consultar las palabras programadas para ahora 
def query_select_scheduled_words():
    try:
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return []
    else:
        try:
            print('Conectado a la BD')
            # Obtener la fecha y hora actuales en formato AAAA-MM-DD HH:MM
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            print('consultando palabras para ahora...')

            # Construir y ejecutar la consulta SQL
            query = f'''SELECT id, word, lang_word, meaning, lang_meaning, description, examples, chat_id, days_schedule FROM words 
            WHERE DATE_FORMAT(scheduled, '%Y-%m-%d %H:%i') = '{fecha_hora_actual}' AND remind = true'''

            lista = []
            
            cursor = conexion.cursor()
            cursor.execute(query)

            #Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            for word_found in cursor:
                word = WordClass(*word_found)
                print(word)
                lista.append(word)

            conexion.close()
            return lista

        except Exception as err:
            print('Error consultando palabras')
            print(err)
            return []
    finally:
        if conexion.is_connected():
            conexion.close()

#funcion para consultar una sola palabra
def query_select_word(word, chatId):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')
            # Obtener la fecha y hora actuales en formato AAAA-MM-DD HH:MM
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            print(f'Palabra {word}...')

            # Construir y ejecutar la consulta SQL
            query = f"SELECT id, word, lang_word, meaning, lang_meaning, description, examples, chat_id, days_schedule FROM words WHERE word = %s AND chat_id = {chatId}"
            
            parametros = list([word])
            cursor = conexion.cursor()
            cursor.execute(query, parametros)

            #Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            lista = cursor.fetchall()
            print(f'Palabras encontradas: {len(lista)}')
            if len(lista) > 0:
                #Si sí hay datos, nos traemos el primero, como es una lista de tuplas toca el 0-0
                word_found = WordClass(lista[0][0], lista[0][1], lista[0][2], lista[0][3], lista[0][4], lista[0][5], lista[0][6], lista[0][7], lista[0][8])
                print(word_found)
                return word_found
            else:
                return None

        except Exception as err:
            print('Error consultando palabras')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()


def query_select_user(chatId):
    try:
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')

            # Construir y ejecutar la consulta SQL
            query = f"SELECT id, chat_id, name, lang FROM users WHERE chat_id = %s"

            parametros = (chatId,)
            cursor = conexion.cursor()
            cursor.execute(query, parametros)

            # Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            lista = cursor.fetchall()
            print(f'Usuarios encontrados: {len(lista)}')
            if len(lista) > 0:
                # Si sí hay datos, nos traemos el primero, como es una lista de tuplas
                u_id, u_chat_id, u_name, u_lang = lista[0]
                user_found = UserClass(u_id, u_chat_id, u_name, u_lang)

                #user_found = UserClass(lista[0][0], lista[0][1], lista[0][2], lista[0][3])
                print(user_found)
                return user_found
            else:
                return None

        except Exception as err:
            print('Error consultando usuarios')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()

#funcion para consultar una sola palabra
def query_select_word_by_id(idWord, chatId):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')
            # Obtener la fecha y hora actuales en formato AAAA-MM-DD HH:MM
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            # Construir y ejecutar la consulta SQL
            query = f"SELECT id, word, lang_word, meaning, lang_meaning, description, examples, chat_id, days_schedule FROM words WHERE id = %s AND chat_id = {chatId}"
            
            parametros = list([idWord])
            cursor = conexion.cursor()
            cursor.execute(query, parametros)

            #Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            lista = cursor.fetchall()
            print(f'Palabras encontradas: {len(lista)}')
            if len(lista) > 0:
                #Si sí hay datos, nos traemos el primero, como es una lista de tuplas toca el 0-0
                word_found = WordClass(lista[0][0], lista[0][1], lista[0][2], lista[0][3], lista[0][4], lista[0][5], lista[0][6], lista[0][7], lista[0][8])
                print(word_found)
                return word_found
            else:
                return None

        except Exception as err:
            print('Error consultando palabras')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()

#función para consultar las palabras programadas para ahora 
def query_select_all(chatId):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return []
    else:
        try:
            print('Conectado a la BD')
            # Obtener la fecha y hora actuales en formato AAAA-MM-DD HH:MM
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            print(f'consultando todas las palabras de {chatId} ...')

            # Construir y ejecutar la consulta SQL
            query = f"SELECT id, word, lang_word, meaning, lang_meaning, description, examples, chat_id, days_schedule FROM words WHERE chat_id = {chatId} ORDER BY word"

            lista = []
            
            cursor = conexion.cursor()
            cursor.execute(query)

            #Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            for word_found in cursor:
                word = WordClass(*word_found)
                print(word)
                lista.append(word)

            conexion.close()
            return lista

        except Exception as err:
            print('Error consultando palabras')
            print(err)
            return []
    finally:
        if conexion.is_connected():
            conexion.close()

#funcion para consultar todas las palabras vencidas a renovar
def query_search_expired_words():
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return []
    else:
        try:
            print('Conectado a la BD')
            # Obtener la fecha y hora actuales en formato AAAA-MM-DD HH:MM
            fecha_hora_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

            print(f'consultando todas las palabras vencidas ...')

            # Construir y ejecutar la consulta SQL
            query = f"SELECT id, days_schedule FROM words WHERE scheduled < NOW() ORDER BY id"

            lista = []
            
            cursor = conexion.cursor()
            cursor.execute(query)

            #Cada registro viene como una tupla, entonces basados en la tupla creamos un objeto tipo word
            for word_found in cursor:
                word = WordClass(id=word_found[0], daysSchedule=word_found[1])
                print(word)
                lista.append(word)

            conexion.close()
            return lista

        except Exception as err:
            print('Error consultando palabras')
            print(err)
            return []
    finally:
        if conexion.is_connected():
            conexion.close()

#funcion para reprogramar una palabra que haya sido encontrada en la consulta de vencidas o mostrada el día de hoy
def query_reschedule_word(objWord):
    print(objWord)
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')
            # Generar fecha y hora aleatorias
            fecha_aleatoria = generar_fecha_aleatoria(objWord.daysSchedule)
            hora_aleatoria = generar_hora_aleatoria()
            # Combinar fecha y hora en un objeto datetime
            fecha_hora_aleatoria = datetime.datetime.combine(fecha_aleatoria.date(), hora_aleatoria.time())
            
            print(f'Reprogramando palabra {objWord.id} - fecha: {fecha_hora_aleatoria}... ')

            cursor = conexion.cursor()
            sql = f"UPDATE words SET scheduled = %s, days_schedule = %s WHERE id = %s"
            
            parametros = (fecha_hora_aleatoria, objWord.daysSchedule, objWord.id)
            cursor.execute(sql, parametros)
            conexion.commit()

            return "success"

        except Exception as err:
            print('Error actualizando palabras')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()

#funcion para editar una palabra especifica
def query_update_word(objWord):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            
            cursor = conexion.cursor()
            sql = f"UPDATE words SET word = %s, meaning = %s, description = %s, examples = %s, remind = true WHERE id = {objWord.id}"
            
            parametros = (objWord.word, objWord.meaning, objWord.description, objWord.examples)
            cursor.execute(sql, parametros)
            conexion.commit()

            return "success"

        except Exception as err:
            print('Error actualizando palabras')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()

def query_delete_word(word_id):
    try: 
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            
            cursor = conexion.cursor()
            sql = f"DELETE FROM words WHERE id = {word_id}"
            
            cursor.execute(sql)
            conexion.commit()

            return "success"

        except Exception as err:
            print('Error actualizando palabras')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()


# funcion para olvidar una palabra
def query_unschedule_word(word_id):
    try:
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            cursor = conexion.cursor()
            sql = f"UPDATE words SET remind = false WHERE id = {word_id}"

            cursor.execute(sql)
            conexion.commit()

            return "success"

        except Exception as err:
            print('Error actualizando palabras')
            print(err)
            return str(err)
    finally:
        if conexion.is_connected():
            conexion.close()


# funcion para reasingarle un idioma a un usuario
def query_update_lang_user(chatId, new_lang):
    try:
        conexion = connect()
    except Exception as err:
        print('Error creando la conexión')
        print(err)
        return "error"
    else:
        try:
            print('Conectado a la BD')
            print(f'Actualizando idioma del usuario {chatId}...')

            cursor = conexion.cursor()
            sql = f"UPDATE users SET lang = %s WHERE chat_id = %s"

            parametros = (new_lang, chatId)
            cursor.execute(sql, parametros)
            conexion.commit()

            return "success"

        except Exception as err:
            print('Error actualizando usuario')
            print(err)
            return "error"
    finally:
        if conexion.is_connected():
            conexion.close()

# Función para generar una fecha aleatoria entre 1 y los días días enviados (7 por defecto) después de la fecha actual
def generar_fecha_aleatoria(dias):
    dias_aleatorios = random.randint(1, dias) + 1 #Le ponemos +1 porque a veces está cayendo en el mismo día de hoy entonces siempre se respetará esos 7 días
    fecha_actual = datetime.datetime.now()
    fecha_aleatoria = fecha_actual + datetime.timedelta(days=dias_aleatorios)
    return fecha_aleatoria

# Función para generar una hora aleatoria entre las 8:00 y las 22:00, pero le ponemos 5 horas para que esté con el horario del UTC-5
def generar_hora_aleatoria():
    hora_aleatoria = datetime.datetime.strptime(f"{HORA_MORNING}:00", "%H:%M")
    minutos_aleatorios = random.randint(0, 840)  # 840 minutos = 14 horas
    hora_aleatoria += datetime.timedelta(minutes=minutos_aleatorios)
    return hora_aleatoria
