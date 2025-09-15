import requests
import json
import re
from classes.ConfigClass import ConfigClass

languages = {
    "ES": "Español",
    "EN": "Inglés",
    "BR": "Portugués Brasileño",
    "FR": "Francés",
    "IT": "Italiano"
}

def get_ia_def(word, lang_bot='ES', lang='EN'):

    custom_instruction = f'''Respondeme siempre en {languages[lang_bot]} y define de esa palabra en el idioma {languages[lang]}.
Quiero que respondas con la siguiente estructura:
> Explicación de la palabra o frase teniendo en cuenta todos los contextos en los que se usa. 
> Traducción al {languages[lang_bot]} de la palabra que te pregunté, no de la explicación.
> Algunas frases de ejemplos en {languages[lang]} con esa palabra o frase. Estos ejemplos deben ser de citas reales (Busca en internet y dame la fuente); como citas de libros, mensajes de foros, notas de periódicos, etc.
No me listes las fuentes consultadas al final.'''

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {ConfigClass.IA_APIKEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": custom_instruction
            },
            {
                "role": "user",
                "content": word
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    answer = response.json()
    content = answer['choices'][0]['message']['content']

    #Para evitar que aparezcan las referencias ([1], [2], etc) eliminamos lo que venga así
    content = drop_references(content)

    return content

def drop_references(content):
    #Usamos el modulo de expresiones regulares para eliminar cualquier cosa que tenga [numero]
    return re.sub(r'(\[\d+\])+', '', content)