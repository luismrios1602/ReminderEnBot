from classes.ConfigClass import ConfigClass
from AI import perplexity, google

model = ConfigClass.IA_MODEL

def get_ia_def(word, lang_bot='ES', lang='EN'):
    global model

    try:
        match model:
            case 'Perplexity':
                return perplexity.get_ia_def(word=word, lang_bot=lang_bot, lang=lang)
            case 'Google':
                return google.get_ia_def(word=word, lang_bot=lang_bot, lang=lang)
        return 'Ningún modelo configurado'
    except Exception as ex:
        print(ex)
        return 'Ha ocurrido un error al intentar definir la palabra. Intente más tarde.'

