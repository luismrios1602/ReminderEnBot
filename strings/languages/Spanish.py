from strings import emojis


class Spanish:
    def __init__(self):
        self.test = f"{emojis.flags["ES"]} probando"
        self.dias = "días"
        self.bienvenida = '''Bienvenido, {username}👋! Soy RemindEn, tu recordatorio de palabras ✌
Envía /help para conocer cómo funciono.'''
        self.ayuda = ('🤖 _¿Qué puedo hacer?:_\n\n'
               '🔍 *Buscar:* Envíame una palabra, si la palabra está registrada la mostraré\\. \n\n'
               '➕ *Registrar:* Si la palabra ingresada no existe, tendrás la opción de registrarla\\. \n'
               '   Explicación, Ejemplos, Traducción y Frecuencia de recordatorio \n\n'
               '*🔊 Pronunciación:* Cuando envías una palabra tienes la opción de escuchar su pronunciación antes de registrarla\\. \n\n'
               '*📅 Recordatorio:* Cada palabra registrada será recordada en un lapso de 7 días\\. El contador de los 7 días se reinicia cada vez que la palabra es recordada\\. \n'
               'El día y hora serán al azar entre las 8:00 UTC\\-5 y las 22:00 UTC\\-5 \n\n'
               '*🧠 Olvidar:* Cuando quieras dejar de recordar una palabra puedes seleccionar la opción de olvidar y seleccionar el tiempo por el que quieres olvidarla\\. \n'
               '1 mes, 3 meses, 6 meses, 1 año, no recordar más\\.\n\n'
               '*🗑 Eliminar:* Busca la palabra a eliminar y haz clic en Eliminar\\.\n\n'
               '*🖊 Editar:* Busca la palabra a editar y haz clic en Editar\\. Posteriormente, seleccione qué quiere editar y siga las instrucciones\\. \n\n'
               '*🧹 Limpiar:* Si limpias este chat, no se eliminarán las palabras registradas anteriormente, y seguirás recibiendo tus recordatorios\\.\n\n'
               '*🛑 Detener recordatorios:* Usa la opción de Stop Bot de Telegram para dejar de recibir mensajes automáticos\\.\n\n')

    def __getitem__(self, key):
        return getattr(self, key, f"sin texto")
