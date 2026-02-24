import json

import requests

from classes.ConfigClass import ConfigClass

languages = {
    "ES": "Español",
    "EN": "Inglés",
    "BR": "Portugués Brasileño",
    "FR": "Francés",
    "IT": "Italiano"
}


def get_ia_def(word, lang_bot='ES', lang='EN'):
    custom_instruction = f'''Respondeme siempre en {languages[lang_bot]} y define esa palabra en el idioma {languages[lang]}. 
Limita tu respuesta a un mensaje de Telegram, no seas denso, sé conciso y corto en la respuesta. Solo usa las negritas para los títulos.
Lo que esté entre comillas usa cursiva.
Quiero que respondas con la siguiente estructura:
Explicación: de la palabra o frase teniendo en cuenta todos los contextos en los que se usa. No seas denso, explica por encima cada uso. Deja los ejemplos solo para la fase final.
Traducción: de la palabra {word} al {languages[lang_bot]}, no de la explicación.
> Algunas frases de ejemplos en {languages[lang]} con esa palabra o frase. Estos ejemplos deben ser de citas reales (Busca en internet y dame la fuente); como citas de libros, mensajes de foros, notas de periódicos, etc.
No me listes las fuentes consultadas al final.'''

    url = ConfigClass.IA_URL
    headers = {
        "X-goog-api-key": f"{ConfigClass.IA_APIKEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "system_instruction": {
            "parts": [
                {"text": f"{custom_instruction}"}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{word}"}
                ]
            }
        ],
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 2048
        }
    }

    response = requests.post(url=url, headers=headers, data=json.dumps(payload))
    print(response.text)
    if response.status_code != 200:
        return 'Error generando la definición'

    answer = response.json()
    content = answer['candidates'][0]['content']['parts'][0]['text']

    return content
